
import json
import sqlalchemy as db 
import os
import subprocess
import time

"""
testing what sqlalchemy decides to use as data type
since it makes numeric range not very obvious
"""

def read_config(path):
    with open(path, 'r') as f:
        global the_config
        the_config = json.load(f)

def config(path, default=None):
    x=the_config
    for item in path.split('.'):
        x=x.get(item)
        if x is None:
            return default
    return x

def pg_exec(args):
    container='postgres_testing'
    subprocess.call(['podman', 'exec', '-it', container] + args)

def db_query(sql, *args):
    pg_exec(['psql', '-U', 'postgres', '-c', sql, *args])

def print_sizes():
    db_query("""
SELECT psu.schemaname as "schema", psu.relname AS table_name
    , to_char(sum(pg_total_relation_size(psu.relid)), '999,999,999,990') AS include_ndx
    , to_char(sum(pg_table_size(psu.relid)), '999,999,999,990') as whole_table
    , to_char(sum(pg_relation_size(psu.relid)), '99,999,999,990') AS not_toasts
    , to_char(sum(pg_table_size(psu.relid) - pg_relation_size(psu.relid)), '999,999,999,990') AS toasts
    , to_char(sum(pg_indexes_size(psu.relid)), '99,999,999,990') AS indexes
    , to_char(cl.reltuples, '999,999,990') as row_count
FROM pg_catalog.pg_statio_user_tables psu
    , pg_catalog.pg_class cl
where psu.relid = cl.oid
group by psu.schemaname, psu.relname, cl.reltuples
order by 1
;
""", 'testing')
    return
    db_query("""
SELECT table_schema, table_name, pg_relation_size('"'||table_schema||'"."'||table_name||'"')
FROM information_schema.tables WHERE table_schema='public'
;
""", 'testing')

def main():
    db_query('CREATE DATABASE testing;')

    # launch test database with test_postgres.sh
    url="postgresql+psycopg2://postgres:633f396d212b1229b6ce@127.0.0.1:7000/testing"
    en = db.create_engine(url)
    co = en.connect()
    me = db.MetaData()
    co.commit()

    names=[]
    for i, t_type in enumerate((
        # Float, Double, Numeric become 32-bit integer when used as primary key
            db.DateTime(),
            db.Time(),
            db.BigInteger(),
            #db.Numeric(14, 3),
            )):
        for j, x_type in enumerate((
                db.Float(),
                db.Double(),
                db.Numeric(12, 2),
                )):
            name=f"testing_{i}_{j}"
            names+=[name]
            table = db.Table(name, me,
                db.Column('t', t_type, primary_key=True),
                db.Column('x', x_type, nullable=False))

    me.create_all(en)
    co.commit()

    for name in names:
        db_query(f'\d {name}', 'testing')

    print_sizes()

    for i,name in enumerate(names):
        if i in (0, 1):
            db_query(f"""
INSERT INTO {name} SELECT
to_timestamp(RANDOM()*49045347542.0) AS t,
RANDOM() * 100000.0 AS x
FROM generate_series(1,1000000)
""", 'testing')
        else:
            db_query(f"""
INSERT INTO {name} SELECT
RANDOM() * 49045347542.0 AS t,
RANDOM() * 100000.0 AS x
FROM generate_series(1,1000000)
""", 'testing')

    print_sizes()

    co.close()

main()

