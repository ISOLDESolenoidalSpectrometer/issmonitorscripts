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
GAUGE_NUMBERS = [1,2]
GAUGE_NAMES = ['upstream','downstream']
LINETERM = '\x0D'+'\x0A'
ENQ = '\x05'
SPEED=9600
#SPEED=115200
STATUS_DECODING = ['Measurement data okay',
	  	   'Underrange',
		   'Overrange',
                   'Sensor error',
                   'Sensor OFF',
                   'No sensor',
                   'Identification error' ]

def send_command(command):
	mg.write((command + LINETERM).encode('ascii') )
	ack = mg.readline()
	mg.write((ENQ).encode('ascii'))
	res = mg.readline().decode('ascii')
	return res


# Find out which serial port the Pfeiffer controller is connected to.
# ISS Pfeiffer controller has serial_number: AH05GWEL
myport = ''
ports = list_ports.comports()
for port in ports:
	if port.serial_number == PFEIFFER_SERIAL_NO:
		myport = port.device
		print("Pfeiffer unit found in serial port: " + str(myport))

if '' == myport:
	print("Pfeiffer unit not found with serial number " + str(PFEIFFER_SERIAL_NO))
	exit() # controller not found

# Readout pressure from gauge and store in variable

mg = serial.Serial(port=myport, baudrate=SPEED, timeout=1)
mg.flushInput()
mg.flushOutput()

# Read some information from the unit
result = send_command('PNR')
print('Firmware version: ' + result)

result = send_command('ERR')
print('Error status: ' + result)

result = send_command('SPS')
print('Setpoint status: ' + result)

result = send_command('TID')
print('Gauge identification: ' + result)

result = send_command('UNI')
print('Pressure unit: ' + result)



# Gauges
for i in range(len(GAUGE_NUMBERS)):
	print('Reading gauge number ' + str(GAUGE_NUMBERS[i]) )
	res = send_command( 'PR' + str(GAUGE_NUMBERS[i]) )
	print(res)
	t = res.split(',')
	print(t)
	res = t[1]
	status = t[0]
	status_int = int(status)
	print('Status:   ' + status + ' (' + STATUS_DECODING[status_int]  + ')' )
	print('Pressure: ' + res)
	if status in ['4', '5', '6']:
		print('Gauge error or turned OFF!')
		continue
	
	pressure = float(res[1:])
	print(pressure)


mg.close()


