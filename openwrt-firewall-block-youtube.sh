#! /bin/sh
# save it into /usr/lib/scripts/firewall.sh
# and add into scheduled tasks as
# */5 * * * * /usr/lib/scripts/firewall.sh

hour=`date +%H`
minute=`date +%M`

echo "hour=$hour"
echo "minute=$minute"

status_file=/tmp/firewall_status

blocked_pattern="youtubei.googleapis.com googlevideo.com ytimg-edge-static.l.google.com i.ytimg.com youtube-ui.l.google.com www.youtube.com googleapis.l.google.com youtubei.googleapis.com video-stats.l.google.com ytimg-edge-static.l.google.com"

enable_firewall() {
    echo "Enabling firewall"
    for chain in INPUT FORWARD OUTPUT
        do
        count=1
        for proto in tcp udp
            do
                for blocked in $blocked_pattern
                    do
                    echo iptables -I $chain $count -p $proto -m string --algo bm --string "$blocked" -j DROP
                    iptables -I $chain $count -p $proto -m string --algo bm --string "$blocked" -j DROP
                    count=`expr $count + 1`
                done
        done
        echo iptables -I $chain $count -p udp --sport 443 -j DROP
        iptables -I $chain $count -p udp --sport 443 -j DROP
        count=`expr $count + 1`
        echo iptables -I $chain $count -p udp --dport 443 -j DROP
        iptables -I $chain $count -p udp --dport 443 -j DROP
        count=`expr $count + 1`
    done
}

disable_firewall() {
    echo "Disabling firewall"
    for chain in INPUT FORWARD OUTPUT
        do
        for proto in tcp udp
            do
                for blocked in $blocked_pattern
                    do
                    echo iptables -D $chain -p $proto -m string --algo bm --string "$blocked" -j DROP
                    iptables -D $chain -p $proto -m string --algo bm --string "$blocked" -j DROP
                done
        done
        echo iptables -D $chain -p udp --sport 443 -j DROP
        iptables -D $chain -p udp --sport 443 -j DROP
        echo iptables -D $chain -p udp --dport 443 -j DROP
        iptables -D $chain -p udp --dport 443 -j DROP
    done
}

case $1 in
    start) enable_firewall
           echo -n "enabled" > $status_file
           exit 0;;
    stop) disable_firewall
          echo -n "disabled" > $status_file
          exit 0;;
esac

# possible status
# enabled|disabled

# start
# from 7:55-09:59
time_status=disabled
if [[ $hour -ge 7 && $hour -lt 10 ]]; then
    time_status=enabled
    if [[ $hour -eq 7 ]]; then
        if [[ $minute -lt 55 ]]; then
            time_status=disabled
        else
            time_status=enabled
        fi
    fi
fi

# from 12:00-17:59
if [[ $hour -ge 12 && $hour -lt 18 ]]; then
    time_status=enabled
fi
# from 20:00-21:59
if [[ $hour -ge 19 && $hour -lt 22 ]]; then
    time_status=enabled
fi
echo "time_status=$time_status"

current_status=
if [[ -f "$status_file" ]]; then
    current_status=`cat $status_file`
fi

if [[ $current_status = $time_status ]]; then
    echo "nothing to do"
else
    if [[ $time_status = "enabled" ]];then
        echo "loading firewall rules"
        enable_firewall
    fi
    if [[ $time_status = "disabled" ]];then
        echo "removing firewall rules"
        disable_firewall
    fi
    echo -n $time_status > $status_file
fi
