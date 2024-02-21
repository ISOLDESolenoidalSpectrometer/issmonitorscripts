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

PFEIFFER_SERIAL_NO = 'AH05GWEL'
GAUGE_NUMBER = 1
GAUGE_NAME = 'upstream'
LINETERM = '\x0D'+'\x0A'
ENQ = '\x05'
SPEED=9600
#SPEED=115200

# Find out which serial port the Pfeiffer controller is connected to.
# ISS Pfeiffer controller has serial_number: AH05GWEL
myport = ''
ports = list_ports.comports()
for port in ports:
	if port.serial_number == PFEIFFER_SERIAL_NO:
		myport = port.device
		print("Pfeiffer unit found in serial port: " + str(myport))

if myport == '':
	print("Pfeiffer unit not found with serial number " + str(PFEIFFER_SERIAL_NO))
	exit() # controller not found

# Readout pressure from guage and store in variable

mg = serial.Serial(port=myport, baudrate=SPEED, timeout=1)
mg.flushInput()
mg.flushOutput()
mg.write(('PR' + str(GAUGE_NUMBER) + LINETERM).encode('ascii') )
ack = mg.readline()
mg.write((ENQ).encode('ascii'))
res = mg.readline().decode('ascii')
print(res)
t = res.split(',')
print(t)
res = t[1]
status = t[0]
print(status)
print(res)
pressure = float(res[1:])


mg.close()
#print(pressure)

