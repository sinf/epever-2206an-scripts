
# Modbus-MQTT-SQL integration

This repository is a bag of scripts and hacks to make Epever's solar charge controller operable with MQTT, PostgreSQL and HomeAssistant and whatnot.  

# Epever 2206AN

No load, no PV, current 22-26 mA , 12.74 V -> 0.28 W idle  
Year 2K problem (only 2 digits for year in clock) xD  
Some registers always give error: E103, H2  

# The RS485 gadget

https://www.waveshare.com/product/rs485-to-eth-b.htm  

Factory default hardcoded IP = 192.168.1.254 , can be changed to DHCP via HTTP  
Not usable with modbus-over-tcp libraries because they send extra headers not needed in plain rs485 over tcp,
also not usable with modbus-over-serial libraries because they refuse to operate on a network socket.  

# Link dump

https://github.com/Chiumanfu/Solar-Pump-Controller/blob/master/ControllerProtocolV2.3.pdf  

https://github.com/rosswarren/epevermodbus.git  

https://github.com/sourceperl/pyModbusTCP.git  

https://github.com/martgras/esphome/tree/testing/esphome/components/modbus_controller/examples/epever  

https://www.epever.com/support/softwares/  

