# -*- coding: utf-8 -*-
"""
A library for communicating with Leybold COOLVAC 6000 cryopump
using the serial RS232 interface

Protocol data format is 9600 baud 7E1 (7 bit, even parity, 1 stop bit)
Handshake is not required, therefore XON/XOFF is false.
"""
__author__ = "Liam Gaffney"
__license__ = "MIT, see LICENSE for more details"
__copyright__ = "2025 Liam Gaffney"

import logging
import serial
import time
import decimal

# ASCII start and end characters
START_CHR  = '\x24' # the dollar symbol ($) is always the first byte
END_CHR    = '\x0D' # end character for the message, a carriage return

# Pump address - bytes 2-4 are the pump address in format Pnn,
# where nn is the address setting on the CoolDrive
PUMP_ADDR = 'P01'

# Interpretation of the status double word response from the unit, "stat" command
# Each bit is equal to 1 if the following is true:
STATUS_BITS = {
        0 : 'reserved',
        1 : 'reserved',
        2 : 'Cold head motor running',
        3 : 'Error',
        4 : 'Process: CoolDown',
        5 : 'Process: WarmUp',
        6 : 'reserved',
        7 : 'reserved',
        8 : 'reserved',
        9 : 'reserved',
        10 : 'Normal operation: Cryo Ready',
        11 : 'Pump is cold',
        12 : 'Power Reset',
        13 : 'Regeneration required',
        14 : 'Collective warning',
        15 : 'RSCON active',
        16 : 'Pump is warm',
        17 : 'Regeneration aborted',
        18 : 'Init executed',
        19 : 'Regeneration normal or purge',
        20 : 'Compressor required',
        21 : 'Compressor switched on',
        22 : 'Forevacuum required',
        23 : 'Forevacuum switched on',
        24 : 'Forevacuum valve open',
        25 : 'Query putge type',
        26 : 'Regeneration running',
        27 : 'High-vacuum valve open',
        28 : 'Operation Point 2',
        29 : 'Operation Point 3',
        30 : 'Service mode is active',
        31 : 'Critical gas operation active'
}

# TODO: Error numbers returned from the "en" command
ERROR_NUMS = {
		0 : 'No error',
		1 : 'Frequency converter of the cold head indicates an error'
}

# TODO: Warning numbers returned from the "wn" command
WARNING_NUMS = {
		0 : 'No warning',
		1 : 'Heating stage 1: temperature rises above a delta K, although this stage is not being driven',
		2 : 'Heating stage 2: temperature rises above a delta K, although this stage is not being driven'
}

# TODO: Program steps returned from the "s" command
PROG_STEPS = {
		0 : 'initial state: Starting status cryo warm',
		99 : 'initial state: Initial status init command was run or the network was down',
		1 : 'cryo check: Pump cold or warm?',
		2 : 'cleaning: Baking out the active charcoal',
		3 : 'cleaning: Baking out the active charcoal',
		4 : 'forevacuum needed: Requesting the backing pump',
		5 : 'roughing to pressure CH on: Pre-evacuation to P MIN CH ON',
		6 : 'roughing ended: End pre-evacuation',
		61 : 'roughing ended, forevacuum closed, compressor on: End pre-evacuation',
		7 : 'cryo ready: Pump cold and ready for process'
}

class COOLVAC():
	def __init__(self,port,baud=9600,pump_addr=PUMP_ADDR):
		self.port = port
		self.pump_addr = pump_addr
		self.ser = serial.Serial( port=self.port,
					  bytesize=serial.SEVENBITS,
					  parity=serial.PARITY_EVEN,
					  stopbits=serial.STOPBITS_ONE,
					  baudrate=baud,
					  xonxoff=False,
					  rtscts=False,
					  timeout=2 )

		logging.basicConfig(format='coolvaclib: %(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=logging.WARNING)
		#logging.basicConfig(format='coolvaclib: %(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=logging.DEBUG)
		logging.debug('Serial port ' + self.port + ' opened at speed ' + str(baud))

		time.sleep(0.2) # Wait 200 ms after opening the port before sending commands
		self.ser.flushOutput() # Flush the output buffer of the serial port before sending any new commands
		self.ser.flushInput() # Flush the input buffer of the serial port before sending any new commands

	def close(self):
		"""The function closes and releases the serial port connection attached to the unit.

		"""
		if self.ser != None :
			self.ser.close()
			
	def calculate_checksum(self, command=''):
		"""This function calculates the required checksum to go with the command
		
		"""
		if command == '':
			return ''
		hex_sum = 0
		for char in command: # Skip the first character
			hex_sum += ord(char)  # Get the ASCII value (which corresponds to hex)
		hex_mod = hex_sum % 256
		
		# Extract bit 6 and bit 7 (counting from 0, bit 6 is 0x40 and bit 7 is 0x80)
		bit_0 = hex_mod & 0x01
		bit_1 = (hex_mod & 0x02) >> 1
		bit_6 = (hex_mod & 0x40) >> 6
		bit_7 = (hex_mod & 0x80) >> 7
		
		# Perform XOR
		xor_0_6 = bit_0 ^ bit_6
		xor_1_7 = bit_1 ^ bit_7

		# Make the 6-bit value
		xor_6bit = (hex_mod & 0b111100) | (xor_0_6) | (xor_1_7 << 1)
		
		logging.debug('Checksum: ' + str(xor_6bit) + ' (' + chr(xor_6bit + 0x30) + ')')
		
		return chr(xor_6bit + 0x30)


	def send_command(self, command=''):
		"""The function sends a command to the unit and returns the response string.

		"""
		if command == '': return ''
		checksum = self.calculate_checksum(self.pump_addr + command)
		full_cmd = START_CHR + self.pump_addr + command + checksum + END_CHR
		self.ser.write( full_cmd.encode('ascii') )
		time.sleep(0.1)
		logging.debug('Command sent to the unit: ' + full_cmd)
		response = self.ser.readline().decode('ascii')
		clean_response = response.replace(START_CHR, '').replace(END_CHR,'') #strip out START_CHR and END_CHR
		logging.debug('Response from unit: ' + response)
		return clean_response # return response from the unit as string

	def flush_input_buffer(self):
		""" Flush the input buffer of the serial port.
		"""
		self.ser.flushInput()

	def flush_output_buffer(self):
		""" Flush the output buffer of the serial port.
		"""
		self.ser.flushOutput()

	def get_status(self):
		""" The function gets the full status message from the unit.

		"""
		response = self.send_command('s')
		return response

	def print_status(self):
		""" The function prints the interpreted full status message from the unit to the console.

		"""
		response = self.get_status()
		
		byteid = 0
		for char in response[2:]:
			for bit in range(4):
				statid = byteid*4 + bit
				if statid > 31:
					break
				bitval = (ord(char) >> bit) & 0x01
				print( STATUS_BITS[statid] + ' : ' + str(bitval) )
			byteid = byteid + 1

	def get_pressure(self):
		""" The function gets the pressure from the unit in mbar.

		"""
		response = self.send_command('p')
		pressure = decimal.Decimal( response[1:-1] )
		return float( pressure )
