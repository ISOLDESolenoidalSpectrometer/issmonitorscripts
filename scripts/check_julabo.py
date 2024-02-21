#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Watchdog script to check the status of the Julabo cooler
# Run as a cronjob. Sends emails when the power is off or has just been restored.
#
# 20190719 - Joonas Konki


from julabolib import julabolib
from serial.tools import list_ports
import subprocess
import requests

HTTP_TIMEOUT = 5


USB_SERIAL_NO = 'FT1UVQPS'

#Find the address of the USB-to-serial converter
ports = list_ports.comports()
myport = ''
for port in ports:
	if USB_SERIAL_NO == port.serial_number:
		myport = port.device
		break

if 0 == len(myport): # port not found
	print("USB-to-serial converter not found")
	exit(1)

mychiller = julabolib.JULABO(myport, baud=4800)

actual_status = mychiller.get_power()
if len(actual_status) > 0:
	actual_status = actual_status[:1]
if '' == actual_status:
	actual_status = '2'

set_temp = mychiller.get_work_temperature()
cur_temp = mychiller.get_temperature()
mychiller.close()

# Post to InfluxDB
if int(actual_status) < 2:
	payload = 'powerstatus,device=chiller value=' + str(actual_status)
	payload += '\ntemps,device=chiller,mode=read value=' + ('%.2f' % cur_temp)
	payload += '\ntemps,device=chiller,mode=set value=' + ('%.2f' % set_temp)
	try:
		r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=he', data=payload, auth=("admin","issmonitor"), verify=False, timeout=HTTP_TIMEOUT )
	except Exception:
		pass


# Check from file if the compressor was already OFF previously to avoid sending multiple email alerts
last_status = '1'
filename = '/home/pi/scripts/last_status_julabo.txt'
try:
        with open(filename,'r') as f:
                last_status = f.read(1)
                f.close()
except FileNotFoundError:
        pass

f = open(filename,'w+')
f.write(actual_status)
f.close()

if last_status != actual_status: # Status has changed! Send email alert!
	status_str = 'OFF'
	if '1' == actual_status:
		status_str = 'ON'
	if '2' == actual_status:
		status_str = 'NORESPONSE'

	script_output = subprocess.call(['/home/pi/scripts/send_alert_email.sh', 'Chiller for compressor (large Julabo)', status_str] )

