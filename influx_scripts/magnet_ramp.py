#!/usr/bin/env python3

import serial
import re
import time
import requests
import datetime
import urllib3

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

ser = serial.Serial( port='/dev/ttyUSB0', baudrate=9600, timeout=10 )
file = open('output2.txt','w')

while(True):
	time.sleep(5)
	#reading = ser.read(size=1024)
	reading = ser.read(size=2048)
	decoded_reading = reading.decode('cp1252')
	escaped_reading = escape_ansi(decoded_reading)
	print('Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
	#print('decoded------')
	#print(decoded_reading)
	print('escaped-----')
	print(escaped_reading)
	print('-----')
	file.write('Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
	#file.write('decoded------')
	#file.write(decoded_reading)
	file.write('\nescaped-----\n')
	file.write(escaped_reading)
	file.write('\n')
	file.write('-----\n')
	#fill_float = 0.0
	#pattern = re.match(r'.*FF\s*([\d\s]+.\d)\s*\%\sHe.*', escaped_reading, re.IGNORECASE)

ser.close()
file.close()
