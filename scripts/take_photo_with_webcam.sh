#!/bin/bash

# VARIABLES
WEBCAM_LOCATION="/dev/video0"
RESOLUTION="2304x1536"
INPUT_FORMAT="yuyv422"
OUTPUT_DIRECTORY="/home/pi/webcam"

# COMMAND
ffmpeg -y -f v4l2 -input_format ${INPUT_FORMAT} -video_size ${RESOLUTION} -i ${WEBCAM_LOCATION} -vf normalize -vframes 1 ${OUTPUT_DIRECTORY}/$(date +%Y%m%d_%H%M).jpg 2>&1 >/dev/null
