#!/usr/bin/env python3

# Test programme to read the ADS1115 voltages connected to ISS magnet diodes
# Liam Gaffney (liam.gaffney@liverpool.ac.uk) - 04/03/2023

import RPi.GPIO as GPIO
import smbus
import cmd
import logging
import time
import requests
import math

# ADS1115 + hardware constants
I2C_BUS = 1
DEVICE_ADDRESS_0 = 0x48
DEVICE_ADDRESS_1 = 0x49
POINTER_CONVERSION = 0x0
POINTER_CONFIGURATION = 0x1
POINTER_LOW_THRESHOLD = 0x2
POINTER_HIGH_THRESHOLD = 0x3

RESET_ADDRESS = 0b0000000
RESET_COMMAND = 0b00000110

HTTP_TIMEOUT=10

# Time between measurements in seconds
MEASUREMENT_PERIOD=120

# Open I2C device
BUS = smbus.SMBus(I2C_BUS)
BUS.open(I2C_BUS)

# GPIO pin for board switch
SWITCHPIN = 4


def swap2Bytes(c):
    '''Revert Byte order for Words (2 Bytes, 16 Bit).'''
    return (c >> 8 | c << 8) & 0xFFFF


def prepareLEconf(BEconf):
    '''Prepare LittleEndian Byte pattern from BigEndian configuration string, with separators.'''
    c = int(BEconf.replace('-', ''), base=2)
    return swap2Bytes(c)


def LEtoBE(c):
    '''Little Endian to BigEndian conversion for signed 2Byte integers (2 complement).'''
    c = swap2Bytes(c)
    if (c >= 2 ** 15):
        c = c - 2 ** 16
    return c


def BEtoLE(c):
    '''BigEndian to LittleEndian conversion for signed 2 Byte integers (2 complement).'''
    if (c < 0):
        c = 2 ** 16 + c
    return swap2Bytes(c)


def resetChip():
    BUS.write_byte(RESET_ADDRESS, RESET_COMMAND)
    return


def measure(ch):
    '''One-shot, Read value from channel with wait time'''
    resetChip()

    # compare with configuration settings from ADS115 datasheet
    # start single conversion - channel+mode - 4.096V - single shot - 8SPS - X
    # - X - X - disable comparator
    if ch==0:
        conf = prepareLEconf('1-100-010-1-001-0-0-0-11') # ch0 board 0 single-ended
        address = DEVICE_ADDRESS_0
    elif ch==1:
        conf = prepareLEconf('1-101-010-1-001-0-0-0-11') # ch1 board 0 single-ended
        address = DEVICE_ADDRESS_0
    elif ch==2:
        conf = prepareLEconf('1-110-010-1-001-0-0-0-11') # ch2 board 0 single-ended
        address = DEVICE_ADDRESS_0
    elif ch==3:
        conf = prepareLEconf('1-111-010-1-001-0-0-0-11') # ch3 board 0 single-ended
        address = DEVICE_ADDRESS_0
    elif ch==4:
        conf = prepareLEconf('1-100-010-1-001-0-0-0-11') # ch0 board 1 single-ended
        address = DEVICE_ADDRESS_1
    elif ch==5:
        conf = prepareLEconf('1-101-010-1-001-0-0-0-11') # ch1 board 1 single-ended
        address = DEVICE_ADDRESS_1
    elif ch==6:
        conf = prepareLEconf('1-110-010-1-001-0-0-0-11') # ch2 board 1 single-ended
        address = DEVICE_ADDRESS_1
    elif ch==7:
        conf = prepareLEconf('1-111-010-1-001-0-0-0-11') # ch3 board 1 single-ended
        address = DEVICE_ADDRESS_1
    else:
        return 0

    BUS.write_word_data(address, POINTER_CONFIGURATION, conf)


    # long enough to be safe that data acquisition (conversion) has completed
    # may be calculated from data rate + some extra time for safety.
    # check accuracy in any case.
    time.sleep(0.2)
    value_raw = BUS.read_word_data(address, POINTER_CONVERSION)
    value = LEtoBE(value_raw)

    return value

def shutdown():
    GPIO.cleanup()
    BUS.close()
    pass

def temperature(v):
    temp = 2497410.0 * math.exp( -0.212736 * (v-1083.46) )
    temp = temp + 2268.07 * math.exp( -0.0113242 * (v-1083.46) )
    temp = 3.32862 * math.log( temp )
    return temp


############
# Main run #
############

# Use BCM GPIO references and setup switch pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCHPIN, GPIO.OUT, initial=GPIO.LOW)

# channel map for diode inputs
diode_map = ["d","c","b","a","e","f","g","h"]

# Loop for ever
try:
    while True:

        # First switch the board on
        GPIO.output(SWITCHPIN, GPIO.HIGH)

        # InfluxDB payload
        payload = ''

        # Loop over all channels
        for ch in range(0,6):

            # Get ADC value
            adc_value = measure(ch=ch)

            # Values are signed in a weird way
            if adc_value > 32767:
                adc_value = adc_value - 65536

            # Convert to voltage
            voltage = 2048.0 * adc_value / 32768.0

            # Print results
            #print( 'ch', ch, ' = ', voltage, ' mV' )

            # InfluxDB payload
            if ch != 0:
                payload += '\n'
            payload += 'voltages,diode=' + str(diode_map[ch]) + ' value=' + str( voltage*0.001 )
            payload += '\ntemps,diode=' + str(diode_map[ch]) + ' value=' + str( temperature(voltage) )

        # Send the payload to InfluxDB
        try:
            r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=temp', auth=('admin','issmonitor'), data=payload, verify=False, timeout=HTTP_TIMEOUT)
            #print(payload)
        except Exception:
            pass


        # Turn the board off
        GPIO.output(SWITCHPIN, GPIO.LOW)

        # Sleep for a while
        time.sleep(MEASUREMENT_PERIOD)

# Keyboard kill signal
except KeyboardInterrupt:
    shutdown()
    print("\nClosing and stopping")

# error capture
except:
    shutdown()
    print("An error occured")


