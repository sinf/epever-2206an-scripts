import sys
import os

host=os.environ.get('IP','127.0.0.1')
port=int(os.environ.get('PORT',4196))
print(host,port)

#from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusTcpClient as ModbusClient

print('init client')
client = ModbusClient(host=host, port=port, framer='rtu', timeout=3)

# PV voltage
print('read registers')
regs = client.read_input_registers(address=0x3104, count=1, slave=1)

print('err:', regs.isError())
print('reg:', regs.getRegister(0))
print('func:', regs.function_code)

print('done')
client.close()

