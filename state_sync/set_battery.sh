#!/bin/sh
set -ex
. ./state_sync.sh

# lead:    1=sealed, 2=GEL, 3=flooded, 0=user defined
# lithium: ?=LiFePo4, ?=Li(NiCoMn)O2 (3s/12V; 6s/24V) , ?=user(9-34V)
sync_one_value batt_type 2

# Ah
sync_one_value batt_rated_capacity 20

# dunno if this can be set
sync_one_value batt_rated_voltage 12

# XTRA manuals:
# when current>K*batt_rated_current for T seconds, it triggers overload protection
# K:1.02-1.05 , T:50
# K:1.05-1.25 , T:30
# K:1.25-1.35 , T:10
# K:1.35- , T:2
# attempts to recorrect 5 times after 5s, 10s, 15s, 20s, 25s
# overload flag is cleared either manually or at next sunrise if night>3h
sync_one_value batt_rated_current 5

# 0=auto, 1=12, 2=24, 3=36, 4=48, 5=60, 6=110, 7=120, 8=220, 9=240
sync_one_value batt_rated_voltage_code 1

# default:16, user: 9-17
sync_one_value high_volt_disocnnect 16

# default:13.8
sync_one_value float_voltage 13.8

# default:15, user: 9-17
sync_one_value charging_limit_voltage 15

# default:15, user: 9-17
sync_one_value over_voltage_reconnect 15

# sealed:14.6, gel:-, flooded:14.8
sync_one_value equalization_voltage 14.6

# default: 120 min, user:0-180 min
sync_one_value equalize_duration 120

# sealed:14.4, gel:14.2, flooded:14.6
sync_one_value boost_voltage 14.2

# default:120, user:10-180 min
sync_one_value boost_duration 120

# sealed:13.2, gel:13.2, flooded:13.2
sync_one_value boost_reconnect_voltage 13.2

# default:10.6
sync_one_value discharging_limit_voltage 11.6

# default:11.1
sync_one_value low_voltage_disconnect 11.8

# default:12.6
sync_one_value low_voltage_reconnect 12.6

# default: 12.2
sync_one_value under_voltage_recover 12.2

# default: 12
sync_one_value under_voltage_warning 12

sync_one_value battery_temperature_warning_upper_limit 40
sync_one_value battery_temperature_warning_lower_limit -35

# mV/celcius/2V
sync_one_value temperature_compensation_coefficient 0.10


#"description": "Usually 20%-80%. The percentage of battery's remaining capacity when stop charging",
#sync_one_value discharging_percentage 0.8

#"description": "depth of charge, 100%",
#sync_one_value charging_percentage 0.8

#	"description": "Management modes of battery charge and discharge, voltage compensation: 0 and SOC: 1",
#sync_one_value charging_management_modes 0

#"description": "battery type, 1=sealed, 2=GEL, 3=flooded, 0=user defined",
sync_one_value batt_type 0

