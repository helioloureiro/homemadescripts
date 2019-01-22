#! /usr/bin/python3

import os
import datetime
import sys

def get_time(filename):
    file_stats = os.stat(filename)
    mtime = file_stats.st_mtime
    return mtime


def report(file_listing):
    today = datetime.datetime.today()
    for filename in file_listing:
        if not os.path.exists(filename):
            print("ERROR: %s doesn't exist or is inacessible." % filename)
            continue
        st_mtime = get_time(filename)
        timestamp = datetime.datetime.fromtimestamp(st_mtime)
        delta = today - timestamp
        print("%s: %d" % (filename, delta.days))

if __name__ == '__main__':
    report(sys.argv[1:])
