#! /bin/bash

MOUSE_PRODUCT="G203 Prodigy Gaming Mouse"
HUB_PRODUCT="USB2.0 Hub"

die() {
  echo "$@ " >&2
  exit 1
}

bind() {
  device=$1
  echo " * binding: $device"
  echo "$device" > /sys/bus/usb/drivers/usb/bind > /dev/null
  if [ $? -ne 0 ]; then
    echo "Failed to bind, trying again"
    sleep 0.5
    bind $device
  fi
}

unbind() {
  device=$1
  echo " * unbinding: $device"
  echo "$device" > /sys/bus/usb/drivers/usb/unbind > /dev/null
  if [ $? -ne 0 ]; then
    echo "Failed to bind, trying again"
    sleep 0.5
    unbind $device
  fi
}

if [ $(id -u) -ne 0 ]; then
  die "you must run this script as root"
fi

cd /sys/bus/usb/devices || \
  die "It seems /sys interface isn't available."

echo "Detecting mouse and hub:"
mouse_id=""
hub_id=""
for d in *
do
  if [ ! -f "$d/product" ]; then
    continue
  fi
  echo -n " * $d: "
  product=$(cat $d/product)

  if [ "$product" = "$MOUSE_PRODUCT" ]; then
    echo "$product (DEVICE FOUND)"
    mouse_id="$d"
  elif [ "$product" = "$HUB_PRODUCT" ]; then
    hub_id="$d"
  else
    echo $product
  fi
done


if [ -n "$hub_id" ]; then
  echo "Restarting $hub_id ($HUB_PRODUCT)"
  unbind "$hub_id"
  sleep 0.5
  bind "$hub_id"
fi

sleep 0.5

if [ -z "$mouse_id" ]; then
  die "device not foud"
fi

echo "Restarting $mouse_id ($MOUSE_PRODUCT)"
unbind "$mouse_id"
sleep 0.5
bind "$mouse_id"


