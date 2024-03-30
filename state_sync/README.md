# scripts to use with cron or manually

## state_sync.sh

sets one register via HTTP if it differs from requested value
can be called from cronjob to persistently force a register to some value (even if endpoint is offline sometimes)
used by the other scripts

## set_battery.sh

set all battery settings in 1 go

## set_on.sh

set to manual mode and permanently on

## set_light_onoff.sh

set to light on/off mode (only stay on while there is daylight)

## set_timer_15m.sh

set to timer mode and on for 15min per day

## set_timer_8h.sh

set to timer mode and on for 8h per day

## set_timer_16h.sh

set to timer mode and on for 16h per day

