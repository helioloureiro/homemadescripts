#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import twitter
from sys import exit
import feedparser
from random import randrange
import requests
import configparser
import os
import time
import random

configuration = ".twitterc"
configuration = "%s/%s" % (os.environ.get("HOME"), configuration)

def ReverseLink(link):
    req = requests.get(link)
    if req.status_code != 200:
        print("Failed status code:", req.status_code)
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
           time.sleep(SLEEP * random.randint(1,5))
           print("Trying again")
       failure_counter += 1
       if failure_counter > 10:
          raise Exception("Failed to shortener link.")
   return shortened

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

ReadConfig()

print("Autenticating in Twitter")
# App python-tweeter
# https://dev.twitter.com/apps/815176
api = twitter.Api(
    consumer_key = cons_key,
    consumer_secret = cons_sec,
    access_token_key = acc_key,
    access_token_secret = acc_sec
    )

print("Reading site's RSS")
site = "http://helio.loureiro.eng.br/index.php?format=feed&type=rss"
d = feedparser.parse(site)

#api.PostUpdate("AutomagicTweets de auto-promoção, sem a menor vergonha na cara...")

for rss in d['entries']:
#  if (randrange(0,2) == 0):
    title = rss.title
    link = rss.link
    print("Shortening ", link)
    shortlink = ShortMe(link)
    print("5 seconds before posting - in case to cancel")
    time.sleep(5)
    print("Publishing: %s %s" % (title, shortlink))
    #sleep(60)
    api.PostUpdate("Novo post: %s %s" % (title, shortlink))
    exit(0)
