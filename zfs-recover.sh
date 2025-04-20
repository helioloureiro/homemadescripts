#! /usr/bin/env bash
#
# https://gist.github.com/faustinoaq/d267102dd004651801c13fae9d7973ec
# https://toabctl.wordpress.com/2023/05/10/mounting-an-encrypted-zfs-filesystem/
# https://develmonk.com/2022/05/20/mount-ubuntu-22-04-zfs-partitions-using-live-iso-for-disaster-recovery/

case $1 in
  start)
    zpool import -f rpool
    zpool list
    cryptsetup open /dev/zvol/rpool/keystore rpool-keystore
    mkdir /mnt-keystore
    mount /dev/mapper/rpool-keystore /mnt-keystore
    ls /mnt-keystore
    cat /mnt-keystore/system.key | zfs load-key -L prompt rpool
    umount /mnt-keystore 
    cryptsetup close rpool-keystore
    zfs list
    zfs set mountpoint=/mnt rpool/ROOT/ubuntu_ni6nkv
    zfs mount rpool/ROOT/ubuntu_ni6nkv
    ls /mnt
    zpool import -N -R /mnt bpool
    zfs mount bpool/BOOT/ubuntu_ni6nkv
    ls /mnt/boot/
    mount /dev/nvme0n1p1 /mnt/boot/efi
    for i in proc dev sys dev/pts; do mount -v --bind /$i /mnt/$i; done
    ;;
  stop)
    for i in proc sys dev/pts dev; do unmount -v /mnt/$i; done
    unmount /mnt/boot/efi
    zfs unmount bpool/BOOT/ubuntu_ni6nkv
    zfs unmount rpool
    zfs set mountpoint=/ rpool/ROOT/ubuntu_ni6nkv
    zfs set mountpoint=/boot bpool
    ;;
  *) echo "Use: $0 [start|stop]"
    exit 1
    ;;
esac


