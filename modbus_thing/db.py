import sys
import time
import traceback
from threading import Thread
import logging

try:
  import sqlalchemy as db 
except ImportError:
  print('failed to import sqlalchemy', file=sys.stderr)

from .util import *
from .register import *
from .device import *

def get_dtype(reg):
  if reg.dtype in ('short', 'long'):
      return db.Integer() if reg.is_integer_type() else db.Float()
  elif reg.dtype in ('delay_hm', 'delay_smh'):
      return db.String(length=8)
  elif reg.dtype == 'date_sm_hd_MY':
      return db.String(length=20)
  else:
      raise Exception("unimplemented")

def start_db(the_device):
    if get_debug_level():
      logging.basicConfig()
      logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    url=config("db.url")
    print('starting db thread:')
    en = db.create_engine(url)
    co = en.connect()
    me = db.MetaData()
    tables = {}
    prefix = config('db.table_prefix','')

    # real time stats: 1 line per status update
    for table_name, regs in the_device.dbtable_regs.items():
        cols = [
          db.Column('t', db.BigInteger(), primary_key=True),
          db.Column('device_id', db.Integer(), nullable=False),
        ]
        for reg in regs.values():
            cols += [db.Column(reg.name, get_dtype(reg), nullable=False)]
        tables[table_name] = db.Table(prefix+table_name, me, *cols)

    me.create_all(en)
    co.commit()

    def db_main():
        debug_print('db main loop')
        while True:
            delay = config("db.poll_delay_s",30)
            for table_name in tables:
                debug_print(f'sql: check table {table_name}')
                tv = int(config(f'db.{table_name}.interval', 24*60*60))
                ids = the_device.names(table_name)
                the_device.read_regs(ids, update_older_than=time.time()-delay)
                things = the_device.collect_for_push(key='db_'+table_name, max_update_interval=tv, names=ids)
                if things:
                    debug_print('sql push update to', table_name)
                    values = {}
                    t=0
                    for r in the_device.dbtable_regs[table_name].values():
                        values[r.name] = r.value if r.value is not None else 0
                        t = max(t, r.last_write_t)
                    t = int(t*1000) # s -> ms
                    values['t'] = t
                    values['device_id'] = 0 # future proofing database for when I have more devices
                    try:
                        co.execute(db.insert(tables[table_name]).values(**values))
                        co.commit()
                    except db.exc.IntegrityError as e:
                        print(traceback.format_exc(), file=sys.stderr) # same timestamp?
                        co.execute('rollback')
                        co.commit()

            time.sleep(delay)
    t=Thread(target=db_main, daemon=True, name='db-client')
    t.start()
    return t

