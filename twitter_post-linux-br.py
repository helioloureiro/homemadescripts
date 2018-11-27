#! /usr/bin/python
# -*- coding: utf-8 -*-

import twitter
from sys import exit
import urllib2
import feedparser
from random import randrange
import ConfigParser
import os
import bsddb
import time
import telebot

# pyTelegramBotAPI
# https://github.com/eternnoir/pyTelegramBotAPI
# pip3 install pyTelegramBotAPI


__version__ = "Fri Aug 24 18:45:04 CEST 2018"


# UnicodeEncodeError: 'ascii' codec can't encode characters in position 130-131: ordinal not in range(128)
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

apikey = None
SLEEP = 1

def ShortMe(link):
   status=False
   sleep_time = SLEEP
   while status is not True:
       try:
           url = 'https://hl.eng.br/api.php?url=' + link
           if apikey is not None:
               url += '&key=' + apikey
           f = urllib2.urlopen(url)
           status = True
       except:
           print "Shortening failed."
           time.sleep(sleep_time)
           print "Trying again"
       sleep_time += 1
       if sleep_time > 10:
          raise Exception("Failed to shortener link.")
   resp = f.read(100)

   return resp

print "Autenticating in Twitter"
# App python-tweeter
# https://dev.twitter.com/apps/815176
configuration = ".twitter_linux-br"
configuration = "%s/%s" % (os.environ.get("HOME"), configuration)
DBFILE = "%s/.linux-br.db" % os.environ.get("HOME")

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

    cfg = ConfigParser.ConfigParser()
    print "Reading configuration: %s" % configuration
    if not os.path.exists(configuration):
        print "Failed to find configuration file %s" % configuration
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
    db = bsddb.btopen(DBFILE, 'c')
    try:
        for k in db.keys():
            None
    except:
        db.close()
        db = bsddb.btopen(DBFILE, 'n')


def CloseDB():
    global db
    db.sync()
    db.close()

ReadConfig()
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
print "Reading site's RSS"
site = "https://linux-br.org/index.php?format=feed&type=rss"
d = feedparser.parse(site)

for rss in d['entries']:
#  if (randrange(0,2) == 0):
    title = u"%s" % rss.title
    link = u"%s" % rss.link
    if db.has_key(link.encode("ascii")):
        continue
    print "Adding into DB to track sent items."
    db[link.encode("ascii")] = title
    print u"Shortening ", link
    shortlink = ShortMe(link)
    print u"Publishing: %s %s" % (title, shortlink)
    #sleep(60)
    try:
        api.PostUpdate(u"Novo post: %s %s" % (title, shortlink))
        bot.send_message(msg.chat.id, u"%s %s" % (title, shortlink))
    except:
        pass
    #exit(0)
CloseDB()
