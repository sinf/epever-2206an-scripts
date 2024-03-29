import json
import struct
import time
import sys
from threading import Lock
from .util import *

def tzcnt(x):
    return len(bin(x)) - len(bin(x).rstrip('0'))

def parse_status_bits(status_bits, value):
    status={}
    for mask_desc, flags_info in status_bits.items():
        mask_s, desc = mask_desc.split('|')
        mask = parse_address(mask_s)
        state = (value & mask) >> tzcnt(mask)
        status[mask_s] = f'[0x{state:x}] {desc}'
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
        """ j: object parsed from json 
        id: b3 or something, short unique string
        name: usable as database column name, e.g. battery_voltage
        dtype can be:
          short (16bit), default
          long (32bit)
          delay_hm (16bit)
          delay_smh (3x 16bit)
          date_sm_hd_MY (3x 16bit)
        """
        self.config = j
        self.type = j['type']
        self.id = j['id'].lower()
        self.name = j['name']
        self.address = parse_address(j['address'])
        self.unit = j.get('unit','')
        self.scale = j.get('scale', 1)
        self.dtype = j.get('dtype', 'short')
        self.dbtable = j.get('dbtable', 'none')
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
        """
        deadline parameter is used to force push (to db) even if value hasn't changed in a long time
        key is used to track last update time for each category of things
        """
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

