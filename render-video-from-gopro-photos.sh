#! /usr/bin/env bash

__version__="1.0.1"

die() {
  echo "$1" >&2
  exit 1
}

generate_sequential_images() {
  counter=0
  for img in G[0-9]*.JPG
  do
    serial=$(printf "%06d" $counter)
    new_name="G${serial}.JPG"
    counter=$(expr $counter + 1)
    if [ -f "$new_name" ]; then
      echo "$new_name already exists"
      continue
    fi
    echo "$img => $new_name"
    mv $img $new_name
  done
}

render_video() {

  case $(uname -s) in
    Linux)
      echo "Merging images into single video file: output.mp4"
      rm -f output.mp4
      ffmpeg -hwaccel cuda -hwaccel_output_format cuda -r 1 -i G%06d.JPG -c:v h264_nvenc -b:v 5M -pix_fmt cuda output.mp4 || \
        die "Failed to render output.mp4"
      echo "Resizing video to 1920x1440: output_1920x1440.mp4"
      rm -f output_1920x1440.mp4
      ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i output.mp4 -c:v h264_nvenc -vf scale=1920:1440 -c:a copy output_1920x1440.mp4 || \
        die "Failed to render output_1920x1440.mp4"
      echo "Cropping file video as 1080p: output_1080p.mp4"
      rm -f output_1080p.mp4
      ffmpeg -hwaccel cuda -i output_1920x1440.mp4 -c:v h264_nvenc -vf "crop=1920:1080:0:180" output_1080p.mp4 || \
        die "Failed to render output_1080p.mp4"
      ;;
    Darwin) 
      echo "Merging images into single video file: output.mp4"
      die "Failed to render output.mp4"
      echo "Resizing video to 1920x1440: output_1920x1440.mp4"
      ffmpeg -hwaccel auto -i output.mp4 -c:v h264_videotoolbox -q:v 90 -vf scale=1920:1440 -c:a copy output_1920x1440.mp4
      echo "Cropping file video as 1080p: output_1080p.mp4"
      ffmpeg -hwaccel auto -i output_1920x1440.mp4 -c:v h264_videotoolbox -q:v 90 -vf "crop=1920:1080:0:180" output_1080p.mp4
  esac
}

case $1 in
  "--help")
  echo "Usage: $0 [--help|--skip-images|--version]"
  exit 0
  ;;
"--version")
  echo "version: $__version__"
  exit 0
  ;;
"--skip-images") set_skip_image=1
  ;;
esac

if [ $set_skip_image -ne 1 ]; then
  generate_sequential_images
fi

render_video
