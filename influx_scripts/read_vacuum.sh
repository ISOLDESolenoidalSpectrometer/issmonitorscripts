#!/bin/bash

LOGFILE=/home/pi/monitor_data/pressure.log
LOGFILE2=/home/pi/monitor_data/pressure.log~
LOCKFILE=/home/pi/monitor_data/.pressure.lock
NUM=10080 # Number of minutes in a week

# Get lockfile

# Get reading from gauge via serial port
#stty 9600 -F /dev/ttyUSB0
#echo -e "COM" > /dev/ttyUSB0
read -t 10 line < $VACUUMPORT
read -t 10 line < $VACUUMPORT

if [ "foo$line" = "foo" ] ; then line="1000,1000,1000,1000,1000,ERROR" ; fi

# Get timestamp
ts=$(date +%s)
full="$(date +'%b %d %02H:%02M:%02S %Y')"

# Extract pressure
pressure1=$(echo $line|cut -d, -f2)
pressure2=$(echo $line|cut -d, -f4)

# Generate truncated file
tail -n $NUM $LOGFILE > $LOGFILE2

# Add line to logfile
printf "%s %s     %s   %s\n" "$ts" "$pressure1" "pressure2" "$full" "$line" >> $LOGFILE2
mv -f $LOGFILE2 $LOGFILE

# Trim whitespace from pressure values
pida1="$(echo -e "${pressure1}" | tr -d '[:space:]')"
pida2="$(echo -e "${pressure2}" | tr -d '[:space:]')"

# Trim leading + from pressure values
pidb1="${pida1:1}"
pidb2="${pida2:1}"


# Export value to InfluxDB
curl -s -k -i -XPOST 'https://dbod-iss.cern.ch:8080/write?db=vacuum' \
-u admin:issmonitor \
--data-binary "pressure,gauge=upstream value=$pidb1
pressure,gauge=downstream value=$pidb2" >> /dev/null

# Remove lockfile

