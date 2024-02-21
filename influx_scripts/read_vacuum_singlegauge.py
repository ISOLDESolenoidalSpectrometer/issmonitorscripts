#!/usr/bin/env python3
import serial
import requests
import time
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

#PFEIFFER_SERIAL_NO = 'AH05GWEL'
DEVICE_PATH = '/dev/ttyUSB0'
#GAUGE_NUMBERS = [1,2]
#GAUGE_NAMES = ['upstream','downstream']
GAUGE_NAME = 'upstream'
LINETERM = '\x0D'+'\x0A'
ENQ = '\x05'
SPEED=9600
#SPEED=115200
HTTP_TIMEOUT = 10

# Find out which serial port the Pfeiffer controller is connected to.
# ISS Pfeiffer controller has serial_number: AH05GWEL
#myport = ''
#ports = list_ports.comports()
#for port in ports:
#	if port.serial_number == PFEIFFER_SERIAL_NO:
#		myport = port.device
#
#if '' == myport:
#	exit() # controller not found
myport = DEVICE_PATH

# Readout pressure from gauge and store in variable

mg = serial.Serial(port=myport, baudrate=SPEED, timeout=1)
mg.flushInput()
mg.flushOutput()

# Gauges
#for i in range(len(GAUGE_NUMBERS)):
mg.write(('PR1' + LINETERM).encode('ascii') )
ack = mg.readline()
mg.write((ENQ).encode('ascii'))
res = mg.readline().decode('ascii')
print(res)
t = res.split(',')
res = t[1]
status = t[0]
if '4' == status:
	exit()

pressure = float(res[1:])

# Push pressure value to influxdb for grafana
payload_p = 'pressure,gauge=' + GAUGE_NAME + ' value=' + ('%.9f' % pressure)
#payload_p = 'pressure,gauge=' + GAUGE_NAMES[i] + ' value=' + ('%.9f' % pressure)
#payload_s = '\nstatus,gauge=' + GAUGE_NAMES[i] + ' value=' + str(status)
payload_s = ',status=' + str(status)
payload = payload_p + payload_s
try:
	r = requests.post('https://dbod-iss.cern.ch:8080/write?db=vacuum', auth = ('admin', 'issmonitor'), data=payload, verify=False, timeout=HTTP_TIMEOUT)
except Exception:
	pass

mg.close()


