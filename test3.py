import socket
import struct
import json
import sys
import os
from pymodbus.client import ModbusTcpClient
from pymodbus.bit_read_message import ReadDiscreteInputsResponse, ReadCoilsResponse


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

    def set(self, data):
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

class Device:
    def __init__(self, client, slave):
        self.mem = {}
        self.regs = {}
        self.client = client
        self.slave = slave

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
                        self.mem[addr] = 0
        return self

    def read_range_1(self, addr_start, count, func):
        thing = func(address=addr_start, count=count, slave=self.slave)
        debug_msg = []
        for offset in range(count):
            addr = addr_start + offset
            if thing.isError():
                debug_msg += ['(err)']
                continue
            if isinstance(thing, ReadDiscreteInputsResponse) or isinstance(thing, ReadCoilsResponse):
                value=0
                for i,b in enumerate(thing.bits):
                    value |= b<<i
            else:
                value = thing.getRegister(offset)
            self.mem[addr] = value
            debug_msg += [hex(value)]
        print('read range:', hex(addr_start), '-', hex(addr_start+count-1), 'data:', ' '.join(debug_msg))

    def read_range_2(self, addr_start, count, func):
        # need we worry about count being very big?
        return self.read_range_1(addr_start, count, func)

    def read_bulk(self, addresses, func):
        """
        reading via the RS485-to-TCP converter is very slow
        so here we attempt to merge multiple reads into one request
        """
        for addr_sequence in find_contiguous_ranges(addresses, max_delta=1):
            a = addr_sequence[0]
            n = addr_sequence[-1] - a + 1
            self.read_range_2(a, n, func)

    def read_single(self, addresses, func):
        for a in addresses:
            self.read_range_1(a, 1, func)

    def read_regs(self, ids=None):
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
            regs_to_read = list(self.regs[i] for i in ids)
            print('regs to read:', regs_to_read)

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

def main():
    host=os.environ.get('IP','127.0.0.1')
    port=int(os.environ.get('PORT',4196))
    print(host, port)

    client = ModbusTcpClient(host=host, port=port, framer='rtu', timeout=3)

    dev = Device(client=client, slave=1)
    dev.parse_config('mppt-device.json')
    #dev.read_regs(['B5'])
    dev.read_regs()
    dev.table()

main()

