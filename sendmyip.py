#! /usr/bin/env python3

import os 
import re 
import sys

HOST = "http://myhost.get/"
INTF = "wlan0"
NODENAME = "raspberry"
CURLOPTS = "-o /dev/null -4 -s"

def getmyip():
    cmd = "ip addr list dev %s" % INTF
    resp = os.popen(cmd).readlines()
    for line in resp:
        if not re.search("inet ", line):
            continue
        params = line.split()
        ip = params[1]
        ip, net = ip.split("/")
        return ip
    print("No IP found")
    sys.exit(0)


if __name__ == '__main__':
    ip = getmyip()
    cmd = f"curl {CURLOPTS} {HOST}/?node={NODENAME},{ip}" 
    print(cmd)
    os.system(cmd)
