#!/usr/bin/env python3

# Script to read Helium fill level from ISS RS232 port
# Liam Gaffney (liam.gaffney@cern.ch) - 22/03/2018
# Joonas Konki (joonas.konki@cern.ch) - 23/03/2018

import serial
import He
import re
from datetime import datetime
import time
import requests
from serial.tools import list_ports

# Serial number identifier of the FTDI USB-to-serial converter
# connected to the power supply to read the He fill level
USB_SERIAL_NO = 'FT1UVP3B'

HTTP_TIMEOUT = 10

def set_level(temp):
	f = open("/home/pi/influx_scripts/He.py","w")
	f.write("Level = " + str(temp))
	f.close()

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

# Find the address of the USB-to-serial converter
ports = list_ports.comports()
myport = ''
for port in ports:
	if USB_SERIAL_NO == port.serial_number:
		myport = port.device
		break

if 0 == len(myport): # port not found
	exit(1)

ser = serial.Serial( port=myport, baudrate=9600, timeout=5 )
reading = ser.read(size=1024)

# If it fails to read anything after the timeout, exit
if not len(reading):
  ser.close()

decoded_reading = reading.decode('cp1252')
escaped_reading = escape_ansi(decoded_reading)
fill_float = 0.0
pattern = re.match(r'.*FF\s*([\d\s]+.\d)\s*\%\sHe.*', escaped_reading, re.IGNORECASE)

if pattern is not None:
  fill_float = float( pattern.group(1).replace(' ','') )
  #print(str(datetime.now()) + ' fill level = ' + str(fill_float) + ' %')

  if (fill_float+0.05 < float(He.Level)) or (fill_float-0.05 > float(He.Level)):

    # Post to InfluxDB, only if the pattern was found
    payload = 'level,mode=rs232 value=' + str(fill_float)
    r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=he', data=payload, auth=("admin","issmonitor"), verify=False, timeout=HTTP_TIMEOUT )
    #print(r.text)
    set_level(fill_float)

ser.close()
