#!/usr/bin/python
#Sample Python program to test 8 analogue inputs on Custard Pi 3
#www.sf-innovations.co.uk
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(24, GPIO.OUT) #pin 24 is chip enable
GPIO.setup(23, GPIO.OUT) #pin 23 is clock
GPIO.setup(19, GPIO.OUT) #pin 19 is data out
GPIO.setup(21, GPIO.IN) #pin 21 is data in
#set pins to default state
GPIO.output(24, True)
GPIO.output(23, False)
GPIO.output(19, True)

f = open('hemon_out.txt','a')

#1st bit selects single/differential
#2nd bit channel address
#3rd bit channel address
#4th bit channel address
#5th bit 1 bit delay for data
#6th bit 1st null bit of data

word7 = [1 ,1, 1, 1, 0, 1, 1] #set channel 6
word6 = [1 ,1, 1, 1, 1, 1, 1] #set channel 7 

GPIO.output(24, False) #enable chip
imon=0  # clear variable
vfill=0 # clear variable

# clock out 7 bits to monitor channel
for x in range (0,7):
	GPIO.output(19, word7[x])
	time.sleep(0.01)
	GPIO.output(23, True)
	time.sleep(0.01)
	GPIO.output(23, False)

# clock in 11 bits of data
for x in range (0,12):
	GPIO.output(23,True) #set clock hi
	time.sleep(0.01)
	bit=GPIO.input(21) #read input
	time.sleep(0.01)
	GPIO.output(23,False) # set clock lo
	value=bit*2**(12-x-1) # work out value of this bit
        imon=imon+value       # add to previous total

text = 'adc value of imon = ' + str(imon) + '\n'
print text # print ADC value
f.write(text)

# test if current is on
if imon > 100:
        # clock out 7 bits to fill V channel
        for x in range (0,7):
                GPIO.output(19, word6[x])
                time.sleep(0.01)
                GPIO.output(23, True)
                time.sleep(0.01)
                GPIO.output(23, False)
        # clock in 11 bits of data
        for x in range (0,12):
                GPIO.output(23,True) #set clock hi
                time.sleep(0.01)
                bit=GPIO.input(21) #read input
                time.sleep(0.01)
                GPIO.output(23,False) # set clock lo
                value=bit*2**(12-x-1) # work out value of this bit
                vfill=vfill+value     # add to previous total

        text = 'adc value of vfill = ' + str(vfill) + '\n'
        print text # print ADC value
        f.write(text)
        
# print x, bit, value, anip
GPIO.output(24, True) #disable chip
#volt = vfill*2.5/4096 #use ref voltage of 2.5 to work out voltage
#print "fill voltage", y, ("%.4f" %round(volt,4)) #print to screen

GPIO.cleanup()
import sys
sys.exit()
#TO TEST
#Note: we use the terminology Channel 0 to 7. On the PCB they are marked as Channel 1 to 8.
#Connect Channels 0 to 7 to 2.5V and voltage should be 2.5V printed to screen
#Connect two equal resistors in series from 2.5V to 0V.
#Connect mid point of resistors to Channels 0 to 7 in turn
#Voltage should be 1.25V printed to screen
