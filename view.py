
import json

prefix='epever_'

with open('config/mppt-device.json') as f:
    j=json.load(f)

regs=[]
for section in j['registers'].values():
    for item in section:
        regs += [item]

def things(table):
    for reg in regs:
        if item['dbtable'] == table:
            yield item['id'].lower(), item['name'], item['description']


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

def parse_address(x):
    if type(x) is str:
        x=x.lower()
        if x.endswith('h'):
            return int(x.rstrip('h'), 16)
        return int(x, 10)
    return int(x)

def tzcnt(x):
    return len(bin(x)) - len(bin(x).rstrip('0'))

def decode_bits():
    var_num=0
    q1='''SELECT
TO_TIMESTAMP(t/1000) as time,
'''
    q2='''
FROM ( SELECT t,
'''
    q3='''FROM epever_stats
ORDER BY t DESC
LIMIT 500
)'''
    for reg in regs:
        id=reg['id'].lower()
        sb = reg.get('status_bits')
        if sb:
            assert reg['dbtable'] == 'stats'
            for mask, statusvalues in sb.items():
                var = f'var{var_num}'
                var_num += 1
                q1 += 'CASE\n'
                for state, msg in statusvalues.items():
                    q1 += f"WHEN {var}={state} THEN '{msg}'\n"
                q1 += f"END '{id}.{mask}'\n"
                mask_nr = parse_address(mask)
                shr = tzcnt(mask_nr)
                q2 += f"(({id} & {hex(mask_nr)}) >> {shr}) AS {var}\n"
    return q1+q2+q3

print()
print(decode_bits())

