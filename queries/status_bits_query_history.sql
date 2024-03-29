SELECT
TO_TIMESTAMP(t/1000) as time,
CASE
WHEN var0=0 THEN 'normal'
WHEN var0=1 THEN 'overvolt'
WHEN var0=2 THEN 'undervolt'
WHEN var0=3 THEN 'low volt disconnect'
END "batt_status.000Fh"
,
CASE
WHEN var1=0 THEN 'normal'
WHEN var1=1 THEN 'over temp (higher than the warning setting E24)'
WHEN var1=2 THEN 'low temp (lower than the warning setting E25)'
WHEN var1=3 THEN 'invalid state'
END "batt_status.00F0h"
,
CASE
WHEN var2=0 THEN 'normal'
WHEN var2=1 THEN 'battery inner resistance abnormal'
END "batt_status.0100h"
,
CASE
WHEN var3=0 THEN 'ok'
WHEN var3=1 THEN 'wrong identification for rated voltage'
END "batt_status.8000h"
,
CASE
WHEN var4=0 THEN 'standby'
WHEN var4=1 THEN 'running'
END "qu_charging_status.0001h"
,
CASE
WHEN var5=0 THEN 'normal'
WHEN var5=1 THEN 'fault'
END "qu_charging_status.0002h"
,
CASE
WHEN var6=0 THEN 'no charging'
WHEN var6=1 THEN 'float'
WHEN var6=2 THEN 'boost'
WHEN var6=3 THEN 'equalization'
END "qu_charging_status.000Ch"
,
CASE
WHEN var7=0 THEN 'ok'
WHEN var7=1 THEN 'PV input is short'
END "qu_charging_status.0010h"
,
CASE
WHEN var8=0 THEN 'ok'
WHEN var8=1 THEN 'load MOSFET is short'
END "qu_charging_status.0080h"
,
CASE
WHEN var9=0 THEN 'ok'
WHEN var9=1 THEN 'the load is short'
END "qu_charging_status.0100h"
,
CASE
WHEN var10=0 THEN 'ok'
WHEN var10=1 THEN 'the load is Over current.'
END "qu_charging_status.0200h"
,
CASE
WHEN var11=0 THEN 'ok'
WHEN var11=1 THEN 'input is over current.'
END "qu_charging_status.0400h"
,
CASE
WHEN var12=0 THEN 'ok'
WHEN var12=1 THEN 'anti-reverse MOSFET is short.'
END "qu_charging_status.0800h"
,
CASE
WHEN var13=0 THEN 'ok'
WHEN var13=1 THEN 'charging or anti-reverse MOSFET is short.'
END "qu_charging_status.1000h"
,
CASE
WHEN var14=0 THEN 'ok'
WHEN var14=1 THEN 'charging MOSFET is short'
END "qu_charging_status.2000h"
,
CASE
WHEN var15=0 THEN 'normal'
WHEN var15=1 THEN 'no power connected'
WHEN var15=2 THEN 'higher volt input'
WHEN var15=3 THEN 'input volt error'
END "qu_charging_status.C000h"
,
CASE
WHEN var16=0 THEN 'standby'
WHEN var16=1 THEN 'running'
END "eq_discharging_status.0001h"
,
CASE
WHEN var17=0 THEN 'normal'
WHEN var17=1 THEN 'fault'
END "eq_discharging_status.0002h"
,
CASE
WHEN var18=0 THEN 'ok'
WHEN var18=1 THEN 'output overpressure'
END "eq_discharging_status.0010h"
,
CASE
WHEN var19=0 THEN 'ok'
WHEN var19=1 THEN 'boost overpressure'
END "eq_discharging_status.0020h"
,
CASE
WHEN var20=0 THEN 'ok'
WHEN var20=1 THEN 'high voltage side short circuit'
END "eq_discharging_status.0040h"
,
CASE
WHEN var21=0 THEN 'ok'
WHEN var21=1 THEN 'input overpressure'
END "eq_discharging_status.0080h"
,
CASE
WHEN var22=0 THEN 'ok'
WHEN var22=1 THEN 'output voltage abnormal'
END "eq_discharging_status.0100h"
,
CASE
WHEN var23=0 THEN 'ok'
WHEN var23=1 THEN 'unable to stop discharging'
END "eq_discharging_status.0200h"
,
CASE
WHEN var24=0 THEN 'ok'
WHEN var24=1 THEN 'unable to discharge'
END "eq_discharging_status.0400h"
,
CASE
WHEN var25=0 THEN 'ok'
WHEN var25=1 THEN 'short circuit'
END "eq_discharging_status.0800h"
,
CASE
WHEN var26=0 THEN 'light load'
WHEN var26=1 THEN 'moderate load'
WHEN var26=2 THEN 'rated load'
WHEN var26=3 THEN 'overload'
END "eq_discharging_status.7000h"
,
CASE
WHEN var27=0 THEN 'normal'
WHEN var27=1 THEN 'low'
WHEN var27=2 THEN 'high'
WHEN var27=3 THEN 'no access input volt error'
END "eq_discharging_status.C000h"

FROM ( SELECT
((batt_status & 0xf) >> 0) AS var0,
((batt_status & 0xf0) >> 4) AS var1,
((batt_status & 0x100) >> 8) AS var2,
((batt_status & 0x8000) >> 15) AS var3,
((qu_charging_status & 0x1) >> 0) AS var4,
((qu_charging_status & 0x2) >> 1) AS var5,
((qu_charging_status & 0xc) >> 2) AS var6,
((qu_charging_status & 0x10) >> 4) AS var7,
((qu_charging_status & 0x80) >> 7) AS var8,
((qu_charging_status & 0x100) >> 8) AS var9,
((qu_charging_status & 0x200) >> 9) AS var10,
((qu_charging_status & 0x400) >> 10) AS var11,
((qu_charging_status & 0x800) >> 11) AS var12,
((qu_charging_status & 0x1000) >> 12) AS var13,
((qu_charging_status & 0x2000) >> 13) AS var14,
((qu_charging_status & 0xc000) >> 14) AS var15,
((eq_discharging_status & 0x1) >> 0) AS var16,
((eq_discharging_status & 0x2) >> 1) AS var17,
((eq_discharging_status & 0x10) >> 4) AS var18,
((eq_discharging_status & 0x20) >> 5) AS var19,
((eq_discharging_status & 0x40) >> 6) AS var20,
((eq_discharging_status & 0x80) >> 7) AS var21,
((eq_discharging_status & 0x100) >> 8) AS var22,
((eq_discharging_status & 0x200) >> 9) AS var23,
((eq_discharging_status & 0x400) >> 10) AS var24,
((eq_discharging_status & 0x800) >> 11) AS var25,
((eq_discharging_status & 0x7000) >> 12) AS var26,
((eq_discharging_status & 0xc000) >> 14) AS var27,
t FROM epever_stats
ORDER BY t DESC
LIMIT 500
)
