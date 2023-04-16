#! /usr/bin/env bash

counter=0
for img in G*.JPG
do
  serial=$(printf "%04d" $counter)
  new_name="G${serial}.JPG"
  echo "$img => $new_name"
  mv $img $new_name
  counter=$((counter++))
done

ffmpeg -hwaccel cuda -hwaccel_output_format cuda -r 1 -i G%04d.JPG -c:v h264_nvenc -b:v 5M -pix_fmt cuda output.mp4
