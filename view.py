
import json

with open('config/mppt-device.json') as f:
    j=json.load(f)

def things(table):
    for section in j['registers'].values():
        for item in section:
            if item['dbtable'] == table:
                yield item['id'].lower(), item['name'], item['description']


prefix='epever_'
for table in ('stats', 'config', 'daily'):
    print(f'CREATE VIEW {prefix}{table}_name AS SELECT\n',
          't, device_id,\n' + \
          ',\n'.join(f'{id} AS {name}' for id,name,descr in things(table)),
          f'\nFROM {prefix}{table};', sep='')
    print()

for table in ('stats', 'config', 'daily'):
    print(f'CREATE TABLE {prefix}descr (id varchar(8), table varchar(8), desc(1024));')

for table in ('stats', 'config', 'daily'):
    for id,name,descr in things(table):
        print(f"INSERT INTO {prefix}descr VALUES ('{id}', '{table}', '", descr.replace("'","\\'"), "');", sep='')
    print()

