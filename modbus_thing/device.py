import json
import time
import traceback
import os

from threading import Lock
from pymodbus.client import ModbusTcpClient
from pymodbus.bit_read_message import ReadDiscreteInputsResponse, ReadCoilsResponse
from .util import *
from .register import *

def find_contiguous_ranges(numbers, max_delta, singles=[]):
    start = 0
    numbers = sorted(numbers)
    for i in range(1,len(numbers)):
        a = numbers[i-1]
        b = numbers[i]
        if (b-a > max_delta) or (a in singles) or (b in singles):
            yield numbers[start:i]
            start = i
    if start <= len(numbers)-1:
        yield numbers[start:]

class MemoryCell:
    def __init__(self):
        self.set(0, 0)
    def set(self, new_value, ts):
        self.value = new_value
        self.last_write_t = ts
        self.error = False


class Device:
    def __init__(self, client, slave):
        """
        client: pymodbus.client.*Client
        slave: modbus slave number
        """
        self.mem = {} # key=address, value=MemoryCell 
        self.regs = {} # key=(register name), value=Register
        self.client = client # pymodbus.client.*Client
        self.slave = slave # modbus slave id
        self.lock = Lock()
        self.lock2 = Lock() # only used by read_regs
        self.last_update_t = 0
        self.dbtable_regs = {} # key=(table name), value=(dict: Register by name)

    def for_db_regs(self):
        for tablename, regs_by_name in self.dbtable_regs.items():
          for reg in regs_by_name.values():
            yield reg

    def read_all(self):
        for tab in self.dbtable_regs.keys():
            self.read_regs(self.names(tab))

    def state_dict(self, ids=None):
        if ids is None:
            regs_needed = self.regs.values()
        else:
            regs_needed = (self.regs[i] for i in ids)
        with self.lock:
            regs_d = [r.to_dict() for r in regs_needed]
        return {
            'last_update_t': self.last_update_t,
            'regs': regs_d,
        }

    def to_json(self, names=None, **kwargs):
        return json.dumps(self.state_dict(names), **kwargs)

    def collect_for_push(self, key, max_update_interval=None, names=None):
        """ doesn't call .read_regs, may operate on stale data """
        now=None
        deadline=None
        now = time.time()
        if max_update_interval is not None:
            deadline = now - max_update_interval
        with self.lock:
            output=[]
            for r in self.regs.values():
                if names is None or r.name in names:
                    r.collect_for_push(output, key, deadline, now)
        return output

    def parse_config(self, path):
        with open(path) as f:
            config = json.load(f)
            for category, regs in config['registers'].items():
                for reg in regs:
                    if reg.get('disable'):
                        continue
                    r = Register(reg)
                    assert r.name not in self.regs
                    self.regs[r.name] = r
                    for addr in r.addresses:
                        self.mem[addr] = MemoryCell()
                    if (r.dbtable and r.dbtable != 'none') and not r.should_always_skip_logging():
                        f = self.dbtable_regs.get(r.dbtable, {})
                        f[r.name] = r
                        self.dbtable_regs[r.dbtable] = f

        singles = []
        for r in self.regs.values():
            if r.config.get('read_alone'):
                singles += r.addresses
        self.singles = tuple(singles)

        print('tables:')
        for table_name, regs in self.dbtable_regs.items():
            print(table_name+':', ' '.join(regs))
        print()
        return self

    def set_all_dirty(self):
        for r in self.regs.values():
            r.is_dirty =  True

    def write(self, name, value:str):
        """
        This function only sends write command but doesn't update self.regs[name]
        it will update next time when the data is read back (if write succeeds)
        """
        if name not in self.regs:
            return True, 'invalid register name: '+str(name)
        reg = self.regs[name]
        try:
            words = reg.parse_str(value)
        except ValueError as e:
            return True, str(e)
        with self.lock:
            reg.is_dirty = True
            self.set_all_dirty() # in case 1 register somehow affects others
            addr = reg.address
            debug_print('write', name, words)
            if reg.type == 'holding':
                if len(words) == 1:
                    resp=self.client.write_register(addr, words[0], self.slave)
                else:
                    resp=self.client.write_registers(addr, words, self.slave)
            elif reg.type == 'coil':
                resp=self.client.write_coil(addr, bool(words[0]), self.slave)
                #if len(words) == 1:
                #else:
                # pdf only mentions function 0x05 write single coil
                #resp=self.client.write_coils(addr, [bool(w) for w in words], self.slave)
        return resp.isError(), str(resp)

    def read_range_1(self, addr_start, count, func):
        addr_s = f'{addr_start:x}-{addr_start+count-1:x}'
        with self.lock:
            try:
                thing = func(address=addr_start, count=count, slave=self.slave)
            except Exception as ex:
                for offset in range(count):
                    self.mem[ addr_start + offset ].error = True
                traceback.print_exc()
                return print('read error:', addr_s, ex)

            set_ts = time.time()
            self.last_update_t = set_ts
            debug_msg = []
            for offset in range(count):
                addr = addr_start + offset
                if thing.isError():
                    self.mem[addr].error = True
                    debug_msg += ['(err)']
                    continue
                if isinstance(thing, ReadDiscreteInputsResponse) or isinstance(thing, ReadCoilsResponse):
                    assert count==1 # spaghetti code :S
                    value=0
                    for i,b in enumerate(thing.bits): # convert True/False bitmask to integer
                        value |= b<<i
                else:
                    try:
                        value = thing.getRegister(offset)
                    except IndexError as ex:
                        traceback.print_exc()
                        debug_msg += ['(IndexError)']
                        continue
                self.mem[addr].set(value, set_ts)
                debug_msg += [hex(value)]
            debug_print('read range:', addr_s, 'data:', ' '.join(debug_msg))

    def read_bulk(self, addresses, func):
        """
        reading via the RS485-to-TCP converter is very slow
        so here we attempt to merge multiple reads into one request
        """
        for addr_sequence in find_contiguous_ranges(addresses, max_delta=1, singles=self.singles):
            a = addr_sequence[0]
            n = addr_sequence[-1] - a + 1
            self.read_range_1(a, n, func)

    def read_single(self, addresses, func):
        for a in addresses:
            self.read_range_1(a, 1, func)

    def names(self, dbtable):
        return list(self.dbtable_regs[dbtable].keys())

    def read_regs(self, ids, update_older_than=None):
        with self.lock2:
            t0=time.time()
            assert update_older_than is None or update_older_than > 100000
            addr_by_type = {
                'input': [],
                'holding': [],
                'coil': [],
                'discrete': [],
            }

            if type(ids) not in (tuple,list,set) \
            or any(type(i) is not str or (i not in self.regs) for i in ids):
                raise ValueError('invalid ids: ' + str(ids))

            debug_print('read regs', ids)
            regs_to_read = (self.regs[i] for i in ids)

            if update_older_than is not None:
                regs_to_read = filter(lambda r: r.is_dirty or r.last_write_t < update_older_than, regs_to_read)

            regs_to_read = list(regs_to_read)
            for reg in regs_to_read:
                addr_by_type[reg.type] = addr_by_type[reg.type] + reg.addresses

            self.read_bulk(addr_by_type['input'], self.client.read_input_registers)
            self.read_bulk(addr_by_type['holding'], self.client.read_holding_registers)
            self.read_single(addr_by_type['discrete'], self.client.read_discrete_inputs)
            self.read_single(addr_by_type['coil'], self.client.read_coils)

            for r in regs_to_read:
                r.set_from_memcells([self.mem[x] for x in r.addresses])
            t1=time.time()
            debug_print(f'reading registers took {t1-t0:.6f} s')

    def table(self):
        print()
        for r in sorted(self.regs.values(), key=lambda r: (r.type,r.name)):
            print(f'{r.name:45s} = {r.rawh:9s}  = {r.value} {r.unit}')
        print()

    def sync_rtc(self, timestamp):
        date = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(timestamp))
        is_error, msg = self.write('real_time_clock', date)
        debug_print('set rtc to', date)
        if is_error:
            print('failed to write RTC register:', msg, file=sys.stderr)
            return False
        return True


def create_device():

    if config('modbus_client.fake') or os.environ.get('FAKE'):
      from .fake_client import FakeClient
      client = FakeClient()
      print('Using FakeClient')
    else:
      host=config('modbus_client.ip','127.0.0.1')
      port=int(config('modbus_client.port',4196))
      print('Connecting modbus client to:', host, port)
      # todo, start other modbus clients
      client = ModbusTcpClient(host=host, port=port, framer='rtu',
          timeout=10, retries=3, retry_on_empty=True, auto_close=True, auto_open=True)

    dev = Device(client=client, slave=1)
    dev.parse_config('config/mppt-device.json')
    dev.read_regs(['batt_rtvoltage']) # try to trigger an early error if something isn't right
    return dev

