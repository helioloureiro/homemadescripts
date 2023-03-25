#! /bin/bash

MOUSE_PRODUCT="G203 Prodigy Gaming Mouse"
#MOUSE_PRODUCT="USB2.0 Hub"

die() {
  echo "$@ " >&2
  exit 1
}

if [ $(id -u) -ne 0 ]; then
  die "you must run this script as root"
fi

cd /sys/bus/usb/devices || \
  die "It seems /sys interface isn't available."

echo "Detecting mouse:"
mouse_id=""
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
  else
    echo $product
  fi
done

if [ -z "$mouse_id" ]; then
  die "device not foud"
fi

echo "Restarting $mouse_id ($MOUSE_PRODUCT)"
echo " * unbinding"
echo "$mouse_id" > /sys/bus/usb/drivers/usb/unbind
sleep 0.5
echo " * binding"
echo "$mouse_id" > /sys/bus/usb/drivers/usb/bind

