
import socket
import struct

host='127.0.0.1'
port=4196

print('read real-time battery voltage')
# device id=1, function code=4, register=0x3104, register count=1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    print('connect')
    s.settimeout(5)
    s.connect((host, port))

    msg='01 04 31 04 00 01 7e f7'
    print('send', msg)
    s.send(bytes.fromhex(msg))

    resp = s.recv(8)
    print('recv:', resp.hex() if type(resp) is bytes else resp)

volts = struct.unpack('>H', resp[3:5])[0] / 100.0
print('volts:', volts)

# Example output:
# recv: 0104020517fa6e
# volts: 13.03

