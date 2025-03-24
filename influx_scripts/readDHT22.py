#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code to read the DHT22 (temp and humidity) sensor and send the data influx
"""

# Ben Jones - University of Liverpool (sgbjone3@liverpool.ac.uk)
# *Code was adapted from Liam Gaffney

import logging
import pigpio
import DHT22
import time
import sys
import math
import requests

# Repetition time between measurements in secs
LOCATION = "vacuum_rack"

#Time between measurements
REP_TIME = 120
HTTP_TIMEOUT=10

# GPIO pin number of relay and sensor - BCM numbering
SENSOR_BCM = 22

# Logger setup
lgr = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def dewpoint(temp, humi):
    """
    Calculate the dew point temperature from temperature and humidity using the Magnus approximation
    """
    b = 17.625
    c = 243.04
    gamma = math.log(humi / 100.0) + ((b * temp) / (c + temp)) 
    return (c * gamma) / (b - gamma)

# Function to read sensor data
def read_sensor_data(sensor):
    ntries = 0
    temp = -999.0
    humi = -999.0
    err_count = sensor.missing_message()
    err_count_prev = int(err_count) - 1

    while int(err_count_prev) < int(err_count) and int(ntries) < 5:

        try:
            lgr.debug("Triggering the sensor")
            sensor.trigger()
            time.sleep(2.2)
        except Exception as e:
            lgr.error("Problem triggering the sensor: {}".format(e))

        try:
            temp = sensor.temperature()
            lgr.debug("Temperature: {}".format(temp))
        except Exception as e:
            lgr.error("Could not read temperature: {}".format(e))

        try:
            humi = sensor.humidity()
            lgr.debug("Humidity: {}".format(humi))
        except Exception as e:
            lgr.error("Could not read humidity: {}".format(e))

        ntries += 1
        err_count_prev = err_count
        err_count = int(sensor.missing_message())

    return float(temp), float(humi)

# Connect to the pigpio daemon
try:
    lgr.debug("Connecting to the pigpio daemon")
    pi = pigpio.pi()
except Exception as e:
    lgr.error("Couldn't connect to the pigpio daemon: {}".format(e))
    sys.exit(1)

# Initialize the sensor
try:
    lgr.debug("Getting sensor on pin {}".format(SENSOR_BCM))
    sensor = DHT22.sensor(pi, SENSOR_BCM)
except Exception as e:
    lgr.error("Could not get sensor on pin {}: {}".format(SENSOR_BCM,e))
    sys.exit(1)

# Main loop to read sensor data and send to InfluxDB
next_reading = time.time()
while True:
    temp, humi = read_sensor_data(sensor)
    next_reading += REP_TIME

    # Calculate dew point
    dp = dewpoint(temp, humi)

    payload = ''

    if temp > -50.0 and humi > -50.0:

        payload += "dh22,location=" + LOCATION + " temperature=" + str(temp) + ",humidity=" + str(humi) + ",dewpoint=" + str(dp)

        # Send the payload to InfluxDB
        try:
            r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=temp', auth=('admin','issmonitor'), data=payload, verify=False, timeout=HTTP_TIMEOUT)
        except Exception:
            pass

    waiting = float(next_reading - time.time())
    if waiting < 10.0:
        waiting = 10.0
    time.sleep(waiting)

sensor.cancel()
pi.stop()
