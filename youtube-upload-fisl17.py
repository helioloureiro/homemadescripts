#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
This script tries to find the videos under the directories like:
    41c/20160714/sala41c-high-201607161401.ogv
if video isn't there, it won't try to process and move to the next one.
If if it is available, it will upload to Youtube using the information
gathered onto site and move to directory "done" after finished.
"""

import simplejson as json
import requests
import re
import os
import shutil
import logging
logging.captureWarnings('InsecurePlatformWarning')


ROOMS = { "41a" : 1, "41b" : 2, "41c" : 3 , "41d" : 4, "41e" : 5 }
DAYS = [ "13", "14", "15", "16" ]
SERVER = "https://segue-api.softwarelivre.org/api"
SECRET = "/home/ehellou/pytube-client_secret.json"
"""
Rooms
https://segue-api.softwarelivre.org/api/rooms/1/slots/of-day/2016-07-13
Talks
https://segue-api.softwarelivre.org/api/talks/652
"""

def build_url(room, day):
    roomid = ROOMS[room]
    url = "%s/rooms/%d/slots/of-day/2016-07-%s" % (SERVER, roomid, day)
    return url

def build_talk(talkid):
    url = "%s/talks/%s" % (SERVER, talkid)
    return url

def youtube(title, descr, author, tags, video):
    descr = "%s\n\n%s" % (descr, author)
    descr = re.sub("\"", "\\\"", descr)
    title = re.sub("\"", "\\\"", title)
    cmd = "youtube-upload " + \
        "--title=\"%s\" " % title + \
        "--description=\"%s\" " % descr + \
        "--client-secrets=%s " % SECRET + \
        "--tags=\"%s\" " % tags + \
        "%s" % video
    print cmd
    os.system(cmd.encode("utf-8"))

def processed(video):
    videoname = os.path.basename(video)
    shutil.move(video, "done/%s" % videoname)

def build_listing():
    if not os.path.exists("done"):
        os.mkdir("done")
    for room in sorted(ROOMS.keys()):
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
                tags = "FISL17, %s" % track
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
                print """Title: %s
Author(s): %s
Description: %s
Video: %s
Tags: %s
Timestamp: %s

""" % (title, authors, full, video, tags, timestamp)
                #return
                videoname = os.path.basename(video)
                videopath = "%s/201607%s/%s" % (room, day, videoname)
                if os.path.exists(videopath):
                    print videopath
                else:
                    print "Already processed.  Skipping..."
                    continue
                youtube(title, full, authors, tags, videopath)
                processed(videopath)
                #return

if __name__ == '__main__':
    build_listing()