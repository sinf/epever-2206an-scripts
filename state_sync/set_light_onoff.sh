#!/bin/sh
set -ex
. ./state_sync.sh

# coil: "force the load on/off. 1 turn on, 0 turn off (used for temporary test of the load)",
#sync_one_value force_load_onoff 1

# coil: "Enable load test mode. 1 enable, 0 disable (normal)"
#sync_one_value enable_load_test_mode 0

# coil: "Default control the load. When the load is default mode, 1=manual on, 0=manual off",
sync_one_value default_control_onoff 1

# coil: "output control mode manual/automatic. 1 output control mode manual, 0 output control mode automatic",
sync_one_value output_control_mode 0

#	"name": "load_controlling_modes",
#	"description": "load controlling modes, 0=manual, 1=light on/off, 2=light on+timer, 3=time control",
sync_one_value load_controlling_modes 1

# DTTV
sync_one_value day_time_threshold_volt 11.5
# minutes, when PV>DTTV for duration > (this), then day begins
sync_one_value light_signal_close_day_delay_time 15

# NTTV (probable typo: night->light)
sync_one_value light_time_threshold_volt 10.0
# minutes, when PV<NTTV for duration > (this), then night begins
sync_one_value light_signal_startup_night_delay_time 15

# should care?
#sync_one_value night_length 08:00:00


