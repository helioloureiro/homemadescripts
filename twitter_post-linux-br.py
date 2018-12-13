#! /usr/bin/python3
# -*- coding: utf-8 -*-

import twitter
from sys import exit
import requests
import feedparser
from random import randrange, randint
import configparser
import os
import dbm
import time
import telebot

# pyTelegramBotAPI
# https://github.com/eternnoir/pyTelegramBotAPI
# pip3 install pyTelegramBotAPI==3.6.2

# python-twitter
# pip3 install python-twitter==3.5


__version__ = "Thu Dec 13 14:05:31 CET 2018"


apikey = None
SLEEP = 1
SITE = "https://linux-br.org/index.php?format=feed&type=rss"
configuration = ".twitter_linux-br"
configuration = "%s/%s" % (os.environ.get("HOME"), configuration)
DBFILE = "%s/.linux-br.dbm" % os.environ.get("HOME")


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

def ReadConfig():
    """
    Configuration from file ~/.twitterc
    """
    global cons_key, \
        cons_sec, \
        acc_key, \
        acc_sec, \
        tlgr_token, \
        channel_id, \
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
    tlgr_token = cfg.get("TELEGRAM", "TOKEN")
    channel_id = int(cfg.get("TELEGRAM", "CHANNEL"))
    apikey = cfg.get("SHORTENER", "APIKEY")

def OpenDB():
    global db
    db = dbm.open(DBFILE, 'c')
    try:
        for k in db.keys():
            None
    except:
        db.close()
        db = dbm.open(DBFILE, 'n')


def CloseDB():
    global db
    db.close()

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
bot = telebot.TeleBot(tlgr_token, threaded=False)
json_string_boilerplate = {
    "message_id": 14,
    "from":{
        "id":64457589,
        "first_name": u'[helio@loureiro.eng.br/gandalf]>',
        "last_name": None,
        "username": u'HelioLoureiro',
        "is_bot": True
        },
    "chat":{
        "id": 64457589,
        "type":"private",
        "title": None
        },
    "date": int(time.time()),
    "text":"HIHI"
    }
msg = telebot.types.Message.de_json(json_string_boilerplate)
msg.chat.id = channel_id
msg.chat.type = "channel"
# "channel_post":{"message_id":8,"chat":{"id":-1001275615139,"title":"linux-br","username":"linux_br","type":"channel"},"date":1535125285,"text":"Testing..."}}]}
#print bot.get_chat(msg.chat.id)

OpenDB()
print("Reading site's RSS")
d = feedparser.parse(SITE)

for rss in d['entries']:
    title = u"%s" % rss.title
    link = u"%s" % rss.link
    if link.encode("ascii") in db:
        continue
    print("Adding into DB to track sent items.")
    db[link.encode("ascii")] = title
    print("Shortening ", link)
    shortlink = ShortMe(link)
    print("Publishing: %s %s" % (title, shortlink))
    try:
        print("Novo post: %s %s" % (title, shortlink))
        #api.PostUpdate(u"Novo post: %s %s" % (title, shortlink))
        #bot.send_message(msg.chat.id, u"%s %s" % (title, shortlink))
    except:
        pass
CloseDB()
