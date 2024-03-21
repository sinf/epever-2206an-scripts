import socket
import struct
import base64
import json
import time
import sys
import os
from pymodbus.client import ModbusTcpClient
from pymodbus.bit_read_message import ReadDiscreteInputsResponse, ReadCoilsResponse

from threading import Thread, Lock
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus
from urllib.parse import parse_qsl

reg_ids_subset = ["i1", "i12", "e20", "e110", "e111", "b1", "b2", "b3", "b5", "b7", "b13", "b14", "b15", "b17", "b18", "b27", "b28", "b30", "c1", "c2", "c7", "d0", "d1", "d2", "d3", "d4", "d6", "d8", "d10", "d12", "d14", "d16", "d18", "d26", "d27"]

def debug_print(*args, **kwargs):
    pass

def read_config():
    with open('epever-modbus-client-config.json', 'r') as f:
        global the_config
        the_config = json.load(f)

def config(path, default=None):
    x=the_config
    for item in path.split('.'):
        x=x.get(item)
        if x is None:
            return default
    return x

def tzcnt(x):
    return len(bin(x)) - len(bin(x).rstrip('0'))

def parse_status_bits(status_bits, value):
    status={}
    for mask_s, flags_info in status_bits.items():
        mask = parse_address(mask_s)
        state = (value & mask) >> tzcnt(mask)
        status[mask_s] = f'[0x{state:x}]'
        for flag_state, flag_msg in flags_info.items():
            if state == parse_address(flag_state):
                status[mask_s] += ' '+flag_msg
                break
    return status

def parse_address(x):
    if type(x) is str:
        x=x.lower()
        if x.endswith('h'):
            return int(x.rstrip('h'), 16)
        return int(x, 10)
    return int(x)

class Register:
    def __init__(self, j):
        self.config = j
        self.type = j['type']
        self.number = j['number']
        self.id = (self.number[0] if type(self.number) is list else self.number).lower()
        self.name = j['name']
        self.address = parse_address(j['address'])
        self.description = j.get('description')
        self.hidden = j.get('hidden', False)
        self.unit = j.get('unit','')
        self.scale = j.get('scale', 1)
        self.dtype = j.get('dtype', 'short') # short, long, delay_hm, delay_smh, date_sm_hd_MY
        self.addresses = [self.address]
        if self.dtype == 'long':
            # 2 big endian 16bit pieces make up one "little endian" 32bit word :S
            self.addresses += [self.address + 1]
        elif self.dtype in ('delay_smh', 'date_sm_hd_MY'):
            self.addresses += [self.address + 1]
            self.addresses += [self.address + 2]
        self.value = 0
        self.raw = b''
        self.rawh = ''
        self.error = True
        self.last_write_t = 0
        self.lock = Lock()
        self.is_dirty = False
        self.last_push_value = {}
        self.last_push_t = {}

    def set_from_memcells(self, mem):
        with self.lock:
            t0 = mem[0].last_write_t
            if any(m.error or m.last_write_t != t0 for m in mem):
                self.error = True
                # only allow 32bit update if both 16bit parts were succesfully read at the same time
                return
            self.last_write_t = t0
            self._set_words(data=[m.value for m in mem])
            self._update_value()

    def _set_words(self, data):
        self.error = False
        self.raw = data
        self.rawh = ' '.join(f'{x:4x}' for x in self.raw)

    def is_integer_type(self):
        return self.scale==1

    def _update_value(self):
        data = self.raw
        if self.dtype == 'short':
            self.value = data[0] * self.scale
        elif self.dtype == 'long':
            self.value = struct.unpack('<i', struct.pack('<HH', data[0], data[1]))[0]
            self.value *= self.scale
        elif self.dtype == 'date_sm_hd_MY':
            sec,min,hour,day,mon,year = struct.unpack('BBBBBB', struct.pack('<HHH',*data))
            year += 2000 # Y3K problem haha
            self.value = f'{year:04d}-{mon:02d}-{day:02d}T{hour:02d}:{min:02d}:{sec:02d}'
        elif self.dtype == 'delay_smh':
            sec,min,hour = data
            self.value = f'{hour:02d}:{min:02d}:{sec:02d}'
        elif self.dtype == 'delay_hm':
            min,hour = struct.unpack('BB', struct.pack('<H', data[0]))
            self.value = f'{hour:02d}:{min:02d}'
        else:
            raise NotImplementedError('_update_value '+str(self.dtype))

    def parse_str(self, value_str):
        if type(value_str) is bytes:
            value_str = value_str.decode('ascii', errors='ignore')
        if self.dtype == 'long':
            words = struct.unpack('<HH', struct.pack('<i', int(float(value_str)/self.scale)))
        elif self.dtype == 'date_sm_hd_MY':
            if value_str == 'now':
                t = time.localtime()
            elif all(c.isdigit() for c in value_str):
                t = time.localtime(int(value_str))
            else:
                t = time.strptime(value_str, '%Y-%m-%dT%H:%M:%S')
            words = [t.tm_sec, t.tm_min, t.tm_hour, t.tm_mday, t.tm_mon, t.tm_year - 2000]
            words = struct.unpack('<HHH',struct.pack('BBBBBB', *words))
        elif self.dtype == 'delay_smh':
            t = time.strptime(value_str, '%H:%M:%S')
            words = [t.tm_sec, t.tm_min, t.tm_hour]
        elif self.dtype == 'delay_hm':
            t = time.strptime(value_str, '%H:%M')
            words = struct.unpack('<H', struct.pack('BB', t.tm_min, t.tm_hour))
        elif self.dtype == 'short':
            x = float(value_str)/self.scale
            x = max(-32768,min(32767,int(round(x))))
            words = [x]
        else:
            raise NotImplementedError('parse_str '+str(self.dtype))
        return words

    def to_dict(self):
        with self.lock:
            thing = {
                'id': self.id,
                'name': self.name,
                'value': self.value,
                'raw': self.rawh.strip(),
                'error': int(self.error),
                'ts': self.last_write_t,
            }
            if self.unit:
                thing['unit'] = self.unit
            if self.config.get('status_bits'):
                thing['status_bits'] = parse_status_bits(self.config['status_bits'], self.value)
        return thing

    def should_always_skip_logging(self):
        # chooses if the data goes to DB and MQTT
        if self.config.get('skip_db'): return True ;
        if self.config.get('write_only'): return True ;
        return False

    def collect_for_push(self, output, key, deadline=None, now=None):
        if self.should_always_skip_logging(): return ;
        value = self.rawh
        if value == '': return ;
        if self.error: return ;
        old_value = self.last_push_value.get(key)
        changed = old_value != value
        deadline_passed = False if deadline is None else (self.last_push_t.get(key,deadline) <= deadline)
        if changed or deadline_passed:
            self.last_push_value[key] = value
            self.last_push_t[key] = now
            output += [self]

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f'({self.id}) {self.name}'

def find_contiguous_ranges(numbers, max_delta):
    start = 0
    numbers = sorted(numbers)
    for i in range(1,len(numbers)):
        a = numbers[i-1]
        b = numbers[i]
        if b-a > max_delta:
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
        self.mem = {}
        self.regs = {}
        self.client = client
        self.slave = slave
        self.lock = Lock()
        self.last_update_t = 0

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

    def to_json(self, ids=None, **kwargs):
        return json.dumps(self.state_dict(ids), **kwargs)

    def collect_for_push(self, key, max_update_interval=None, ids=None):
        now=None
        deadline=None
        if max_update_interval is not None:
            now = time.time()
            deadline = now - max_update_interval
        with self.lock:
            output=[]
            for r in self.regs.values():
                if ids is None or r.id in ids:
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
                    assert r.id not in self.regs
                    self.regs[r.id] = r
                    for addr in r.addresses:
                        self.mem[addr] = MemoryCell()
        return self

    def set_all_dirty(self):
        for r in self.regs.values():
            r.is_dirty =  True

    def write(self, id, value:str):
        # regs[id] is not updated here. it will update next time when the data is read back (if write succeeds)
        if id not in self.regs:
            return True, 'invalid id: '+str(id)
        reg = self.regs[id]
        try:
            words = reg.parse_str(value)
        except ValueError as e:
            return True, str(e)
        with self.lock:
            reg.is_dirty = True
            self.set_all_dirty() # in case 1 register somehow affects others
            addr = reg.address
            debug_print('write', id, words)
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
                    value=0
                    for i,b in enumerate(thing.bits): # convert True/False bitmask to integer
                        value |= b<<i
                else:
                    value = thing.getRegister(offset)
                self.mem[addr].set(value, set_ts)
                debug_msg += [hex(value)]
            debug_print('read range:', addr_s, 'data:', ' '.join(debug_msg))

    def read_bulk(self, addresses, func):
        """
        reading via the RS485-to-TCP converter is very slow
        so here we attempt to merge multiple reads into one request
        """
        for addr_sequence in find_contiguous_ranges(addresses, max_delta=1):
            a = addr_sequence[0]
            n = addr_sequence[-1] - a + 1
            self.read_range_1(a, n, func)

    def read_single(self, addresses, func):
        for a in addresses:
            self.read_range_1(a, 1, func)

    def default_regs(self):
        return list(filter(lambda x: not x.hidden, self.regs.values()))

    def read_regs(self, ids=None, update_older_than=None):
        addr_by_type = {
            'input': [],
            'holding': [],
            'coil': [],
            'discrete': [],
        }

        if ids is None:
            regs_to_read = self.default_regs()
        else:
            if type(ids) not in (tuple,list,set) \
            or any(type(i) is not str or (i not in self.regs) for i in ids):
                raise ValueError('invalid id: ' + str(ids))
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

    def table(self):
        print()
        for r in sorted(self.regs.values(), key=lambda r: (r.type,r.id)):
            print(f'{r.id:10s} {r.name:45s} = {r.rawh:9s}  = {r.value} {r.unit}')
        print()



class RequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], s: socketserver.BaseServer):
        super().__init__(request, client_address, s)

    def oldest_good_time(self):
        return time.time() - 30

    def bad_request(self,
            code=HTTPStatus.NOT_IMPLEMENTED,
            msg="Request DENIED! This incident will be logged and reported\n"):
        # not actually logging anything lol
        self.send_response(code)
        self.end_headers()
        self.wfile.write(msg.encode())

    def do_HEAD(self):
        self.bad_request()

    def do_GET(self):
        path=self.path
        min_t = self.oldest_good_time()
        if path.startswith('/status'):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if path == '/status':
                the_device.read_regs(update_older_than=min_t)
                resp = the_device.to_json(indent=1)
            elif path == '/status2':
                the_device.read_regs(ids=reg_ids_subset, update_older_than=min_t)
                resp = the_device.to_json(ids=reg_ids_subset, indent=1)
            else:
                resp = 'nope\n'
            self.wfile.write(resp.encode())
        elif (id:=path[1:]) in the_device.regs: # /<id>
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            the_device.read_regs(ids=[id], update_older_than=min_t)
            resp = the_device.to_json(ids=[id], indent=1)
            self.wfile.write(resp.encode())
        else:
            self.bad_request()

    def do_POST(self):
        if config('http_api.can_write') != True:
            return self.bad_request()

        bodylen = int(self.headers.get('Content-Length'))
        body = self.rfile.read(bodylen)

        if self.path == '/write':
            t=self.headers.get('Content-Type')
            if t == 'application/json':
                ids_values = json.loads(body)
            elif t == 'application/x-www-form-urlencoded':
                f = lambda x: x.decode('utf-8', errors='ignore')
                ids_values = dict((f(k),f(v)) for k,v in parse_qsl(body))
            else:
                return self.bad_request(HTTPStatus.BAD_REQUEST)
        else: # /<id>
            if (id := self.path[1:]) not in the_device.regs:
                return self.bad_request(HTTPStatus.NOT_FOUND)
            ids_values = {id: body.strip()}
        resp = {}
        ok=True
        print(ids_values)
        for id, value in ids_values.items():
            is_error, msg = the_device.write(id, value)
            resp[id] = msg if is_error else 'ok'
            ok = ok and not is_error
        resp_j = json.dumps(resp, indent=4).encode()
        self.send_response(HTTPStatus.OK if ok else HTTPStatus.INTERNAL_SERVER_ERROR)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(resp_j)


class ImprovedServer(socketserver.ThreadingTCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

def start_http_server():
    ip = config('http_api.bind_ip', '127.0.0.1')
    port = int(config('http_api.port', 8000))
    def server_main():
        print(f"Starting server at {ip} {port}")
        sv = ImprovedServer((ip, port), RequestHandler)
        sv.serve_forever()
    t = Thread(target=server_main, daemon=True, name='http-server')
    t.start()
    return t

def create_device():
    host=config('modbus_client.ip','127.0.0.1')
    port=int(config('modbus_client.port',4196))
    print('Connecting modbus client to:', host, port)

    # !!!
    client = ModbusTcpClient(host=host, port=port, framer='rtu',
        timeout=3, retries=3, retry_on_empty=True)

    dev = Device(client=client, slave=1)
    dev.parse_config('mppt-device.json')
    dev.read_regs(['b5']) # try to trigger an early error if something isn't right
    return dev

def start_mqtt():
    import paho.mqtt.client as paho

    def mqtt_main():
        client = paho.Client(client_id="epever-modbus-client",
             protocol=paho.MQTTv5,
             callback_api_version=paho.CallbackAPIVersion.VERSION2)
        client.connect(config("mqtt.ip"), config("mqtt.port"))
        client.loop_start()
        while True:
            the_device.read_regs()
            if regs := the_device.collect_for_push('mqtt', config('mqtt.max_publish_interval')):
                for reg in regs:
                    if reg.config.get('skip_db'):
                        continue
                    j = json.dumps(reg.to_dict(), indent=1)
                    client.publish(config("mqtt.topic")+'/'+reg.id, payload=j, qos=0)
            time.sleep(config("mqtt.poll_delay_s",30))
    t=Thread(target=mqtt_main, daemon=True, name='mqtt-client')
    t.start()
    return t

def start_db():
    import sqlalchemy as db 

    url=config("db.url")
    print('starting db thread:', url)
    en = db.create_engine(url)
    co = en.connect()
    me = db.MetaData()
    ids = []
    tables = {}

    for reg in the_device.regs.values():
        if reg.should_always_skip_logging():
            continue
        ids += [reg.id]

        if reg.dtype in ('short', 'long'):
            x_type = db.Integer() if reg.is_integer_type() else db.Float()
        elif reg.dtype in ('delay_hm', 'delay_smh'):
            x_type = db.String(length=8)
        elif reg.dtype == 'date_sm_hd_MY':
            raise NotImplementedError('start_db '+str(reg.dtype))

        tables[reg.id] = db.Table(config('table_prefix','')+reg.id, me,
            db.Column('t', db.Float(), primary_key=True),
            db.Column('x', x_type, nullable=False))
    me.create_all(en)
    co.commit()

    def db_main():
        while True:
            if things := the_device.collect_for_push('db', ids=tables.keys()):
                for r in things:
                    co.execute(db.insert(tables[r.id]).values(t=r.last_write_t, x=r.value))
                co.commit()
            time.sleep(config("db.poll_delay_s",30))
    t=Thread(target=db_main, daemon=True, name='db-client')
    t.start()
    return t

def main_loop():
    poll_delay = config('modbus_client.poll_delay_s', -1)
    if poll_delay < 0:
        while True:
            time.sleep(10)
    else:
        while True:
            read_regs()
            time.sleep(poll_delay)

def main():

    read_config()

    global the_device
    the_device = create_device()

    th=[]
    try:
        if config('http_api.enable') == True:
            th += [sv := start_http_server()]
        if config('mqtt.enable') == True:
            th += [dev := start_mqtt()]
        if config('db.enable') == True:
            th += [dev := start_db()]

        the_device.read_regs()
        time.sleep(1)

        if all(t.is_alive() for t in th):
            main_loop()
    except KeyboardInterrupt:
        pass

    if False:
        for i,t in enumerate(th):
            print(f'waiting for thread {i}/{len(th)}')
            t.join(timeout=30)
        print('done')


main()

