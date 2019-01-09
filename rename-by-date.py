#! /usr/bin/python3
"""
Rename filename.extension to YYYYMMDD-HHMMSS.extension.
"""

import sys
import os
import time

def get_time(filename):
    file_stats = os.stat(filename)
    mtime = file_stats.st_mtime
    return time.localtime(mtime)

def convert_time2string(time_tuple):
    return time.strftime("%Y%m%d-%H%M%S", time_tuple)

def get_extension(filename):
    filename = os.path.basename(filename)
    filename_parts = filename.split(".")
    if len(filename_parts) > 1:
        return "." + filename_parts[-1]
    return ""

def does_exist(filename):
    if os.path.exists(filename):
        return True
    return False

def increment_name(filename):
    filename = os.path.basename(filename)
    f_parts = filename.split(".")
    timestamp = f_parts[0]
    extension = ""
    if len(f_parts) > 1:
        extension = "." + f_parts[1]
    t_parts = timestamp.split("-")
    if len(t_parts) == 2:
        timestamp += "-001"
    else:
        counter = "%03d" % (int(t_parts[-1]) + 1)
        timestamp = "-".join([t_parts[0], t_parts[1], counter])
    return "%s%s" % (timestamp, extension)

def get_new_name(filename):
    directory = os.path.dirname(filename)
    if len(directory) > 0:
        directory += "/"
    timestamp = get_time(filename)
    timestamp_str = convert_time2string(timestamp)
    extension = get_extension(filename)
    new_name = "%s%s" % (timestamp_str, extension)
    while does_exist("%s%s" % (directory, new_name)):
        new_name = increment_name(new_name)
    return "%s%s" % (directory, new_name)

def rename(listing):
    for filename in listing:
        new_filename = get_new_name(filename)
        print("filename=%s => %s" % (filename, new_filename))
        os.rename(filename, new_filename)



if __name__ == '__main__':
    rename(sys.argv[1:])
