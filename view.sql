CREATE VIEW epever_stats_name AS SELECT
t, device_id,
b1 AS pv_input_voltage,
b2 AS pv_input_current,
b3 AS pv_input_power,
b5 AS batt_rtvoltage,
b7 AS batt_power,
b13 AS load_voltage,
b14 AS load_current,
b15 AS load_power,
b17 AS batt_temp,
b18 AS eq_temp,
b27 AS batt_soc,
b28 AS batt_tempr,
c1 AS batt_status,
c2 AS qu_charging_status,
c7 AS eq_discharging_status,
d0 AS pv_max_volt_d,
d1 AS pv_min_volt_d,
d2 AS batt_max_volt_d,
d3 AS batt_min_volt_d,
d4 AS e_consumed_d,
d10 AS e_consumed,
d12 AS e_generated_d,
d18 AS e_generated,
d26 AS batt_voltage,
d27 AS batt_current,
h3 AS manual_control_onoff,
h4 AS default_control_onoff,
h7 AS force_load_onoff,
i1 AS over_temperature_flag,
i12 AS is_day
FROM epever_stats;

CREATE VIEW epever_config_name AS SELECT
t, device_id,
x0 AS pv_rated_voltage,
x1 AS pv_rated_current,
x2 AS pv_rated_power,
x3 AS batt_rated_voltage,
x4 AS batt_rated_current,
x5 AS batt_rated_power,
x6 AS charging_mode,
x7 AS load_rated_current,
b30 AS batt_rated_volt,
e1 AS batt_type,
e2 AS batt_rated_capacity,
e3 AS temperature_compensation_coefficient,
e4 AS high_volt_disocnnect,
e5 AS charging_limit_voltage,
e6 AS over_voltage_reconnect,
e7 AS equalization_voltage,
e8 AS boost_voltage,
e9 AS float_voltage,
e10 AS boost_reconnect_voltage,
e11 AS low_voltage_reconnect,
e12 AS under_voltage_recover,
e13 AS under_voltage_warning,
e14 AS low_voltage_disconnect,
e15 AS discharging_limit_voltage,
e24 AS battery_temperature_warning_upper_limit,
e25 AS battery_temperature_warning_lower_limit,
e26 AS controller_inner_temperature_upper_limit,
e27 AS controller_inner_temperature_upper_limit_recover,
e31 AS day_time_threshold_volt,
e32 AS light_signal_startup_night_delay_time,
e33 AS light_time_threshold_volt,
e34 AS light_signal_close_day_delay_time,
e62 AS load_controlling_modes,
e63 AS working_time_length_1,
e64 AS working_time_length_2,
e67 AS turn_on_timing_1,
e70 AS turn_off_timing_1,
e73 AS turn_on_timing_2,
e76 AS turn_off_timing_2,
e100 AS backlight_time,
e102 AS night_length,
e103 AS main_power_supply,
e104 AS batt_rated_voltage_code,
e107 AS manual_default_load_onoff,
e108 AS equalize_duration,
e109 AS boost_duration,
e110 AS discharging_percentage,
e111 AS charging_percentage,
e113 AS charging_management_modes,
h1 AS charging_device_onoff,
h2 AS output_control_mode,
h6 AS enable_load_test_mode
FROM epever_config;

CREATE VIEW epever_daily_name AS SELECT
t, device_id,
d6 AS e_consumed_m,
d8 AS e_consumed_y,
d14 AS e_generated_m,
d16 AS e_generated_y,
e20 AS real_time_clock
FROM epever_daily;

CREATE TABLE epever_descr (id varchar(8), table varchar(8), desc(1024));
CREATE TABLE epever_descr (id varchar(8), table varchar(8), desc(1024));
CREATE TABLE epever_descr (id varchar(8), table varchar(8), desc(1024));
INSERT INTO epever_descr VALUES ('b1', 'stats', 'PV array input voltage; Solar charge controller--PV array voltage');
INSERT INTO epever_descr VALUES ('b2', 'stats', 'Solar charge controller--PV array current');
INSERT INTO epever_descr VALUES ('b3', 'stats', 'Solar charge controller--PV array power');
INSERT INTO epever_descr VALUES ('b5', 'stats', 'real time battery voltage; undocumented in ControllerProtocolV2.3 table but mentioned in example');
INSERT INTO epever_descr VALUES ('b7', 'stats', 'battery charging power');
INSERT INTO epever_descr VALUES ('b13', 'stats', 'load voltage');
INSERT INTO epever_descr VALUES ('b14', 'stats', 'load current');
INSERT INTO epever_descr VALUES ('b15', 'stats', 'load power');
INSERT INTO epever_descr VALUES ('b17', 'stats', 'battery temperature');
INSERT INTO epever_descr VALUES ('b18', 'stats', 'temperature inside equipment; temperature inside case');
INSERT INTO epever_descr VALUES ('b27', 'stats', 'battery SOC; The percentage of battery\'s remaining capacity');
INSERT INTO epever_descr VALUES ('b28', 'stats', 'The battery temperature measured by remote temperature sensor');
INSERT INTO epever_descr VALUES ('c1', 'stats', 'D3-D0: 01H Overvolt , 00H Normal ,
02H Under Volt, 03H Low Volt
Disconnect, 04H Fault
D7-D4: 00H Normal, 01H Over
Temp.(Higher than the warning
settings), 02H Low Temp.(Lower
than the warning settings),
D8: Battery inner resistance
abnormal 1,
normal 0
D15: 1-Wrong identification for rated
voltage');
INSERT INTO epever_descr VALUES ('c2', 'stats', 'charging equipment status;
D15-D14: Input volt status. 00
normal, 01 no
power connected, 02H Higher volt
input, 03H
Input volt error.
D13: Charging MOSFET is short.
D12: Charging or Anti-reverse
MOSFET is short.
D11: Anti-reverse MOSFET is short.
D10: Input is over current.
D9: The load is Over current.
D8: The load is short.
D7: Load MOSFET is short.
D4: PV Input is short.
D3-2: Charging status. 00 No
charging,01 Float,02
Boost, 03 Equalization.
D1: 0 Normal, 1 Fault.
D0: 1 Running, 0 Standby.
');
INSERT INTO epever_descr VALUES ('c7', 'stats', 'equipment discharging status
D15-D14: 00H normal, 01H low,
02H High, 03H no access
Input volt error.
D13-D12: output power:00-light
load,01-moderate,02-rated,03-overlo
ad
D11: short circuit
D10: unable to discharge
D9: unable to stop discharging
D8: output voltage abnormal
D7: input overpressure
D6: high voltage side short circuit
D5: boost overpressure
D4: output overpressure
D1: 0 Normal, 1 Fault.
D0: 1 Running, 0 Standby.');
INSERT INTO epever_descr VALUES ('d0', 'stats', 'maximum PV voltage today, 00:00 refresh every day');
INSERT INTO epever_descr VALUES ('d1', 'stats', 'minimum PV voltage today, 00:00 refresh every day');
INSERT INTO epever_descr VALUES ('d2', 'stats', 'maximum battery voltage today, 00:00 refresh every day');
INSERT INTO epever_descr VALUES ('d3', 'stats', 'minimum battery voltage today, 00:00 refresh every day');
INSERT INTO epever_descr VALUES ('d4', 'stats', 'consumed energy today, 00:00 clear every day');
INSERT INTO epever_descr VALUES ('d10', 'stats', 'total consumed energy');
INSERT INTO epever_descr VALUES ('d12', 'stats', 'generated energy today, 00:00 clear every day');
INSERT INTO epever_descr VALUES ('d18', 'stats', 'total generated energy');
INSERT INTO epever_descr VALUES ('d26', 'stats', 'battery voltage');
INSERT INTO epever_descr VALUES ('d27', 'stats', 'battery current');
INSERT INTO epever_descr VALUES ('h3', 'stats', 'Manual control the load. When the load is manual mode, 1=manual on, 0=manual off');
INSERT INTO epever_descr VALUES ('h4', 'stats', 'Default control the load. When the load is default mode, 1=manual on, 0=manual off');
INSERT INTO epever_descr VALUES ('h7', 'stats', 'force the load on/off. 1 turn on, 0 turn off (used for temporary test of the load)');
INSERT INTO epever_descr VALUES ('i1', 'stats', 'Over temperature inside the device. 1 The temperature inside the controller is higher than the over-temperature protection point. 0 Normal');
INSERT INTO epever_descr VALUES ('i12', 'stats', 'day/night. 1-Night, 0-Day');

INSERT INTO epever_descr VALUES ('x0', 'config', 'PV array rated voltage');
INSERT INTO epever_descr VALUES ('x1', 'config', 'PV array rated current');
INSERT INTO epever_descr VALUES ('x2', 'config', 'PV array rated power');
INSERT INTO epever_descr VALUES ('x3', 'config', 'rated voltage to battery');
INSERT INTO epever_descr VALUES ('x4', 'config', 'rated current to battery');
INSERT INTO epever_descr VALUES ('x5', 'config', 'rated power to battery');
INSERT INTO epever_descr VALUES ('x6', 'config', 'charging mode 0=connect/disconnect, 1=PWM, 2=MPPT');
INSERT INTO epever_descr VALUES ('x7', 'config', 'rated current of load');
INSERT INTO epever_descr VALUES ('b30', 'config', 'Current system rated voltage. 1200, 2400, 3600, 4800 represent 12V， 24V，36V，48V');
INSERT INTO epever_descr VALUES ('e1', 'config', 'battery type, 1=sealed, 2=GEL, 3=flooded, 0=user defined');
INSERT INTO epever_descr VALUES ('e2', 'config', 'battery capacity, rated capacity of battery');
INSERT INTO epever_descr VALUES ('e3', 'config', 'temperature compensation coefficient, range 0-9');
INSERT INTO epever_descr VALUES ('e4', 'config', 'high volt disocnnect');
INSERT INTO epever_descr VALUES ('e5', 'config', 'charging limit voltage');
INSERT INTO epever_descr VALUES ('e6', 'config', 'over voltage reconnect');
INSERT INTO epever_descr VALUES ('e7', 'config', 'equalization voltage');
INSERT INTO epever_descr VALUES ('e8', 'config', 'boost voltage');
INSERT INTO epever_descr VALUES ('e9', 'config', 'float voltage');
INSERT INTO epever_descr VALUES ('e10', 'config', 'boost reconnect voltage');
INSERT INTO epever_descr VALUES ('e11', 'config', 'low voltage reconnect');
INSERT INTO epever_descr VALUES ('e12', 'config', 'under voltage recover');
INSERT INTO epever_descr VALUES ('e13', 'config', 'under voltage warning');
INSERT INTO epever_descr VALUES ('e14', 'config', 'low voltage disconnect');
INSERT INTO epever_descr VALUES ('e15', 'config', 'discharging limit voltage');
INSERT INTO epever_descr VALUES ('e24', 'config', 'battery temperature warning upper limit');
INSERT INTO epever_descr VALUES ('e25', 'config', 'battery temperature warning lower limit');
INSERT INTO epever_descr VALUES ('e26', 'config', 'controller inner temperature upper limit');
INSERT INTO epever_descr VALUES ('e27', 'config', 'controller inner temperature upper limit recover. Over Temperature, system recover once it drop to lower than this value');
INSERT INTO epever_descr VALUES ('e31', 'config', 'day time threshold volt (DTTV), PV lower than this value, controller would detect it as sundown');
INSERT INTO epever_descr VALUES ('e32', 'config', 'light signal startup (night) delay time, PV voltage lower than NTTV, and duration exceeds the Light signal startup (night) delay time, controller would detect it as night time');
INSERT INTO epever_descr VALUES ('e33', 'config', 'light time threshold volt (NTTV), PV voltage higher than this value, controller would detect it as sunrise');
INSERT INTO epever_descr VALUES ('e34', 'config', 'light signal close (day) delay time, PV voltage higher than DTTV, and duration exceeds the Light signal close (day) delay time, controller would detect it as day time');
INSERT INTO epever_descr VALUES ('e62', 'config', 'load controlling modes, 0=manual, 1=light on/off, 2=light on+timer, 3=time control');
INSERT INTO epever_descr VALUES ('e63', 'config', 'Working time length 1. The length of load output timer1, D15-D8: hour , D7-D0: minute');
INSERT INTO epever_descr VALUES ('e64', 'config', 'Working time length 2. The length of load output timer2, D15-D8: hour , D7-D0: minute');
INSERT INTO epever_descr VALUES ('e67', 'config', 'Turn on timing 1. Turn on timing of load output');
INSERT INTO epever_descr VALUES ('e70', 'config', 'Turn off timing 1. Turn off timing of load output');
INSERT INTO epever_descr VALUES ('e73', 'config', 'Turn on timing 2. Turn on timing of load output');
INSERT INTO epever_descr VALUES ('e76', 'config', 'Turn off timing 2, Turn off timing of load output');
INSERT INTO epever_descr VALUES ('e100', 'config', 'Backlight time. Close after LCD backlight light setting the number of seconds');
INSERT INTO epever_descr VALUES ('e102', 'config', 'Length of night. Set default values of the whole night length of time. D15-D8: hour, D7-D0: minute');
INSERT INTO epever_descr VALUES ('e103', 'config', 'Device configure of main power supply. 1=battery is main, 2= AC-DC power mainly');
INSERT INTO epever_descr VALUES ('e104', 'config', 'battery rated voltage code. 0, auto recognize. 1-12V, 2-24V ,3-36V，4-48V，5-60V， 6-110V，7-120V，8-220V，9-240V');
INSERT INTO epever_descr VALUES ('e107', 'config', 'Default Load On/Off in manual mode, 0=off, 1=on');
INSERT INTO epever_descr VALUES ('e108', 'config', 'Equalize duration. Usually 0-120 minutes');
INSERT INTO epever_descr VALUES ('e109', 'config', 'Boost duration. Usually 10-120 minutes');
INSERT INTO epever_descr VALUES ('e110', 'config', 'Usually 20%-80%. The percentage of battery\'s remaining capacity when stop charging');
INSERT INTO epever_descr VALUES ('e111', 'config', 'depth of charge, 100%');
INSERT INTO epever_descr VALUES ('e113', 'config', 'Management modes of battery charge and discharge, voltage compensation: 0 and SOC: 1');
INSERT INTO epever_descr VALUES ('h1', 'config', '1 charging device on, 0 charging device off');
INSERT INTO epever_descr VALUES ('h2', 'config', 'output control mode manual/automatic. 1 output control mode manual, 0 output control mode automatic');
INSERT INTO epever_descr VALUES ('h6', 'config', 'Enable load test mode. 1 enable, 0 disable (normal)');

INSERT INTO epever_descr VALUES ('d6', 'daily', 'consumed energy this month, 00:00 clear on the first day of month');
INSERT INTO epever_descr VALUES ('d8', 'daily', 'consumed energy this year, 00:00 clear on 1, Jan');
INSERT INTO epever_descr VALUES ('d14', 'daily', 'generated energy this month, 00:00 clear on first day of month');
INSERT INTO epever_descr VALUES ('d16', 'daily', 'generated energy this year, 00:00 clear on 1, Jan');
INSERT INTO epever_descr VALUES ('e20', 'daily', 'real time clock sec,min,hour,day,month,year;
D7-0 Sec, D15-8 Min.
(Year, Month, Day, Hour, Min, Sec.
should be written simultaneously)');

