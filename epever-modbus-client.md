# Startup

Need files:  
- epever-modbus-client-config.json (see epever-modbus-client-config.json.template)
- mppt-device.json

python epever-modbus-client.py  

Query status and error codes  
curl http://localhost:8000/C1  
curl http://localhost:8000/C2  
curl http://localhost:8000/C7  

Query real time clock:  
curl http://localhost:8000/E20-E21-E22  

Set real time clock:  
curl http://localhost:8000/E20-E21-E22 -d now  
curl http://localhost:8000/E20-E21-E22 -d $(date +%s)  
curl http://localhost:8000/E20-E21-E22 -d 2024-03-07T17:15:02  

Set load on/off  
curl http://localhost:8000/H3 -d 1  
curl http://localhost:8000/H3 -d 0  

Set delays
curl http://localhost:8000/E63 -d 02:30  
curl http://localhost:8000/E67-E68-E69 -d 01:23:45


# Configuration options

|-|-|
|value|use|
|modbus\_client.ip|required|
|modbus\_client.port|required|
|modbus\_client.polling|set true to read full state periodically|
|http\_api.bind\_ip||
|http\_api.port||
|http\_api.can\_write|if false, writing is disabled|
|http\_api.enable|http only available if true|
|db\_.url|database URL for SQL alchemy|
|db\_.enable|if true and modbus\_client.polling=true, write state to database when polling|
|mqtt\_.\*|todo|

# ID

Each variable is identified by ID ("number" in mppt-device.json)
Variables using more than 1 register have longer ID such as E20-E21-E22 

# HTTP API

## GET /status

outputs all memory

## GET /status2

outputs less things than /status

## GET /<id>

output only one register

## POST /write

body: key=value pairs (application/x-www-form-urlencoded)  
sets multiple registers and returns (no) error for each  

## POST /<id>

set one register to value of post body

