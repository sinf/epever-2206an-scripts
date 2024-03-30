from pymodbus.bit_read_message import ReadDiscreteInputsResponse, ReadCoilsResponse
from pymodbus.register_read_message import ReadInputRegistersResponse, ReadHoldingRegistersResponse
from pymodbus.register_write_message import WriteMultipleRegistersResponse
import random

def bitlist(x):
  return list(reversed(list((int(i) for i in bin(x)[2:]))))

class FakeClient:
  def __init__(self, *args, **kwargs):
    self.data={}
  
  def _write(self, address, values, slave, kind):
    for value in values:
      self.data[address] = value
      address += 1

  def _read(self, address, count, slave, kind, xmin, xmax):
    out=[]
    for i in range(count):
      addr_i = address + i
      if addr_i in self.data:
        x=self.data[addr_i]
      else:
        x=int(random.uniform(xmin, xmax)+0.5)
      x = max(xmin,min(xmax,x))
      out += [x]
    return out

  def write_registers(self, address, words, slave):
    self._write(address, words, slave, 'reg')
    return WriteMultipleRegistersResponse(address=address, count=len(words))
  def write_register(self, address, word, slave):
    return self.write_registers(address, [word], slave)
  def write_coils(self, address, values, slave):
    self._write(address, values, slave, 'coil')
    return WriteMultipleRegistersResponse(address=address, count=len(values))
  def write_coil(self, address, value, slave):
    return self.write_coils(address, [value], slave)

  def read_input_registers(self, address, count, slave):
    return ReadInputRegistersResponse(
      values=self._read(address, count, slave, 'input', 0, 0xFFFF),
    )
  def read_holding_registers(self, address, count, slave):
    return ReadHoldingRegistersResponse(
      values=self._read(address, count, slave, 'holding', 0, 0xFFFF),
    )
  def read_discrete_inputs(self, address, count, slave):
    assert count == 1
    values = self._read(address, count, slave, 'discrete', 0, 1)
    return ReadDiscreteInputsResponse(values=bitlist(values[0]), slave=slave)
  def read_coils(self, address, count, slave):
    assert count == 1
    values = self._read(address, count, slave, 'coil', 0, 1)
    return ReadCoilsResponse(values=bitlist(values[0]), slave=slave)

