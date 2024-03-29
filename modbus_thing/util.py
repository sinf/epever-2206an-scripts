import json
import sys
import time

enable_debug_print=False

def set_debug_level(level):
  global enable_debug_print
  enable_debug_print=level

def debug_print(*args, **kwargs):
    if enable_debug_print:
      print(time.strftime('[%y-%m-%d %H:%M:%S]'), *args, **kwargs, file=sys.stderr)

def read_config(path):
    print('config file:', path)
    with open(path, 'r') as f:
        global the_config
        the_config = json.load(f)
    print(the_config.get('description'))

def config(path, default=None):
    x=the_config
    for item in path.split('.'):
        x=x.get(item)
        if x is None:
            return default
    return x
