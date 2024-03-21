
import socket
import struct
import json
import sys
import os

class TcpDriver:
    def __init__(self, slave_addr, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        self.socket = s
        self.slave_addr = slave_addr

    def close(self):
        self.socket.close()

    def read(self, count):
        data = self.socket.recv(count)
        print('read', data.hex(), file=sys.stderr)
        return data

    def write(self, data):
        # not standard protocol, this omits transaction id
        print('write', data.hex(), file=sys.stderr)
        self.socket.send(data)

def crc16(frame):
    crc = 0xFFFF
    for item in frame:
        next_byte = item
        crc ^= next_byte
        for _ in range(8):
            lsb = crc & 1
            crc >>= 1
            if lsb:
                crc ^= 0xA001
    return crc

def make_read_query(slave_addr, func, addr, numreg):
    x = struct.pack('>BBHH', slave_addr, func, addr, numreg)
    x += struct.pack('<H', crc16(x))
    return x

def parse_response(resp):
    slave_addr, func, data_len = struct.unpack('>BBB', resp[:3])
    data = resp[3:-2]
    assert len(data) == data_len
    crc_received = struct.unpack('<H', resp[-2:])[0]
    crc_expected = crc16(resp[:-2])
    if crc_received != crc_expected:
        print(f'crc received {hex(crc_got)}, crc expected {hex(crc_expected)}', file=sys.stderr)
        raise ValueError('crc check fail')
    return data

def data_conv_from(data, dtype):
    if dtype == 'uint16':
        value = struct.unpack('>H', data)[0]
    elif dtype == 'int32le':
        value = struct.unpack('>i', data[2:] + data[:2] )[0]
    else:
        raise ValueError(f'unknown dtype: {dtype}')
    return value

class Device:
    def __init__(self, path):
        with open(path) as f:
            self.config = json.load(f)
        self.regs = {}
        funcs = {
            'registers_RO': 0x04,
            'realtime_datum_RO': 0x04,
            'stats_RO': 0x04,
            'registers_RW': 0x03,
        }
        for section, things in self.config.items():
            func = funcs.get(section)
            if not func:
                print('unused section:', section, file=sys.stderr)
                continue
            for thing in things:
                name = thing['name']
                thing['section'] = section
                thing['address'] = int(thing['address'].rstrip('h'), 16)
                thing['func'] = func
                self.regs[name] = thing

    def read_regs(self, driver, func, addr, count):
        query = make_read_query(driver.slave_addr, func, addr, count)
        driver.write(query)
        resp_raw = driver.read(256)
        resp = parse_response(resp_raw)
        return resp

    def read_all(self, driver):
        count_by_type = {
            'uint16': 1,
            'int32le': 2,
        }
        output=''
        cur_section=None
        for reg in self.regs.values():
            #if reg['address'] != 0x3104: continue ;
            print('reading:', reg['name'], reg['address'], reg['func'], file=sys.stderr)
            dtype = reg.get('dtype', 'uint16')
            count = count_by_type[dtype]
            data = self.read_regs(driver, reg['func'], reg['address'], count)
            value = data_conv_from(data, dtype) * reg.get('scale', 1)
            unit = reg.get('unit', '')
            num = reg.get("number","-")
            num = ','.join(num) if type(num) is list else num
            if reg['section'] != cur_section:
                cur_section = reg['section']
                output += f'\n# {cur_section}\n' 
            output += f'{num:8s} {reg["name"]:45s} {data.hex():8s}  {str(value):10.10s} {unit}\n'
        #return output
        print(output)

def main():
    host='127.0.0.1'
    port=4196
    dr=TcpDriver(slave_addr=1, host=host, port=port)
    try:
        dev=Device('mppt-device.json')
        #dev.read_regs(dr, 0x4, 0x3104, 1)
        dev.read_all(dr)
    finally:
        dr.close()

main()

