import time
import sys
from argparse import ArgumentParser
from .util import set_debug_level, debug_print, read_config, config
from .mqtt import start_mqtt
from .httpserver import start_http_server
from .db import start_db
from .device import create_device

def main():
    ap = ArgumentParser()
    ap.add_argument('-c', '--config-file', type=str, default='config/epever-modbus-client-config.json')
    ap.add_argument('-d', '--debug', action='store_true', default=False)
    ap.add_argument('-k', '--key', type=str)
    ap.add_argument('-v', '--value', type=str)
    ap.add_argument('-r', '--sync-rtc', default=False, action='store_true')
    args = ap.parse_args()

    if args.debug:
      set_debug_level(True)

    read_config(args.config_file)
    dev = create_device()

    if args.sync_rtc:
      dev.sync_rtc(time.time())

    if args.key:
      if args.key in ('*', 'all'):
        dev.read_all()
        dev.read_regs(dev.names('testing'))
        print(dev.table())
      else:
        err, msg = dev.write(args.key, args.value)
        print(err, msg)

if __name__ == '__main__':
    main()

