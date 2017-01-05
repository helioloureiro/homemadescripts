#! /usr/bin/python -u
# -*- coding: utf-8 -*-

"""
Based in:
http://stackoverflow.com/questions/15870619/python-webcam-http-streaming-and-image-capture
and
http://stackoverflow.com/questions/245447/how-do-i-draw-text-at-an-angle-using-pythons-pil
"""


import pygame
import pygame.camera
import time
import sys
import os
import twitter
import ConfigParser
import json
import requests
import Image
import ImageFont, ImageDraw, ImageOps
import threading
import re
from random import randint, random
from shutil import copy
from math import modf

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
RETRIES = 10 # try to start webcam
THRESHOLD=15 # quality threshold
DEBUG = True
TIMEOUT =  10 * 60 # 10 minutes

mypid = os.getpid()
lockfile = "%s/%s.%d" % (LOCKDIR, LOCKPREFIX, mypid)
plock = threading.Lock() # control print
failed_img = "%s.failed_img.jpg" % sys.argv[0]
error_tries = FAILCOUNTER
start_time = time.time()

def debug(msg):
    if DEBUG:
        plock.acquire()
        print msg
        plock.release()

def lockpid():
    """
    Create a pid based lock file.
    Return true to "locked" and false in case of failure (already in use).
    """
    directory = os.listdir(LOCKDIR)
    lockedfile = None
    for filename in directory:
        if not re.search(LOCKPREFIX, filename): continue
        lockedfile = filename
    if lockedfile:
        # double check
        p = lockedfile.split(".")[-1]
        pid = int(p)
        try:
            # SIGNAL 18 is SIGCONT
            # it should be ignored
            os.kill(pid, 18)
            print "Process already running"
            return False
        except OSError:
            debug("Dead file found (%s).  Removing." % lockedfile)
            os.unlink("%s/%s" % (LOCKDIR, lockedfile))

    fd = open(lockfile, 'w')
    fd.write("%d\n" % mypid)
    fd.flush()
    fd.close()
    return True

def unlockpid():
    if os.path.exists(lockfile):
        debug("Removing lock")
        os.unlink(lockfile)

def Far2Celsius(temp):
    temp = float(temp)
    celsius = (temp - 32) * 5 / 9
    return "%0.1f" % celsius

def get_content():
    global wth_key, wth_loc

    debug("Getting text content")
    timestamp = time.strftime("Date: %Y-%m-%d %H:%M", time.localtime())
    msg = []
    msg.append("Stockholm")
    msg.append(timestamp)

    debug(" * requesting json about weather")
    url = "https://api.forecast.io/forecast/%s/%s" % (wth_key, wth_loc)
    req = requests.get(url)
    jdata = json.loads(req.text)

    # this was just to follow up - not needed
    #print jdata.keys()
    #print jdata["currently"]

    debug(" * converting from Farenheit to Celsius")
    summary = jdata["currently"]["summary"]
    temp = jdata["currently"]["temperature"]
    temp = Far2Celsius(temp)

    msg.append(u"Temperature: %s°C" % temp)
    msg.append("Summary: %s" %summary)

    debug(" * * Weather update finished")
    return msg

def getfailedimg():
    if not os.path.exists(FAILDIR):
        debug("Directory not found: %s" % FAILDIR)
        return None
    IMGS = []
    for filename in os.listdir(FAILDIR):
        if not re.search("jpg|gif|png", filename):
            continue
        IMGS.append("%s/%s" % (FAILDIR, filename) )
    # get a randomic one
    pos = randint(0, len(IMGS) - 1)
    chosen_one = IMGS[pos]
    copy(chosen_one, failed_img)
    return failed_img

def ReadConfig():
    global cons_key, cons_sec, acc_key, acc_sec, wth_key, wth_loc

    cfg = ConfigParser.ConfigParser()
    debug("Reading configuration: %s" % configuration)
    if not os.path.exists(configuration):
        print "Failed to find configuration file %s" % configuration
        sys.exit(1)
    cfg.read(configuration)
    cons_key = cfg.get("TWITTER", "CONS_KEY")
    cons_sec = cfg.get("TWITTER", "CONS_SEC")
    acc_key = cfg.get("TWITTER", "ACC_KEY")
    acc_sec = cfg.get("TWITTER", "ACC_SEC")
    wth_key = cfg.get("FORECAST.IO", "KEY")
    wth_loc = cfg.get("FORECAST.IO", "LOCATION")

def GetPhoto(f = None, quality = None):
    global filename, FAILCOUNTER, error_tries
    """
    """
    debug("GetPhoto: failcounter=%d" % FAILCOUNTER)
    if FAILCOUNTER < 0:
        print "Fail counter reached maximum attempts.  Failed."
        debug("Trying to return a failed img.")
        filename = getfailedimg()
        if not filename:
            sys.exit(1)
        debug("Using failed img: %s" % filename)
        # it needs to be 0ed or it will fail
        FAILCOUNTER = 0
        return 0
    filename = None
    debug("Pygame init")
    pygame.init()
    debug("Camera init")
    pygame.camera.init()
    device = None
    if os.path.exists("/dev/video1"):
        device = "/dev/video1"
    elif os.path.exists("/dev/video0"):
        device = "/dev/video0"
    if not device:
        print "Not webcam found.  Aborting..."
        sys.exit(1)
    # you can get your camera resolution by command "uvcdynctrl -f"
    cam = pygame.camera.Camera(device, IMGSIZE)

    debug("Camera start")
    cam.start()
    if FAILCOUNTER % 2:
        debug("Darker image...")
        time.sleep(1*FAILCOUNTER/FAILCOUNTER)
    else:
        debug("Lighter image...")
        time.sleep(FAILCOUNTER/(1 + FAILCOUNTER))
    #time.sleep(3)
    debug("Getting image ritual")
    counter = RETRIES
    while counter:
        if cam.query_image():
            debug(" * camera ready")
            break
        debug(" * waiting for camera (%d)" % counter)
        time.sleep(1)
        counter -= 1
    # idea from https://codeplasma.com/2012/12/03/getting-webcam-images-with-python-and-opencv-2-for-real-this-time/
    # get a set of pictures to be discarded and adjust camera
    debug(" * * RETRIES=%d" % RETRIES)
    debug(" * * error_tries=%d" % error_tries)
    debug(" * * FAILCOUNTER=%d" % FAILCOUNTER)
    debug(" * calibrating white balance: ")
    if (error_tries < 0):
        error_tries = 0
    for x in xrange(DISCARDFRAMES * ( error_tries - FAILCOUNTER + 1) ):
        while not cam.query_image():
            time.sleep(1)
        image = cam.get_image()
        msg = "." * x + "(%d)" % x
        debug(msg)
    debug(" * * getting image")
    debug("Smile!")
    image = cam.get_image()
    #debug(" ")
    #time.sleep(1)
    debug("Camera stop")
    cam.stop()

    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
    if not f:
        timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        # year = time.strftime("%Y", time.localtime())
        filename = "%s/%s.jpg" % (SAVEDIR, timestamp)
    else:
        filename = f
    debug("Saving file %s" % filename)
    pygame.image.save(image, filename)
    debug("Checking quality.")
    resp = brightness(filename, verbose=True)
    debug("Quality response=%d" % resp)
    if resp:
        debug("Low quality detected.  Fails=%d" % FAILCOUNTER)
        FAILCOUNTER -= 1
        if FAILCOUNTER < 6:
            if (resp <= THRESHOLD):
                debug("Not best quality, but acceptable")
                return 0
        debug("Trying with lower threshold for quality")
        # lower 20% of dark or ligth is ok
        debug("Low quality detected.  Trying again.")
        GetPhoto(filename)

def TheWalkingDead(walker=None):
    """
    After a certain time, it is sure task won't be completed.
    So kill it.
    """
    if not walker:
        return
    count = 0
    while(walker.isAlive()):
        time.sleep(random())
        current_time = time.time()
        delta = current_time - start_time
        #print "Thread(%s) counter=%d delta=%0.2f" % (walker, count, delta)
        if delta > TIMEOUT:
            debug("Reached timeout.  Killing pid")
            os.kill(mypid,9)
        count += 1


def WeatherScreenshot():
    debug("\n ### WeatherScreenshot [%s] ### " % time.ctime())
    debug("Threading image acquisition")
    #th = threading.Thread(target=GetPhoto)
    #th.start()
    #twd = threading.Thread(target=TheWalkingDead, args=(th,))
    #twd.walker = "Testing"
    #twd.start()
    #if not twd.is_alive():
    #    sys.exit(1)

    ReadConfig()

    debug("Autenticating in Twitter")
    # App python-tweeter
    # https://dev.twitter.com/apps/815176
    tw = twitter.Api(
        consumer_key = cons_key,
        consumer_secret = cons_sec,
        access_token_key = acc_key,
        access_token_secret = acc_sec
        )
    #debug("Retrieving info...")
    #msg = get_content()
    #th.join()
    #twd.join()

    #if FAILCOUNTER < 0:
    #    print "Failed to acquire image.  Quitting..."
    #    sys.exit(1)
    #if not msg:
    msg = "Just another reboot at %s" % \
            time.strftime("%H:%M", time.localtime())
    tw.PostUpdate(status = msg)
    if False:
        msg_body = "\n".join(msg[1:])
        im = Image.open(filename)
        # just get truetype fonts on package ttf-mscorefonts-installer
        try:
            f_top = ImageFont.truetype(font="Arial", size=60)
        except TypeError:
            # older versions hasn't font and require full path
            arialpath = "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"
            f_top = ImageFont.truetype(arialpath, size=60)
        try:
            f_body = ImageFont.truetype(font="Arial", size=20)
        except TypeError:
            # older versions hasn't font and require full path
            arialpath = "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"
            f_body = ImageFont.truetype(arialpath, size=20)

        # SHADOW
        step = 1
        for c in [ WHITE, BLACK ]:
            txt = Image.new('L', IMGSIZE)
            d = ImageDraw.Draw(txt)
            d.text( (10 + step, 10 + step), msg[0], font=f_top, fill=255)
            position = 80
            for m in msg[1:]:
                d.text( (10 + step, position + step), m, font=f_body, fill=255)
                position += 20
            w = txt.rotate(0, expand=1)
            step = 0
            im.paste(ImageOps.colorize(w, c, c), (0,0), w)
            im.save(filename)

        # adding the credit to the right guys (awesome guys btw)
        msg = u"%s \nvia http://forecast.io/#/f/59.4029,17.9436" % "\n".join(msg)
        try:
            print u"%s" % msg
        except UnicodeEncodeError:
            # I just hate this...
            pass
        if sys.argv[-1] == "dry-run":
            debug("Just dry-run mode.  Done!")
            return
        try:
            #tw.PostMedia(status = msg,media = filename)
            tw.Post(status = msg)
            debug("done!")
        except:
            print "Failed for some reason..."
            # it failed so... deal w/ it.
            pass
    else:
        print "no message available"
    #print "Removing media file %s" % filename
    #os.unlink(filename)


if __name__ == '__main__':
    try:
        if lockpid():
            WeatherScreenshot()
            unlockpid()
    except KeyboardInterrupt:
        sys.exit(0)
