#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
This script tries to find the videos under the directories like:
    /api/1/20180711/sala41c-high-201607161401.ogv
if video isn't there, it won't try to process and move to the next one.
If if it is available, it will upload to Youtube using the information
gathered onto site and move to directory "done" after finished.
"""

import json
import requests
import re
import os
import shutil
import logging
import sys
logging.captureWarnings('InsecurePlatformWarning')

YEAR = "2018"
MONTH = "07"
ROOMS = range(1, 12)
DAYS = range(11, 15)
SERVER = "https://segue-api.fisl18.softwarelivre.org"
SECRET = "%s/pytube-client_secret.json" % os.environ.get("HOME")
"""
Rooms
https://segue-api.fisl18.softwarelivre.org/api/rooms/2/slots/of-day/2018-07-11
https://segue-api.softwarelivre.org/api/rooms/1/slots/of-day/2016-07-13
Talks
https://segue-api.softwarelivre.org/api/talks/652
https://segue-api.fisl18.softwarelivre.org/api/talks/12
"""

def build_url(room, day):
    url = "%s/api/rooms/%d/slots/of-day/%s-%s-%d" % (SERVER, room, YEAR, MONTH, day)
    return url

def build_talk(talkid):
    url = "%s/api/talks/%s" % (SERVER, talkid)
    return url

def youtube(title, descr, author, tags, video):
    descr = "%s\n\n%s" % (descr, author)
    descr = descr.replace("\"", "\\\"")
    title = title.replace("\"", "\\\"")
    cmd = "youtube-upload " + \
        "--title=\"%s\" " % title + \
        "--description=\"%s\" " % descr + \
        "--client-secrets=%s " % SECRET + \
        "--tags=\"%s\" " % tags + \
        "\"%s\"" % video

    try:
        print(cmd)
        result = os.system(cmd)
    except UnicodeEncodeError:
        cmd_ascii = cmd.decode("utf-8").encode("iso8859-1")
        print(cmd_ascii)
        result = os.system(cmd_ascii)
    return result


def processed(video):
    videoname = os.path.basename(video)
    shutil.move(video, "done/%s" % videoname)

def video_dir(full_path):
    # remove http or https
    dirname = re.sub("^.*://", "", os.path.dirname(full_path))
    # split in slices
    piece_cakes = dirname.split("/")
    # make the cake
    cake = "/".join(piece_cakes[1:])
    # enjoy
    return cake

def download_video(video_url):
    videoname = os.path.basename(video_url)
    videopath = video_dir(video_url)

    if os.path.exists("%s/%s" % (videopath, videoname)):
        if os.stat("%s/%s" % (videopath, videoname)).st_size != 0:
            return

    if not os.path.exists(videopath):
        os.makedirs(videopath)

    video = requests.get(video_url, stream=True)
    with open("%s/%s" % (videopath, videoname), 'wb') as destination:
        for block in video.iter_content(chunk_size=1024):
            if block:
                destination.write(block)

def check_upload_status(filename):
    if os.path.exists("done/%s" % filename):
        return True
    return False

def build_listing():
    if not os.path.exists("done"):
        os.mkdir("done")
    for room in sorted(ROOMS):
        for day in DAYS:
            print("Retrieving info from room %d at day %d" % (room, day))
            url = build_url(room, day)
            #print url
            resp = requests.get(url)
            j = json.loads(resp.text)
            #print("DUMP: %s" % json.dumps(j))
            for presentation in j["items"]:
                print("PRESENTATION")
                #print presentation
                #return
                if presentation["status"] != "confirmed":
                    print(" * cancelled")
                    continue
                timestamp = presentation["begins"]
                title = presentation["talk"]["title"]
                authors = presentation["talk"]["owner"]
                if presentation["talk"]["coauthors"]:
                    a = ",".join(presentation["talk"]["coauthors"])
                    authors = "%s e %s" %(a, authors)
                #print authors
                track = presentation["talk"]["track"]
                track = re.sub("[-/]", ",", track)
                track = re.sub(" e ", ",", track)
                track = re.sub(",,", ",", track)
                tags = "FISL18, %s" % track
                talkid = presentation["talk"]["id"]
                url2 = build_talk(talkid)
                try:
                    video = presentation["recordings"][-1]
                except IndexError:
                    continue

                #print url2
                r = requests.get(url2)
                j2 = json.loads(r.text)
                #print(" * dump2: %s" % json.dumps(j2))
                full = j2["resource"]["full"]
                try:
                    print("Title: %s" % title)
                except UnicodeEncodeError:
                    print("Title skipped due UnicodeEncodeError")
                try:
                    print("Author(s): %s" % authors)
                except UnicodeEncodeError:
                    print("Author(s) skipped due UnicodeEncodeError")
                try:
                    print("Video: %s" % video)
                except UnicodeEncodeError:
                    print("Video skipped due UnicodeEncodeError")
                try:
                    print("Tags: %s" % tags)
                except UnicodeEncodeError:
                    print("Tags skipped due UnicodeEncodeError")
                try:
                    print("Timestamp: %s" % timestamp)
                except UnicodeEncodeError:
                    print("Timestamp skipped due UnicodeEncodeError")
                try:
                    print("Description: %s" % full)
                except UnicodeEncodeError:
                    print("Description skipped due UnicodeEncodeError")

                videoname = os.path.basename(video)
                #Video: http://hemingway.softwarelivre.org/fisl18/high/Sala 1/sala1-high-201807121056.ogv
                #videopath = "/fisl18/high/Sala %d/%s%s%d/%s" % (room, YEAR, MONTH, day, videoname)
                videopath = video_dir(video)

                if check_upload_status(videoname) is False:
                    download_video(video)
                    result = youtube(title, full, authors, tags, videopath + "/" + videoname)
                    if result != 0:
                        print("Video failed to upload.")
                        sys.exit(result)
                    processed(videopath + "/" + videoname)


if __name__ == '__main__':
    try:
        build_listing()
    except KeyboardInterrupt:
        print("That's all folks!")
