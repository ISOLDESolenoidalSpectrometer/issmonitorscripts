#!/usr/bin/env python3
import serial
import requests
import time
import re
from serial.tools import list_ports

#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#
# Disable warnings another way: (Not tested)
#     requests.packages.urllib3.disable_warnings()
#
# Or from urllib3 documentation:
#     import urllib3
#     urllib3.disable_warnings()
#

EDWARDS_SERIAL_NO = 'FT5Z6FCA'
GAUGE_NUMBERS = [1,2]
GAUGE_NAMES = ['mwpc','empty']
LINETERM = '\r'
ENQ = '?'
SPEED=9600
#SPEED=115200
HTTP_TIMEOUT = 10

# Find out which serial port the Edwards controller is connected to.
myport = ''
ports = list_ports.comports()
for port in ports:
	if port.serial_number == EDWARDS_SERIAL_NO:
		myport = port.device

if '' == myport:
	exit() # controller not found

# Readout pressure from gauge and store in variable

mg = serial.Serial(port=myport, baudrate=SPEED, timeout=1)
mg.flushInput()
mg.flushOutput()

# Gauges
for i in range(len(GAUGE_NUMBERS)):
	mg.write(('?GA' + str(GAUGE_NUMBERS[i]) + LINETERM).encode('ascii') )
	res = mg.readline().decode('ascii')
	pattern = re.match(r'(Err)(\d*)', res, re.IGNORECASE)
	if pattern is not None:
		pressure = 1010
		status = int(pattern.group(1))
	else:
		pressure = float(res.strip('\r'))
		status = 0

	# Push pressure value to influxdb for grafana
	payload_p = 'pressure,gauge=' + GAUGE_NAMES[i] + ' value=' + ('%.9f' % pressure)
	payload_s = ',status=' + str(status)
	payload = payload_p + payload_s
	try:
		r = requests.post('https://dbod-iss.cern.ch:8080/write?db=vacuum', auth = ('admin', 'issmonitor'), data=payload, verify=False, timeout=HTTP_TIMEOUT)
	except Exception:
		pass

mg.close()


