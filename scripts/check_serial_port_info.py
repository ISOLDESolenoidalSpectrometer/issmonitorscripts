#!/usr/bin/env python3
"""
	Print some information on the serial port interfaces.
	Try also command: 
		python3 -m serial.tools.list_ports -v

	FT1UVP3B : connected to the power supply He level readout
	FT1UVQPS : connected to the chiller (Julabo FL11006)
	FTXOBKUT : connected to the compressor (Coolpak 6000)
	
	20190123 - Joonas Konki
"""
from serial.tools import list_ports

ports = list_ports.comports()

for port in ports:
	print("\nFound unknown unit in port: " + str(port.device) )
	print("Manufacturer: %s" % port.manufacturer)
	print("Product: %s" % port.product)
	print("Serial number: %s" % port.serial_number)
	vidd = 0
	if port.vid is not None: vidd = int(port.vid)
	print("Vendor ID (VID): %s (0x%x)" % (vidd, vidd))
	pidd = 0
	if port.pid is not None: pidd = int(port.pid)
	print("Product ID (PID): %s (0x%x)" % (pidd, pidd))
	print("HWID: %s" % port.hwid)
	print("Location: %s" % port.location)
	print("Interface: %s" % port.interface)
	print("Description: %s" % port.description)


