#! /bin/sh
# save it into /usr/lib/scripts/firewall.sh
# and add into scheduled tasks as
# */5 * * * * /usr/lib/scripts/firewall.sh
# requires: iptables-mod-filter bc
# to run as tests environment: env TEST_ENV=1 DEBUG=1 FAKE_TIME=20:00,Sun sh firewall.sh

#blocking times
# HH:MM start, HH:MM stop, weekday
rules="07:55,08:30,Mon"
rules="$rules 12:00,18:00,Mon"
rules="$rules 07:55,08:30,Tue"
rules="$rules 12:00,18:00,Tue"
rules="$rules 07:55,08:00,Wed"
rules="$rules 12:00,18:00,Wed"
rules="$rules 07:55,08:00,Thu"
rules="$rules 12:00,18:00,Thu"
rules="$rules 07:55,08:30,Fri"
rules="$rules 12:00,16:00,Fri"

die() {
    echo "$@"
    exit 1
}

debug() {
    test -z $DEBUG && return
    echo "$@"
}

check_dep() {
    # skip on tests environment
    test -z $TEST_ENV || return

    dep=$1
    opkg status $dep | grep -q Installed-Time
    if [ $? -ne 0 ]; then
        die "Missing $dep.  Install it running: opkg install $dep"
    fi
}



## Check module installation or fail
check_dep iptables-mod-filter
## Check bc or fail
check_dep bc

if [ -z $FAKE_TIME ]; then
    HOUR=$(date "+%H")
    MINUTE=$(date "+%M")
    WEEKDAY=$(date  "+%a")
else
    HOUR=$(echo $FAKE_TIME | cut -d, -f1 | cut -d: -f1)
    MINUTE=$(echo $FAKE_TIME | cut -d, -f1 | cut -d: -f2)
    WEEKDAY=$(echo $FAKE_TIME | cut -d, -f2)
fi

echo "Current time: hour=$HOUR minute=$MINUTE (weekday=$WEEKDAY)"
now=$( echo "$HOUR * 60 + $MINUTE" | bc)

status_file=/tmp/firewall_status.lck

blocked_pattern="youtubei.googleapis.com"
blocked_pattern="$blocked_pattern googlevideo.com"
blocked_pattern="$blocked_pattern ytimg-edge-static.l.google.com" 
blocked_pattern="$blocked_pattern i.ytimg.com" 
blocked_pattern="$blocked_pattern youtube-ui.l.google.com" 
blocked_pattern="$blocked_pattern www.youtube.com" 
blocked_pattern="$blocked_pattern googleapis.l.google.com" 
blocked_pattern="$blocked_pattern youtubei.googleapis.com" 
blocked_pattern="$blocked_pattern video-stats.l.google.com" 
blocked_pattern="$blocked_pattern ytimg-edge-static.l.google.com"
blocked_pattern="$blocked_pattern instagram.com"
blocked_pattern="$blocked_pattern facebook.com"

run_cmd() {
    command="$@"
    debug "$command"
    # don't run on test
    test -z $TEST_ENV || return
    eval $command
}

enable_firewall() {
    status=$(cat status_file)
    if [ "$status" = "manual_enabled" ]; then
        return
    fi
    if [ "$status" = "timetable_enabled" ]; then
        return
    fi
    echo "Enabling firewall"
    for chain in INPUT FORWARD OUTPUT
        do
        count=1
        for proto in tcp udp
            do
                for blocked in $blocked_pattern
                    do
                    cmd="iptables -I $chain $count -p $proto -m string --algo bm --string \"$blocked\" -j DROP"
                    run_cmd $cmd
                    count=$(expr $count + 1)
                done
        done
    done
}

disable_firewall() {
    status=$(cat status_file)
    if [ "$status" = "manual_disabled" ]; then
        return
    fi
    if [ "$status" = "timetable_disabled" ]; then
        return
    fi

    echo "Disabling firewall"
    for chain in INPUT FORWARD OUTPUT
    do
        for line in $(iptables -L $chain -n --line-numbers)
        do
            # check whether it starts with a number
            echo $line | grep -q "^[0-9]"
            if [ $? -ne 0 ]; then
                # next firewall line
                continue
            fi
            # check whether it has the term "STRING" on it
            echo $line | grep -qi string
            if [ $? -ne 0 ];then
                # next firewall line
                continue
            fi

            for blocked in $blocked_pattern
            do
                echo $line | grep -q $blocked
                if [ $? -eq 0 ];then
                    line_nr=$(echo $line | cut -d" " -f1 | sort -nr)
                    run_cmd "iptables -D $chain  $line_nr"
                    break
                fi
            done
        done
    done
}

get_status() {
    if [ ! -f $status_file ];then
        echo "Not running at this time."
        exit 0
    fi
    status=$(cat $status_file)
    echo "status: $status"
}


is_running_manual_mode() {
    if [ ! -f $status_file ];then 
        echo "no"
        return
    fi
    cat $status_file | grep -q "manual_"
    if [ $? -eq 0 ]; then
        echo "yes"
        return
    fi
    echo "no"
}

convert_minutes() {
    #format HH:MM
    timestamp=$1
    hour=$(echo $timestamp | cut -d: -f1)
    minute=$(echo $timestamp | cut -d: -f2)
    echo "$hour * 60 + $minute" | bc
}

check_running_manual_mode() {
    status=$(is_running_manual_mode)
    case $status in
        yes) die "manual lock in place - use \"reset\" to remove it" ;;
        no) ;;
        *) die "uknown error: $status"
    esac
}

check_firewall() {
    # expects [stop|start]
    action=$1

    check_running_manual_mode

    status=""
    test -f $status_file && status=$(cat $status_file)

    if [ "$action" = "stop" ] && [ "$status" = "timetable_disabled" ]; then
        echo "already disabled - nothing to be done"
        return
    fi

    if [ "$action" = "stop" ] && [ "$status" != "timetable_disabled" ]; then
        disable_firewall
        echo -n "timetable_disabled" > $status_file
        return
    fi

    if [ "$action" = "start" ] && [ "status" = "timetable_enabled" ]; then
        echo "already enabled - nothing to be done"
        return
    fi

    if [ "$action" = "start" ] && [ "status" != "timetable_enabled" ]; then
        enable_firewall
        echo -n "timetable_enabled" > $status_file
        return
    fi

}


timetable() {

    check_running_manual_mode

    action="stop"
    for pattern in $rules
    do
        debug "Inspecting rule: $pattern"
        time_start=$(echo $pattern | cut -d, -f 1)
        time_stop=$(echo $pattern | cut -d, -f 2)
        wday=$(echo $pattern | cut -d, -f 3)
        if [ "$wday" != "$WEEKDAY" ]; then
            debug "No matching weekday - skipping"
            continue
        fi

        time_start=$(convert_minutes $time_start)
        debug "now: $now < start: $time_start"
        if  [ $now -lt $time_start ];then
            debug "Before starting time: $time_start (now: $now) - skipping"
            continue
        fi

        time_stop=$(convert_minutes $time_stop)
        debug "now: $now > stop: $time_stop"
        if [ $now -eq $time_stop ] || [ $now -gt $time_stop ];then
            debug "After stopping time: $time_stop (now: $now) - skipping"
            continue
        fi
        debug " * rule activate: $pattern"
        action="start"
        break
    done

    debug "timetable action: $action"

    check_firewall $action

}


case $1 in
    start) enable_firewall
        echo -n "manual_enabled" > $status_file
           ;;
    stop) disable_firewall
          echo -n "manual_disabled" > $status_file
          ;;
    restart) $0 stop
             $0 start
             ;;
    status) get_status ;;
    timetable) timetable ;;
    reset) $0 stop
        rm -f $status_file
        ;;
    *) echo "Use: $0 [start|stop|status|restart|timetable|reset]"
esac

