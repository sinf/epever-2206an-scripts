# Startup

This program can:
- read/write modbus registers via HTTP  
- periodically dump the registers into MQTT or a SQL database  

Relevant files:  
- config/epever-modbus-client-config.json (see epever-modbus-client-config.json.template)
- config/mppt-device.json

Usage:  
python epever-modbus-client.py  
python epever-modbus-client.py -c path/to/config.json  

Or:  
podman build -t epever  
podman run --rm -it -v ./config:/app/config:ro localhost/epever  

# Configuration options

|-|-|
|value|use|
|modbus\_client.ip|required|
|modbus\_client.port|required|
|modbus\_client.poll\_delay\_s|set to >=0 to read registers periodically even if they aren't sent anywhere|
|http\_api.bind\_ip||
|http\_api.port||
|http\_api.can\_write|if false, writing is disabled|
|http\_api.enable|http only available if true|
|mqtt\_.ip||
|mqtt\_.port||
|mqtt\_.topic|actual topic becomes $topic/<id>|
|mqtt\_.poll\_delay\_s|publish interval (only changed values)|
|mqtt\_.max\_publish\_interval|(seconds) publish values even if they haven't changed when they become older than this|
|mqtt\_.enable|true or false|
|db\_.url|database URL for SQL alchemy|
|db\_.table\_prefix|each register goes into a table named $table\_prefix<id> with columns t (time,s) and x (value)|
|db\_.poll\_delay\_s|db write interval (only changed values)|
|db\_.enable|if true and modbus\_client.polling=true, write state to database when polling|

# HTTP API

### Example

export addr=http://localhost:8000  

Query status and error codes  
curl $addr/c1  
curl $addr/c2  
curl $addr/c7  

Query real time clock:  
curl $addr/e20

Set real time clock:  
curl $addr/e20 -d now  
curl $addr/e20 -d $(date +%s)  
curl $addr/e20 -d 2024-03-07T17:15:02  

Set load on/off (H2 does nothing, ignore it)  
curl $addr/h3 -d 1  
curl $addr/h3 -d 0  

Set delays
curl $addr/e63 -d 02:30  
curl $addr/e67 -d 01:23:45


### GET /<tablename>

outputs all registers that have dbtable=<tablename>  
examples:
curl $addr/stats  
curl $addr/config  
curl $addr/daily  

### GET /<id>

output only one register

### POST /write

body: key=value pairs (application/x-www-form-urlencoded)  
sets multiple registers and returns (no) error for each  

### POST /<id>

set one register to value of post body

# Data usage

postgresql 16 uses 8192 bytes per empty table, 85 tables total = 696320 bytes overhead  

