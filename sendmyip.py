#! /usr/bin/python


import os, re, sys

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
    print "No IP found"
    sys.exit(0)


ip = getmyip()
cmd = "curl %s %s/?node=%s,%s" % \
      (CURLOPTS, HOST, NODENAME, ip)
print cmd
os.system(cmd)
