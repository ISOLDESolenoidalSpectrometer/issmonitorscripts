#!/bin/bash

# Read twice in case it is already in use by something else
#python ADC_test.py > tmp.txt
python /home/pi/influx_scripts/ADC_read.py > /home/pi/influx_scripts/adc_output.txt

# Get timestamp
ts=$(date +%s)
full="$(date +'%b %d %02H:%02M:%02S %Y')"

# array of voltages, temps and logfiles
declare -a voltage
declare -a temp
i=0

# read voltages
while read -r line;
do
    voltage[$i]=$( echo $line | cut -d' ' -f4 )
    temp[$i]=$( echo "(3.32862*l(2497410*e(-0.212736*(${voltage[$i]}*1000.-1083.46))+2268.07*e(-0.0113242*(${voltage[$i]}*1000.-1083.46))))" | bc -l )
    logfile=/home/pi/monitor_data/diode_${i}.log
    printf "%s\t%s\t%s\t%s\n" "$ts" "${voltage[$i]}" "${temp[$i]}" "$full" >> $logfile
    i=$((i+1))
done < "/home/pi/influx_scripts/adc_output.txt"

# send to influx
curl -s -k -i -XPOST 'https://dbod-iss.cern.ch:8080/write?db=temp' \
-u admin:issmonitor \
--data-binary "voltages,diode=a value=${voltage[2]}
voltages,diode=b value=${voltage[3]}
voltages,diode=c value=${voltage[4]}
voltages,diode=d value=${voltage[5]}
voltages,diode=e value=${voltage[6]}
voltages,diode=f value=${voltage[7]}
temps,diode=a value=${temp[2]}
temps,diode=b value=${temp[3]}
temps,diode=c value=${temp[4]}
temps,diode=d value=${temp[5]}
temps,diode=e value=${temp[6]}
temps,diode=f value=${temp[7]}"

