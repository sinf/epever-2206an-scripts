import socket
import struct
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

reg_ids_subset = ["I1", "I12", "E20-E21-E22", "E110", "E111", "B1", "B2", "B3-B4", "B5", "B7-B8", "B13", "B14", "B15-B16", "B17", "B18", "B27", "B28", "B30", "C1", "C2", "C7", "D0", "D1", "D2", "D3", "D4-D5", "D6-D7", "D8-D9", "D10-D11", "D12-D13", "D14-D15", "D16-D17", "D18-D19", "D26", "D27-D28"]

def parse_address(x):
    if type(x) is str:
        x=x.lower()
        if x.endswith('h'):
            return int(x.rstrip('h'), 16)
        return int(x, 10)
    return int(x)

class Register:
    def __init__(self, j):
        self.type = j['type']
        self.number = j['number']
        self.id = '-'.join(self.number) if type(self.number) is list else self.number
        self.name = j['name']
        self.address = parse_address(j['address'])
        self.description = j.get('description')
        self.unit = j.get('unit','')
        self.scale = j.get('scale', 1)
        self.dtype = j.get('dtype', 'short')
        self.addresses = [self.address]
        if self.dtype == 'long':
            # 2 big endian 16bit pieces make up one "little endian" 32bit word :S
            self.addresses += [self.address + 1]
        elif self.dtype in ('delay_smh', 'date_sm_hd_MY'):
            self.addresses += [self.address + 1]
            self.addresses += [self.address + 2]
        self.value = 0
        self.raw = b''
        self.rawh = b''
        self.error = False
        self.last_write_t = 0
        self.lock = Lock()

    def set(self, mem):
        with self.lock:
            t0 = mem[0].last_write_t
            if any(m.error or m.last_write_t != t0 for m in mem):
                self.error = True
                # only allow 32bit update if both 16bit parts were succesfully read at the same time
                return
            data = [m.value for m in mem]
            self.last_write_t = t0
            self.error = False
            self.raw = data
            self.rawh = ' '.join(f'{x:4x}' for x in self.raw)
            self.value = data[0] * self.scale
            if self.dtype == 'long':
                self.value = struct.unpack('<i', struct.pack('<HH', data[0], data[1]))[0]
                self.value *= self.scale
            elif self.dtype == 'date_sm_hd_MY':
                sec,min,hour,day,mon,year = struct.unpack('BBBBBB', struct.pack('<HHH',*data))
                year += 2000 # Y3K problem haha
                self.value = f'{year:04d}-{mon:02d}-{day:02d}T{hour:02d}:{min:02d}:{sec:02d}'
            elif self.dtype == 'delay_smh':
                sec,min,hour = data
                self.value = f'{hour:02d}:{min:02d}:{sec:02d}'

    def to_dict(self):
        with self.lock:
            thing = {
                'id': self.id,
                'name': self.name,
                'unit': self.unit,
                'value': self.value,
                'error': int(self.error),
                'ts': self.last_write_t,
            }
        return thing

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

    def to_json(self, ids=None):
        if ids is None:
            regs_needed = self.regs.values()
        else:
            regs_needed = (self.regs[i] for i in ids)
        with self.lock:
            regs_d = [r.to_dict() for r in regs_needed]
        return json.dumps({
            'last_update_t': self.last_update_t,
            'regs': regs_d,
        })

    def parse_config(self, path):
        with open(path) as f:
            config = json.load(f)
            for category, regs in config['registers'].items():
                for reg in regs:
                    if reg.get('disable'):
                        continue
                    r = Register(reg)
                    self.regs[r.id] = r
                    for addr in r.addresses:
                        self.mem[addr] = MemoryCell()
        return self

    def read_range_1(self, addr_start, count, func):
        with self.lock:
            thing = func(address=addr_start, count=count, slave=self.slave)
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
            print('read range:', hex(addr_start), '-', hex(addr_start+count-1), 'data:', ' '.join(debug_msg))

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

    def read_regs(self, ids=None, update_older_than=None):
        addr_by_type = {
            'input': [],
            'holding': [],
            'coil': [],
            'discrete': [],
        }

        if ids is None:
            regs_to_read = self.regs.values()
        else:
            assert type(ids) in (tuple,list,set)
            regs_to_read = (self.regs[i] for i in ids)

        if update_older_than is not None:
            regs_to_read = filter(lambda r: r.last_write_t < update_older_than, regs_to_read)

        regs_to_read = list(regs_to_read)
        for reg in regs_to_read:
            addr_by_type[reg.type] = addr_by_type[reg.type] + reg.addresses

        self.read_bulk(addr_by_type['input'], self.client.read_input_registers)
        self.read_bulk(addr_by_type['holding'], self.client.read_holding_registers)
        self.read_single(addr_by_type['discrete'], self.client.read_discrete_inputs)
        self.read_single(addr_by_type['coil'], self.client.read_coils)

        for r in regs_to_read:
            r.set([self.mem[x] for x in r.addresses])

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

    def status_response(self):
        global the_device
        the_device.read_regs(update_older_than = self.oldest_good_time())
        return the_device.to_json()

    def status2_response(self):
        global the_device
        the_device.read_regs(ids=reg_ids_subset, update_older_than = self.oldest_good_time())
        return the_device.to_json(ids=reg_ids_subset)

    def bad_request(self):
        self.send_response(HTTPStatus.NOT_IMPLEMENTED)
        self.end_headers()
        self.wfile.write(b"Request DENIED! This incident will be logged and reported\n")
        # not actually logging anything lol

    def do_HEAD(self):
        self.bad_request()

    def do_GET(self):
        if self.path == '/status':
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(self.status_response().encode())
        elif self.path == '/status2':
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(self.status2_response().encode())
        else:
            self.bad_request()

    def do_POST(self):
        if self.path == None:
            pass
        else:
            self.bad_request()


def start_http_server():
    def server_main():
        ip = os.environ.get('SV_IP', '127.0.0.1')
        port = int(os.environ.get('SV_PORT', 8000))
        print(f"Starting server at {ip} {port}")
        sv = socketserver.ThreadingTCPServer((ip, port), RequestHandler)
        sv.serve_forever()
    t = Thread(target=server_main, daemon=True, name='http-server')
    t.start()
    return t

def create_device():
    host=os.environ.get('IP','127.0.0.1')
    port=int(os.environ.get('PORT',4196))
    print('Connecting modbus client to:', host, port)

    client = ModbusTcpClient(host=host, port=port, framer='rtu', timeout=3)
    dev = Device(client=client, slave=1)
    dev.parse_config('mppt-device.json')
    dev.read_regs(['B5'])
    return dev

def start_device_poller():
    def dev_main():
        global the_device
        while True:
            the_device.read_regs()
            time.sleep(30)
    t=Thread(target=dev_main, daemon=True, name='modbus-client')
    t.start()
    return t

def main():

    global the_device
    the_device = create_device()

    th=[]
    try:
        th += [sv := start_http_server()]
        #th += [dev := start_device_poller()]
        time.sleep(1)
        if all(t.is_alive() for t in th):
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass

    if False:
        for i,t in enumerate(th):
            print(f'waiting for thread {i}/{len(th)}')
            t.join(timeout=30)
        print('done')


main()

