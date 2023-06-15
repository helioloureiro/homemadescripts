#! /usr/bin/python3 -u
# -*- coding: utf-8 -*-

import twitter
from time import sleep, ctime
from sys import exit, argv
import requests
import feedparser
from random import randrange
import os
from re import sub
import re
import configparser

configuration = ".twitterc"
configuration = "%s/%s" % (os.environ.get("HOME"), configuration)


def ReverseLink(link):
    req = requests.get(link)
    if req.status_code != 200:
        return None
    return req.url

def ShortMe(link):
   shortened = None
   failure_counter = 0
   while shortened is None:
       try:
           url = 'https://hl.eng.br/api.php?url=' + link
           if apikey is not None:
               url += '&key=' + apikey
           print("url=%s" % url)
           req = requests.get(url)
           if req.status_code == 200:
               reverse = ReverseLink(req.text)
               print("reverse=%s" % reverse)
               if reverse == link:
                   shortened = req.text
       except:
           print("Shortening failed.")
           time.sleep(SLEEP * randint(1,5))
           print("Trying again")
       failure_counter += 1
       if failure_counter > 10:
          raise Exception("Failed to shortener link.")
   return shortened

def Fortune():
    """
    Generating a cute fortune.  140 chars longer at maximum.
    """
    print("Gerando fortune...")
    f = os.popen("/usr/games/fortune -n 140")
    t = f.read()
    #t = "#FORTUNE: " + t
    if (len(t) > 140):
        t = Fortune()
    t = sub("Deus", "beer", t)
    t = sub("God", "beer", t)
    t = sub("Lord", "beer", t)
    if re.search("mulher", t):
        t = Fortune()
    return t

def ReadConfig():
    """
    Configuration from file ~/.twitterc
    """
    global cons_key, \
        cons_sec, \
        acc_key, \
        acc_sec, \
        apikey

    cfg = configparser.ConfigParser()
    print("Reading configuration: %s" % configuration)
    if not os.path.exists(configuration):
        print("Failed to find configuration file %s" % configuration)
        exit(1)
    cfg.read(configuration)
    cons_key = cfg.get("TWITTER", "CONS_KEY")
    cons_sec = cfg.get("TWITTER", "CONS_SEC")
    acc_key = cfg.get("TWITTER", "ACC_KEY")
    acc_sec = cfg.get("TWITTER", "ACC_SEC")
    apikey = cfg.get("SHORTENER", "APIKEY")

if (argv[-1] == "-c"):
   import py_compile
   print("Compilando:", argv[0])
   py_compile.compile(argv[0])
   exit(0)

print("######### Starting at: " + str(ctime()) + " ########################")
ReadConfig()

print("Autenticating in Twitter")
# App python-tweeter
# https://dev.twitter.com/apps/815176
api = twitter.Api(
    consumer_key        = cons_key,
    consumer_secret     = cons_sec,
    access_token_key    = acc_key,
    access_token_secret = acc_sec
    )

print("Reading site's RSS")
site = "http://helio.loureiro.eng.br/index.php?format=feed&type=rss"
d = feedparser.parse(site)

try:
   api.PostUpdate("AutomagicTweets de auto-promoção, " + \
                  "sem a menor vergonha na cara...")
except:
   pass
api.PostUpdate(Fortune())

for i in range(len(d.entries), 0, -1):
    pos = i - 1 # rss position
    rss = d.entries[pos]
    if (randrange(0,10) >= 7):
        if (randrange(0,10) >= 7):
            api.PostUpdate(Fortune())
        title = rss.title
        link = rss.link
        print("Shortening ", link)
        shortlink = ShortMe(link)
        #title = title.encode('utf-8')
        try:
            print("Publishing: %s %s" % (title, shortlink))
        except UnicodeEncodeError as e:
            print("Failed to print due unicode: ", e)
            sleep(10 * 60)
        try:
            api.PostUpdate("#Lembra? %s %s" % (title, shortlink))
        except twitter.TwitterError as e:
            print("Failed to post:", e)
        except UnicodeDecodeError as e:
            print("Failed to post due unicode issue: ", e)
            #api.PostUpdate("#Lembra? %s %s" % (title.decode('latin-1').encode('utf-8'),
            #                                   shortlink.decode('latin-1').encode('utf-8')))
            api.PostUpdate(f"#Lembra? {title} {shortlink}")
    else:
        #print("Ignorando o post:", rss.title.encode('utf-8'))
        print(f"Ignorando o post: {rss.title}")
