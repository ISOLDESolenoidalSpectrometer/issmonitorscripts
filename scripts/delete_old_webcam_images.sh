#!/bin/bash
IMAGE_DIRECTORY="/home/pi/webcam"
CUTOFF_DATE=$(date --date="$(date +%Y-%m-%d) -30 days" +%Y%m%d)

for file in $(find "${IMAGE_DIRECTORY}" -type f -name "20[2-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]*.jpg")
do
    # Extract date
    FILENAME=${file##*/}
    DATE_STRING=${FILENAME%%_*}
    if [[ $(($DATE_STRING)) -lt $(($CUTOFF_DATE)) ]]
    then
        rm $file
    fi
done
