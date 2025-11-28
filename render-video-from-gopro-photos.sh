#! /usr/bin/env bash

__version__="1.1.1"

die() {
  echo "$1" >&2
  exit 1
}

## src: https://github.com/bahamas10/ysap/blob/main/code/2025-08-21-progress-bar/progress-bar
BATCHSIZE=1
BAR_CHAR='▌'
EMPTY_CHAR=' '

NVIDIA_GPU=true
SPEED_FRAMES=8

shopt -s globstar nullglob checkwinsize

progress-bar() {
	local current=$1
	local len=$2
  local title=$3

	local perc_done=$((current * 100 / len))

	local suffix=" $current/$len ($perc_done%) $title"

	local length=$((COLUMNS - ${#suffix} - 2))
	local num_bars=$((perc_done * length / 100))

	local i
	local s='['
	for ((i = 0; i < num_bars; i++)); do
		s+=$BAR_CHAR
	done
	for ((i = num_bars; i < length; i++)); do
		s+=$EMPTY_CHAR
	done
	s+=']'
	s+=$suffix

	printf '\e7' # save the cursor location
	  printf '\e[%d;%dH' "$LINES" 0 # move cursor to the bottom line
	  printf '\e[0K' # clear the line
	  printf '%s' "$s" # print the progress bar
	printf '\e8' # restore the cursor location
}

init-term() {
  shopt -s globstar nullglob checkwinsize
  # this line is to ensure LINES and COLUMNS are set
  (:)
	printf '\n' # ensure we have space for the scrollbar
	  printf '\e7' # save the cursor location
	    printf '\e[%d;%dr' 0 "$((LINES - 1))" # set the scrollable region (margin)
	  printf '\e8' # restore the cursor location
	printf '\e[1A' # move cursor up
}

deinit-term() {
  shopt -s globstar nullglob checkwinsize
  # this line is to ensure LINES and COLUMNS are set
  (:)
	printf '\e7' # save the cursor location
	  printf '\e[%d;%dr' 0 "$LINES" # reset the scrollable region (margin)
	  printf '\e[%d;%dH' "$LINES" 0 # move cursor to the bottom line
	  printf '\e[0K' # clear the line
	printf '\e8' # reset the cursor location
}

generate_sequential_images() { 
  init-term
  shopt -s globstar nullglob checkwinsize
  # this line is to ensure LINES and COLUMNS are set
  (:)
  files=(*.JPG)
  sizeof=${#files[@]}
  for ((counter=0; counter < sizeof; counter += 1))
  do
    serial=$(printf "%06d" $counter)
    new_name="G${serial}.JPG"
    filename="${files[@]:counter:1}"
    progress-bar "$((counter+1))" "$sizeof" "$filename => $new_name"
    if [ -f "$new_name" ]; then
      continue
    fi
      mv $filename $new_name
  done
  progress-bar $sizeof $sizeof
  echo
  deinit-term
}

speed_rate() {
  python3 -c "print(1./$SPEED_FRAMES)"
}

render_video_nvidia() {
  echo "Merging images into single video file: output.mp4"
  rm -f output.mp4
  ffmpeg -hwaccel cuda -hwaccel_output_format cuda -r 1 -i G%06d.JPG -c:v h264_nvenc -b:v 5M -pix_fmt cuda output.mp4 || \
    render_video_cpu

  echo "Resizing video to 1920x1440: output_1920x1440.mp4"
  rm -f output_1920x1440.mp4
  ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i output.mp4 -c:v h264_nvenc -vf scale=1920:1440 -c:a copy output_1920x1440.mp4 || \
    die "Failed to render output_1920x1440.mp4"

  echo "Cropping file video as 1080p: output_1080p.mp4"
  rm -f output_1080p.mp4
  ffmpeg -hwaccel cuda -i output_1920x1440.mp4 -c:v h264_nvenc -vf "crop=1920:1080:0:180" output_1080p.mp4 || \
    die "Failed to render output_1080p.mp4"

  echo "Creating ${SPEED_FRAMES}x speed video: output_1080p_${SPEED_FRAMES}x.mp4"
  rm -f output_1080p_${SPEED_FRAMES}x.mp4
  ffmpeg -hwaccel cuda -itsscale $speed_rate -i output_1080p.mp4 -c copy output_1080p_${SPEED_FRAMES}x.mp4 || \
    die "Failed to render ${SPEED_FRAMES}x fast on output_1080p_${SPEED_FRAMES}x.mp4"
  }

render_video_macos() {
  echo "Merging images into single video file: output.mp4"
  rm -f output.mp4
  ffmpeg -hwaccel auto -r 1 -i G%06d.JPG -c:v h264_videotoolbox -b:v 5M output.mp4 || \
    die "Failed to render output.mp4"

  echo "Resizing video to 1920x1440: output_1920x1440.mp4"
  rm -f output_1920x1440.mp4
  ffmpeg -hwaccel auto -i output.mp4 -c:v h264_videotoolbox -q:v 90 -vf scale=1920:1440 -c:a copy output_1920x1440.mp4 || \
    die "Failed to resized to 1920x1440"

  echo "Cropping file video as 1080p: output_1080p.mp4"
  rm -f output_1080p.mp4
  ffmpeg -hwaccel auto -i output_1920x1440.mp4 -c:v h264_videotoolbox -q:v 90 -vf "crop=1920:1080:0:180" output_1080p.mp4 || \
    die "Failed to crop video to 1080p"
}


render_video_cpu() {
  echo "Merging images into single video file: output.mp4"
  rm -f output.mp4
  ffmpeg -r 1 -i G%06d.JPG -c:v h264 -b:v 5M output.mp4 || \
    die "Failed to render output.mp4"

  echo "Resizing video to 1920x1440: output_1920x1440.mp4"
  rm -f output_1920x1440.mp4
  ffmpeg -i output.mp4 -c:v h264 -vf scale=1920:1440 -c:a copy output_1920x1440.mp4 || \
    die "Failed to render output_1920x1440.mp4"

  echo "Cropping file video as 1080p: output_1080p.mp4"
  rm -f output_1080p.mp4
  ffmpeg -i output_1920x1440.mp4 -c:v h264 -vf "crop=1920:1080:0:180" output_1080p.mp4 || \
    die "Failed to render output_1080p.mp4"

  echo "Creating ${SPEED_FRAMES}x speed video: output_1080p_${SPEED_FRAMES}x.mp4"
  rm -f output_1080p_${SPEED_FRAMES}x.mp4
  ffmpeg -itsscale $speed_rate -i output_1080p.mp4 -c copy output_1080p_${SPEED_FRAMES}x.mp4 || \
    die "Failed to render ${SPEED_FRAMES}x fast on output_1080p_${SPEED_FRAMES}x.mp4"
}

show_help() {
  cat <<EOF
Usage: $0 [--help] [--skip-images] [--version] [--enable-nvidia|--disable-nvidia] [--speed-frame]
 --help:           display this help
 --skip-images:    don't process images (probably because it was done before)
 --version:        the current version
 --enable-nvidia:  enable rendering on NVIDIA (default is on)
 --disable-nvidia: disable rendering on NVIDIA and run on CPU instead
 --speed-frames:   the nr of frames per second to be render at the end (default=$SPEED_FRAMES)
EOF
}

trap deinit-term exit
trap init-term winch

set_skip_image=0

options=$(getopt -l "help,version,skip-images,disable-nvidia,enable-nvidia,speed-frames:" --options "" --name $(basename $0) -- "$@")
eval set -- $options

while true; do
  case $1 in
    "--help")
      show_help
      exit 0
      ;;
    "--version")
      echo "version: $__version__"
      exit 0
      ;;
    "--skip-images") set_skip_image=1
      shift
      ;;
    "--enable-nvidia") NVIDIA_GPU=true
      shift
      ;;
    "--disable-nvidia") NVIDIA_GPU=false
      shift
      ;;
    "--speed-frames") SPEED_FRAMES=$2
      shift 2
      ;;
    --) shift; break;;
  esac
done

if [ $set_skip_image -ne 1 ]; then
  generate_sequential_images
fi

case $(uname -s) in
  Linux) 
    if [ "$NVIDIA_GPU" == false ]; then
      render_video_cpu
    else
      render_video_nvidia
    fi
    ;;
  Darwin) render_video_macos;;
  *) echo "Unsuported operating sistem"
     exit 1
     ;;
 esac
