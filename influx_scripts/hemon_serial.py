#!/usr/bin/env python3

# Script to read Helium fill level from ISS RS232 port
# Liam Gaffney (liam.gaffney@cern.ch) - 22/03/2018
# Joonas Konki (joonas.konki@cern.ch) - 23/03/2018

import serial
import re
from datetime import datetime
import time
import requests

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

ser = serial.Serial( port='/dev/ttyUSB1', baudrate=9600, timeout=10 )
reading = ser.read(size=1024)

# If it fails to read anything after the timeout, try another serial port
if not len(reading):
  ser.close()
  ser = serial.Serial( port='/dev/ttyUSB0', baudrate=9600, timeout=10)
  reading = ser.read(size=1024)

# If it fails to read from the second serial port, exit here.
if not len(reading):
  exit(1)

decoded_reading = reading.decode('cp1252')
escaped_reading = escape_ansi(decoded_reading)
fill_float = 0.0
pattern = re.match(r'.*FF\s*([\d\s]+.\d)\s*\%\sHe.*', escaped_reading, re.IGNORECASE)

if pattern is not None:
  fill_float = float( pattern.group(1).replace(' ','') )
  #print(str(datetime.now()) + ' fill level = ' + str(fill_float) + ' %')
  
  # Post to InfluxDB, only if the pattern was found
  payload = 'level,mode=rs232 value=' + str(fill_float)
  r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=he', data=payload, auth=("admin","issmonitor"), verify=False )
  #print(r.text)

ser.close()
