#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Check the pressure on the CoolVac cryo pump and send to Grafana
#
# 20250320 - Liam Gaffney

from coolvaclib import coolvaclib
from serial.tools import list_ports
import subprocess
import requests

HTTP_TIMEOUT = 10
COOLVAC_SERIAL_NO = 'FT1UTHMW'
PUMP_ADDR = 'P01'

# Find out which serial port the USB-to-Serial converter
# of the compressor is connected to.
myport = ''
ports = list_ports.comports()
for port in ports:
	if COOLVAC_SERIAL_NO == port.serial_number:
		myport = port.device
		break

if 0 == len(myport): # port not found
	print("USB-to-serial converter not found")
	exit(1)

# Setup the connection
mycryo = coolvaclib.COOLVAC( port=myport, pump_addr=PUMP_ADDR )

# Get the pressure
pressure = mycryo.get_pressure()

# Close connection
mycryo.close()

# Post to InfluxDB
if pressure is not None:
	payload = 'pressure,gauge=cryo value=' + ('%.9f' % pressure)
	payload += ',status=0'
else:
	payload = 'pressure,gauge=cryo value=0.0,status=2'
	
try:
	r = requests.post('https://dbod-iss.cern.ch:8080/write?db=vacuum', auth = ('admin', 'issmonitor'), data=payload, verify=False, timeout=HTTP_TIMEOUT)
except Exception:
	pass
	
