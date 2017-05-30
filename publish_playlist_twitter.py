#! /usr/bin/python -u

"""
Publish video playlist into Twitter.
"""
import list_youtuble_playlist as ytb
import twitter
import random
import curl
import tempfile
import os
import ConfigParser
import time

PLAYLIST = "PLQYPYhKQVTvcNqNnkEfEKhaMxUf2tn_CP" # PyConSE
HOMEDIR = os.environ.get("HOME")
configuration = "%s/.twitterc" % HOMEDIR

def ReadConfig():
    """
    Configuration from file ~/.twitterc
    """
    global cons_key, cons_sec, acc_key, acc_sec, wth_key, wth_loc

    cfg = ConfigParser.ConfigParser()
    print "Reading configuration: %s" % configuration
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

def GetVideo():
    y = ytb.main(PLAYLIST)
    x = os.urandom(int(time.time()/1000))
    random.seed(x)
    talk = random.choice(y.keys())
    return { talk : y[talk] }

def GetImage(url, fd):
    c = curl.Curl()
    c.get(url)
    img_write = os.fdopen(fd, 'w')
    img_write.write(c.body())
    img_write.flush()
    img_write.close()

def TwitterPost(video_info):
    # App python-tweeter
    # https://dev.twitter.com/apps/815176
    tw = twitter.Api(
        consumer_key = cons_key,
        consumer_secret = cons_sec,
        access_token_key = acc_key,
        access_token_secret = acc_sec
    )
    title = video_info.keys()[0]
    print "Title: %s" % title
    image = video_info[title]['thumb']
    print "Image: %s" % image
    url = video_info[title]['url']
    print "Video: %s" % url
    fd, file_image = tempfile.mkstemp()
    GetImage(image, fd)
    msg = "Watch again: %s\n%s #pyconse" % (title, url)
    print "Posting: %s" % msg
    print "Image: %s" % file_image
    tw.PostMedia(status = msg,media = file_image)
    os.unlink(file_image)

def main():
    video = GetVideo()
    ReadConfig()
    TwitterPost(video)


if __name__ == '__main__':
    main()
