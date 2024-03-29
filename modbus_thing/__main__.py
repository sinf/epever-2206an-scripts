import time
import sys
from argparse import ArgumentParser
from .util import set_debug_level, debug_print, read_config, config
from .mqtt import start_mqtt
from .httpserver import start_http_server
from .db import start_db
from .device import create_device

rtc_sync_interval = 2*60*60
next_rtc_sync_t = 0
def maybe_sync_rtc(device):
    global next_rtc_sync_t
    now = time.time()
    if now > next_rtc_sync_t:
        next_rtc_sync_t = now + rtc_sync_interval
        device.sync_rtc(now)

def main_loop():
    poll_delay = config('modbus_client.poll_delay_s', -1)
    print('Enter main loop. Delay:', 10 if poll_delay<0 else poll_delay, 's')
    try:
        if poll_delay < 0:
            while True:
                maybe_sync_rtc(the_device)
                time.sleep(60)
        else:
            while True:
                maybe_sync_rtc(the_device)
                the_device.read_all()
                time.sleep(poll_delay)
    except KeyboardInterrupt:
        pass

def main():
    ap = ArgumentParser()
    ap.add_argument('-c', '--config-file', type=str, default='config/epever-modbus-client-config.json')
    ap.add_argument('-d', '--debug', action='store_true', default=False)
    ap.add_argument('-t', '--test-once', action='store_true', default=False)
    args = ap.parse_args()

    if args.debug:
      set_debug_level(True)

    read_config(args.config_file)

    global the_device
    the_device = create_device()

    th=[]
    debug_print('read all regs')
    the_device.read_all()

    if args.test_once:
        return

    debug_print('start threads')
    if config('http_api.enable') == True:
        th += [sv := start_http_server(the_device)]
    if config('mqtt.enable') == True:
        th += [dev := start_mqtt(the_device)]
    if config('db.enable') == True:
        th += [dev := start_db(the_device)]

    time.sleep(1)
    if all(t.is_alive() for t in th):
        main_loop()

    if False:
        for i,t in enumerate(th):
            debug_print(f'waiting for thread {i}/{len(th)}')
            t.join(timeout=30)
        print('done')


if __name__ == '__main__':
    main()

