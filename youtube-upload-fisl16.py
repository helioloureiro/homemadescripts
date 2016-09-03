#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
This script gets all schedule from FISL16, tries to find the video online,
download it and upload onto Youtube..
"""

import simplejson as json
import requests
import re
import os
import sys
from time import sleep
import logging
logging.captureWarnings('InsecurePlatformWarning')

DRYRUN = False
ROOMS = xrange(1,13)
DAYS = [ "08", "09", "10", "11" ]
SERVER = "http://schedule.fisl16.softwarelivre.org/api16"
SECRET = "/home/helio/pytube-client_secret.json"
"""
Rooms
http://schedule.fisl16.softwarelivre.org/api/rooms/1/slots/of-day/2015-07-08
http://schedule.fisl16.softwarelivre.org/api16/rooms/1/slots/of-day/2015-07-11
Talks
http://schedule.fisl16.softwarelivre.org/api16/talks/299
"""

def build_url(room, day):
    url = "%s/rooms/%s/slots/of-day/2015-07-%s" % (SERVER, room, day)
    return url

def build_talk(talkid):
    url = "%s/talks/%s" % (SERVER, talkid)
    return url

def youtube(title, descr, author, tags, video):
    descr = "%s\n\n%s" % (descr, author)
    descr = re.sub("\"", "\\\"", descr)
    title = re.sub("\"", "\\\"", title)
    cmd = "youtube-upload " + \
        u"--title=\"%s\" " % title + \
        u"--description=\"%s\" " % descr + \
        "--client-secrets=%s " % SECRET + \
        u"--tags=\"%s\" " % tags + \
        "%s" % video
    print cmd
    if not DRYRUN:
        os.system(cmd)

def wget(video):
    print "Running wget"
    cmd = "wget %s" % video
    if not DRYRUN:
        os.system(cmd)
    else:
        print "Saving fake video file"
        touch(video)

def processed(video):
    videoname = os.path.basename(video)
    # saving space instead
    # shutil.move(video, "done/%s" % videoname)
    os.unlink(video)
    target = "done/%s" % videoname
    fd = open(target, "w")
    fd.write("done\n")
    fd.flush()
    fd.close()

def touch(filename):
    filename = re.sub(".*/", "", filename)
    fd = open(filename, "w")
    fd.flush()
    fd.close()
    print "File %s created" % filename

def info():
    print "Getting help..."
    print "Usage: %s [dry-run]" % sys.argv[0]
    print "\tdry-run: it doesn't download real video, neither tries to " + \
        "upload to youtube"

def build_listing():
    global DRYRUN

    if re.search("help", sys.argv[-1]):
        info()
        sys.exit(0)
    if sys.argv[-1] == "dry-run":
        print "Running in dry-run mode"
        DRYRUN = True

    if not os.path.exists("done"):
        os.mkdir("done")
    for room in ROOMS:
        room = str(room)
        for day in DAYS:
            print "Retrieving info from room %s at day %s" % (room, day)
            url = build_url(room, day)
            #print url
            resp = requests.get(url)
            j = json.loads(resp.text)
            for presentation in j["items"]:
                print "PRESENTATION"
                #print presentation
                #return
                if presentation["status"] != "confirmed":
                    continue
                timestamp = presentation["begins"]
                title = presentation["talk"]["title"]
                authors =  presentation["talk"]["owner"]
                if presentation["talk"]["coauthors"]:
                    a = ",".join(presentation["talk"]["coauthors"])
                    authors = "%s e %s" %(a, authors)
                #print authors
                track = presentation["talk"]["track"]
                track = re.sub("[-/]",",", track)
                track = re.sub(" e ", ",", track)
                track = re.sub(",,", ",", track)
                tags = "FISL16, %s" % track
                talkid = presentation["talk"]["id"]
                url2 = build_talk(talkid)
                try:
                    video = presentation["recordings"][-1]
                except IndexError:
                    continue
                #print url2
                r = requests.get(url2)
                j2 = json.loads(r.text)
                full = j2["resource"]["full"]
                #print full
                #print ""
                text =  u"""Title: %s
Author(s): %s
Description: %s
Video: %s
Tags: %s
Timestamp: %s

""" % (title, authors, full, video, tags, timestamp)
                print text.encode("utf-8")
                #return
                videoname = os.path.basename(video)
                print "Video=%s" % video
                print "VideoName=%s" % videoname
                videopath = "done/%s" % videoname
                if os.path.exists(videopath):
                    print "Already processed.  Skipping..."
                    #return
                    continue
                wget(video)
                youtube(title, full, authors, tags, videoname)
                processed(videoname)
                #return
                # sleep a bit in case to SIGSTOP is needed
                sleep(5)

if __name__ == '__main__':
    build_listing()