#!/usr/bin/env bash

# box characters: https://cloford.com/resources/charcodes/utf-8_box-drawing.htm

sizeof() {
    local msg="$1"
    local size=$(echo $msg | wc -L)
    # one space at beginning and other at the end
    size=$((size+2))
    echo $size
}

printchar() {
    local char="$1"
    local nr="$2"
    while [ $nr -gt 0 ]
        do
        echo -ne "$char"
        nr=$((nr-1))
    done
}


printbox() {
    local msg="$1"
    local s=$(sizeof "$msg")

    echo -n "┌"
    printchar "─" $s
    echo "┐"
    echo -e "│ ${msg} │"
    echo -n "└"
    printchar "─" $s
    echo -e "┘\n"
}

message="$@"
printbox "$message"
