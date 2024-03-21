# mppt-device.json fields per entry

# as documented in the pdf

## type
values: input , ...
modbus register type, which function code to use when reading

## address
if ends with 'h', it means base-16

## ip
same as "number" in Epever's datasheet
(in lowercase) used as ID for each entry, key in database, HTTP endpoint

## name
copypaste from pdf

## description
copypaste from pdf

## unit
copypaste from  pdf

## scale
inverse of scale in pdf
default 1

# Other custom stuff

## dbtable
values: none, config, stats, daily
This is used to choose which database table to write the changes in. Different tables have a different update frequency.
none: ignored
config: battery rated voltage, load on/off, etc..
stats: real time stats (current voltage, consumed energy, errors)
daily: daily min/max/avg etc.. daily summary of stats. includes real time clock

## write_only
true/false
if true, this value must not be ever read back


## status_bits
for bitmasks, this is a KV object defining purpose of bits
key=mask
subkey=state of bits extracted using the mask
value=description of what the flag means

## dtype
values:
short (16bit, 1 register)
long (32bit, 2 adjacent registers)
delay_hm (hour and minute packed into 16 bits)
delay_smh (hour, minute, second in adjacent registers)
date_sm_hd_MY (3 registers containing year:month day:min hour:sec)


## read_alone
true/false
if some register is weird and broken and must be read separately

