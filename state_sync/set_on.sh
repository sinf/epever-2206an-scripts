#!/bin/sh
set -ex
. ./state_sync.sh

# coil: "force the load on/off. 1 turn on, 0 turn off (used for temporary test of the load)",
#sync_one_value force_load_onoff 1

# coil: "Enable load test mode. 1 enable, 0 disable (normal)"
#sync_one_value enable_load_test_mode 0

# holding: "Default Load On/Off in manual mode, 0=off, 1=on",
sync_one_value manual_default_load_onoff 1

# coil: "Manual control the load. When the load is manual mode, 1=manual on, 0=manual off",
sync_one_value manual_control_onoff 1

# coil: "Default control the load. When the load is default mode, 1=manual on, 0=manual off",
sync_one_value default_control_onoff 1

# coil: "output control mode manual/automatic. 1 output control mode manual, 0 output control mode automatic",
sync_one_value output_control_mode 1

#	0=manual, 1=light on/off, 2=light on+timer, 3=time control",
sync_one_value load_controlling_modes 0

