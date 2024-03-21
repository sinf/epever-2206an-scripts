import sys
import os

host=os.environ.get('IP','127.0.0.1')
port=int(os.environ.get('PORT',4196))

sys.path.insert(0, "./pyModbusTCP")

from pyModbusTCP.client import ModbusClient

print('init client')
client = ModbusClient(host=host, port=port, unit_id=1, auto_open=True, timeout=3, debug=True)

# PV voltage
print('read registers')
regs = client.read_input_registers(0x3104, 1)

print(regs)

print('done')
client.close()

