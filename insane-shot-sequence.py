#! /usr/bin/python -u
# -*- coding: utf-8 -*-

"""
Based in:
http://stackoverflow.com/questions/15870619/python-webcam-http-streaming-and-image-capture
and
http://stackoverflow.com/questions/245447/how-do-i-draw-text-at-an-angle-using-pythons-pil
"""


from picamera import PiCamera
import picamera
import time
import sys
import os
import re
import requests
from random import randint, random
from shutil import copy

# stop annoying messages
# src: http://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
requests.packages.urllib3.disable_warnings()

HOMEDIR = os.environ.get("HOME")
configuration = "%s/.twitterc" % HOMEDIR
SAVEDIR = "%s/weather" % HOMEDIR
FAILDIR = "%s/images" % SAVEDIR
IMGSIZE = (1280, 720)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DISCARDFRAMES = 10
LOCKDIR = "/tmp"
LOCKPREFIX = ".weather"
FAILCOUNTER = 10 # amount ot attempts to get a picture
WARMUP = 10 # try to start webcam
THRESHOLD=15 # quality threshold
DEBUG = True
TIMEOUT =  10 * 60 # 10 minutes

start_time = time.time()

def debug(msg):
    if DEBUG:
        print msg

def GetPhotos(counter = 0):
    """
    Photo aquisition
    """
    global filename
    
    debug("Camera init")
    try:
        camera = PiCamera()
    except picamera.exc.PiCameraMMALError:
        print "Camera crashed... calling again."
        GetPhotos(counter)
        return
    debug("Camera start")
    camera.start_preview()
    time.sleep(1)
    #if not os.path.exists(SAVEDIR):
    #    os.makedirs(SAVEDIR)
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    if not os.path.exists("%s/%s/%s" % (SAVEDIR, year, month)):
        os.makedirs("%s/%s/%s" % (SAVEDIR, year, month) )
    timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
    filename = "%s/%s/%s/%s-%04d.jpg" % (SAVEDIR, year, month, timestamp,counter)
    debug("Saving file %s" % filename)
    camera.capture(filename)
    camera.stop_preview()
    camera.close()
 

if __name__ == '__main__':
    try:
        counter = 0
        time_start = time.time()
        maximum_time = 30 * 60
        while True:
            GetPhotos(counter)
            counter += 1
            time_current = time.time()
            delta = time_current - time_start
            print "Delta: %0.2f (maximum: %d)" % (delta, maximum_time)
            if (time_current - time_start) >= maximum_time:
                break
    except KeyboardInterrupt:
        sys.exit(0)
