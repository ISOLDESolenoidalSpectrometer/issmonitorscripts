#!/usr/bin/env python3

# Script to read Helium fill level from ISS RS232 port
# Liam Gaffney (liam.gaffney@cern.ch) - 22/03/2018 

"""
   TODO: 
   - Insert code to send data to InfluxDB
   - Check the readout  and validity of the regular expressions in the code 
     when the magnet is ramping up and current is ON (JK)

"""

import serial
import re
import requests
import urllib3
import time
from serial.tools import list_ports

# Serial number identifier of the FTDI USB-to-serial converter
# connected to the power supply to read the He fill level
USB_SERIAL_NO = 'FT1UVP3B'
HTTP_TIMEOUT = 10

def escape_ansi(line):
	ansi_regex = r'\x1b(' \
             r'(\[\??\d+[hl])|' \
             r'([=<>a-kzNM78])|' \
             r'([\(\)][a-b0-2])|' \
             r'(\[\d{0,2}[ma-dgkjqi])|' \
             r'(\[\d+;\d+[hfy]?;?\d?m?)|' \
             r'(\[;?[hf])|' \
             r'(#[3-68])|' \
             r'([01356]n)|' \
             r'(O[mlnp-z]?)|' \
             r'(\/Z)|' \
             r'(\d+)|' \
             r'(\[\?\d;\d0c)|' \
             r'(\d;\dR))'
	ansi_escape = re.compile(ansi_regex, flags=re.IGNORECASE)
	return ansi_escape.sub('', line)

# urllib warnings
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# Find the address of the USB-to-serial converter
ports = list_ports.comports()
myport = ''
for port in ports:
	if USB_SERIAL_NO == port.serial_number:
		myport = port.device
		break

if 0 == len(myport): # port not found
	exit(1)

# Read serial
ser = serial.Serial( port=myport, baudrate=9600, timeout=5 )

# Keep running
while True:

	reading = ser.read(size=256)

	"""
	   Example byte string readout from the serial:
	   reading = b'\x1b[0m\x1b[1;1H\x1b[0;1;7m1\x1b[0m2\x1b[0;1;7m3\x1b[0m4\x1b[0m5\x1b[0m6\x1b[0m7\x1b[0m8\x1b[0;1m\x1b[13;21H000x   0.0 A\x1b[13;53H+000 +0.0 V'

	   Once escape characters are removed:

	   1234567800x   0.0 A+000 +0.0 V

	"""

	decoded_reading = reading.decode('ascii','ignore')
	escaped_reading = escape_ansi(decoded_reading)
	#print(escaped_reading) 

	payload = ''
	current_float = 0.0
	#currentpattern = re.match(r'.*00x\s*(\d+.\d+)\s*A.*', escaped_reading, re.IGNORECASE)
	currentpattern = re.match(r'.*x\s*(\d+.\d+)\s*A.*', escaped_reading, re.IGNORECASE)
	if currentpattern is not None: 
		current_float = float( currentpattern.group(1) )
		print('current = ' + str(current_float) + ' A')
		payload += 'magnet,measurement=current value=' + str(current_float) + '\n'

	voltage_float = 0.0
	voltagepattern = re.match(r'.*\+\s*([\+\-]?\d+.\d+)\s*V.*', escaped_reading, re.IGNORECASE)
	if voltagepattern is not None:
		voltage_float = float( voltagepattern.group(1) )
		print('voltage = ' + str(voltage_float) + ' V')
		payload += 'magnet,measurement=voltage value=' + str(voltage_float) + '\n'

	# send to influx
	try:
		r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=he', data=payload, auth=("admin","issmonitor"), verify=False, timeout=HTTP_TIMEOUT )
		#print(r)
	except:
		print("error")
		pass

	# wait before next reading
	time.sleep(2)

# Finish
ser.close()
