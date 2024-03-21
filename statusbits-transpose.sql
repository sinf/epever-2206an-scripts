SELECT time,bit,msg FROM
(SELECT
TO_TIMESTAMP(t/1000) as time,'c1.000Fh' AS bit
,
CASE
WHEN var0=0 THEN 'normal'
WHEN var0=1 THEN 'overvolt'
WHEN var0=2 THEN 'undervolt'
WHEN var0=3 THEN 'low volt disconnect'
END msg
FROM ( SELECT
((c1 & 0xf) >> 0) AS var0,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c1.00F0h' AS bit
,
CASE
WHEN var1=0 THEN 'normal'
WHEN var1=1 THEN 'over temp (higher than the warning setting E24)'
WHEN var1=2 THEN 'low temp (lower than the warning setting E25)'
WHEN var1=3 THEN 'invalid state'
END msg
FROM ( SELECT
((c1 & 0xf0) >> 4) AS var1,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c1.0100h' AS bit
,
CASE
WHEN var2=0 THEN 'normal'
WHEN var2=1 THEN 'battery inner resistance abnormal'
END msg
FROM ( SELECT
((c1 & 0x100) >> 8) AS var2,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c1.8000h' AS bit
,
CASE
WHEN var3=0 THEN 'ok'
WHEN var3=1 THEN 'wrong identification for rated voltage'
END msg
FROM ( SELECT
((c1 & 0x8000) >> 15) AS var3,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.0001h' AS bit
,
CASE
WHEN var4=0 THEN 'standby'
WHEN var4=1 THEN 'running'
END msg
FROM ( SELECT
((c2 & 0x1) >> 0) AS var4,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.0002h' AS bit
,
CASE
WHEN var5=0 THEN 'normal'
WHEN var5=1 THEN 'fault'
END msg
FROM ( SELECT
((c2 & 0x2) >> 1) AS var5,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.000Ch' AS bit
,
CASE
WHEN var6=0 THEN 'no charging'
WHEN var6=1 THEN 'float'
WHEN var6=2 THEN 'boost'
WHEN var6=3 THEN 'equalization'
END msg
FROM ( SELECT
((c2 & 0xc) >> 2) AS var6,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.0010h' AS bit
,
CASE
WHEN var7=0 THEN 'ok'
WHEN var7=1 THEN 'PV input is short'
END msg
FROM ( SELECT
((c2 & 0x10) >> 4) AS var7,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.0080h' AS bit
,
CASE
WHEN var8=0 THEN 'ok'
WHEN var8=1 THEN 'load MOSFET is short'
END msg
FROM ( SELECT
((c2 & 0x80) >> 7) AS var8,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.0100h' AS bit
,
CASE
WHEN var9=0 THEN 'ok'
WHEN var9=1 THEN 'the load is short'
END msg
FROM ( SELECT
((c2 & 0x100) >> 8) AS var9,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.0200h' AS bit
,
CASE
WHEN var10=0 THEN 'ok'
WHEN var10=1 THEN 'the load is Over current.'
END msg
FROM ( SELECT
((c2 & 0x200) >> 9) AS var10,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.0400h' AS bit
,
CASE
WHEN var11=0 THEN 'ok'
WHEN var11=1 THEN 'input is over current.'
END msg
FROM ( SELECT
((c2 & 0x400) >> 10) AS var11,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.0800h' AS bit
,
CASE
WHEN var12=0 THEN 'ok'
WHEN var12=1 THEN 'anti-reverse MOSFET is short.'
END msg
FROM ( SELECT
((c2 & 0x800) >> 11) AS var12,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.1000h' AS bit
,
CASE
WHEN var13=0 THEN 'ok'
WHEN var13=1 THEN 'charging or anti-reverse MOSFET is short.'
END msg
FROM ( SELECT
((c2 & 0x1000) >> 12) AS var13,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.2000h' AS bit
,
CASE
WHEN var14=0 THEN 'ok'
WHEN var14=1 THEN 'charging MOSFET is short'
END msg
FROM ( SELECT
((c2 & 0x2000) >> 13) AS var14,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c2.C000h' AS bit
,
CASE
WHEN var15=0 THEN 'normal'
WHEN var15=1 THEN 'no power connected'
WHEN var15=2 THEN 'higher volt input'
WHEN var15=3 THEN 'input volt error'
END msg
FROM ( SELECT
((c2 & 0xc000) >> 14) AS var15,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0001h' AS bit
,
CASE
WHEN var16=0 THEN 'standby'
WHEN var16=1 THEN 'running'
END msg
FROM ( SELECT
((c7 & 0x1) >> 0) AS var16,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0002h' AS bit
,
CASE
WHEN var17=0 THEN 'normal'
WHEN var17=1 THEN 'fault'
END msg
FROM ( SELECT
((c7 & 0x2) >> 1) AS var17,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0010h' AS bit
,
CASE
WHEN var18=0 THEN 'ok'
WHEN var18=1 THEN 'output overpressure'
END msg
FROM ( SELECT
((c7 & 0x10) >> 4) AS var18,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0020h' AS bit
,
CASE
WHEN var19=0 THEN 'ok'
WHEN var19=1 THEN 'boost overpressure'
END msg
FROM ( SELECT
((c7 & 0x20) >> 5) AS var19,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0040h' AS bit
,
CASE
WHEN var20=0 THEN 'ok'
WHEN var20=1 THEN 'high voltage side short circuit'
END msg
FROM ( SELECT
((c7 & 0x40) >> 6) AS var20,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0080h' AS bit
,
CASE
WHEN var21=0 THEN 'ok'
WHEN var21=1 THEN 'input overpressure'
END msg
FROM ( SELECT
((c7 & 0x80) >> 7) AS var21,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0100h' AS bit
,
CASE
WHEN var22=0 THEN 'ok'
WHEN var22=1 THEN 'output voltage abnormal'
END msg
FROM ( SELECT
((c7 & 0x100) >> 8) AS var22,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0200h' AS bit
,
CASE
WHEN var23=0 THEN 'ok'
WHEN var23=1 THEN 'unable to stop discharging'
END msg
FROM ( SELECT
((c7 & 0x200) >> 9) AS var23,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0400h' AS bit
,
CASE
WHEN var24=0 THEN 'ok'
WHEN var24=1 THEN 'unable to discharge'
END msg
FROM ( SELECT
((c7 & 0x400) >> 10) AS var24,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.0800h' AS bit
,
CASE
WHEN var25=0 THEN 'ok'
WHEN var25=1 THEN 'short circuit'
END msg
FROM ( SELECT
((c7 & 0x800) >> 11) AS var25,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.7000h' AS bit
,
CASE
WHEN var26=0 THEN 'light load'
WHEN var26=1 THEN 'moderate load'
WHEN var26=2 THEN 'rated load'
WHEN var26=3 THEN 'overload'
END msg
FROM ( SELECT
((c7 & 0x7000) >> 12) AS var26,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))
UNION
(SELECT
TO_TIMESTAMP(t/1000) as time,'c7.C000h' AS bit
,
CASE
WHEN var27=0 THEN 'normal'
WHEN var27=1 THEN 'low'
WHEN var27=2 THEN 'high'
WHEN var27=3 THEN 'no access input volt error'
END msg
FROM ( SELECT
((c7 & 0xc000) >> 14) AS var27,
t FROM epever_stats
ORDER BY t DESC
LIMIT 1
))