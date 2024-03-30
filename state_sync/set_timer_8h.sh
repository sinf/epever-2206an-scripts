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
sync_one_value load_controlling_modes 3

# used with light on+timer ??
#sync_one_value working_time_length_1 01:00
#sync_one_value working_time_length_2 01:00

# used with timer control, which one?
sync_one_value turn_on_timing_1 09:00:00
sync_one_value turn_off_timing_1 09:00:00
sync_one_value turn_on_timing_2 09:00:00
sync_one_value turn_off_timing_2 09:00:00

# dunno?
#sync_one_value night_length 08:00

# 2206AN pdf doesnt mention timer 3, does it exist?

# what are these?
sync_one_value working_time_length_1 00:10
sync_one_value working_time_length_2 00:20
sync_one_value working_time_length_3 00:30

# or these?
sync_one_value working_time2_length_1 00:10
sync_one_value working_time2_length_2 00:20
sync_one_value working_time2_length_3 00:30

# enable timer2 ?
sync_one_value timed_control_qutum 1

