#! /usr/bin/python -u
# -*- coding: utf-8 -*-
#
import twitter
from time import *
from sys import exit, argv
from random import randrange, random, SystemRandom
import re
import os
import ConfigParser
from py_compile import compile
import httplib

"""
Add it into your crontab
30 9 * * 5 python /path/to/twitter_friends.py
"""

configuration = ".twitterc"
configuration = "%s/%s" % (os.environ.get("HOME"), configuration)
user = 'helioloureiro'
dryrun = False
CONTROLE = {} # control for the ones already done or not so lucky
FFS = {} # all followers


SIZE = 140
MSG = ""
PCTG = 10 # % of chance to post.  Lower means less posts.
counter = 1 # users count

TESTE = False

if twitter.__version__ != '3.2':
    print "Only python-twitter 3.2 is supported"
    exit(1)

def isLucky():
  #result = int(random() * 100)
  result = int(SystemRandom().random() * 100)
  if (result <= PCTG):
    return True
  else:
    return False

def SendingList(api, tag, list_name):
    """
    Sending message
    """
    global FFS, CONTROLE, counter, dryrun

    print "Running for %s: %d" % (tag, len( FFS[list_name] ))
    MSG = tag + " "
    for name in FFS[list_name]:
        if CONTROLE.has_key(name):
            continue
        else:
            CONTROLE[name] = 1
        print counter, name
        name = '@' + name
        if ( len(MSG + " " + name) > SIZE):
            print MSG
            if not dryrun:
                api.PostUpdate(MSG)
                sleep(randrange(1,30) * 60)
            MSG = tag + " " + name
        else:
            MSG += " " + name
        counter += 1

    if not dryrun:
        sleep(randrange(1,30) * 60)

    print MSG
    if not dryrun:
        try:
            api.PostUpdate(MSG)
        except twitter.TwitterError as e:
            if ( re.search('Status is a duplicate.', e.message) ):
                pass

def ReadConfig():
    """
    Configuration from file ~/.twitterc
    """
    global cons_key, cons_sec, acc_key, acc_sec

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

def GetDateTag():
    """
    Check comemorative days
    """
    # Find great tags:
    month = strftime("%B",localtime())
    day = strftime("%d",localtime())

    tag = "#FF" #default
    if (day, month) == ('02', 'November'):
       tag = "#FollowFinados"
    elif (day, month) == ('25', 'December'):
       tag = "#FollowXmas"
    elif (day, month) == ('01', 'January'):
       tag = "#FollowHappyNewYear"
    elif (day, month) == ('25', 'January'):
       tag = "#FollowSPb-day"
    elif (day, month) == ('31', 'October'):
       tag = "#FollowHalloween"
    elif (day, month) == ('15', 'November'):
       tag = "#FollowRepublic"
    elif (day, month) == ('08', 'March'):
       tag = "#FollowWomenDay"
    elif (day, month) == ('14', 'February'):
       tag = "#FollowStValentine"
    elif (day, month) == ('17', 'February'):
       tag = "#FollowStPatrick"
    elif (day, month) == ('01', 'May'):
       tag = "#FollowLaborDay"
    elif (day, month) == ('19', 'June'):
       tag = "#FollowCorpusChristi"
    elif (day, month) == ('20', 'June'):
       tag = "#FollowCorpusChristi"
    elif (day, month) == ('28', 'November'):
       tag = "#FollowBlackFriday"
    elif (day, month) == ('29', 'November'):
       tag = "#FollowBlackFriday"
    else:
       """
       Only days to check
       """
       if (day == '13'):
          tag = "#FollowFriday13th"

    return tag

### MAIN ###
def main():
    global FFS, CONTROLE, dryrun
    if (argv[-1] == "-c"):
       compile(argv[0])
       exit(1)

    if argv[-1] in [ "-t", "-d" ]:
        dryrun = True
        print "Activated dryrun mode"

    time_i = time()
    print "[" + ctime() + "] starting your twitter_friends..."

    dow = strftime("%A", localtime())
    if (dow != 'Friday'):
       print "Today isn't #FF day, because today isn't Friday, doh!", str(dow)
       if not (argv[-1] == "--force"):
          print "Aborting..."
          exit(1)
       else:
          print "Called \"force\".  Enforcing."

    tag =  GetDateTag()
    print "Running on tag:", tag

    ReadConfig()

    print "Autenticating in Twitter"
    # App python-tweeter
    # https://dev.twitter.com/apps/815176
    try:
        api = twitter.Api(
            consumer_key = cons_key,
            consumer_secret = cons_sec,
            access_token_key = acc_key,
            access_token_secret = acc_sec
            )
    except:
        print "Failed to authenticate on Twitter."
        exit(1)

    print "Gathering lists"
    all_lists = api.GetLists(screen_name = user)
    #print all_lists
    """
    >>> for l in mylists:
    ...     print l.slug, l.name, l.id
    ...
    python Python 99979587
    ff FF 71764323
    freebsd FreeBSD 61981324
    linux Linux 53798850
    amigos Amigos 40323100
    misc Misc 40166658
    futebol Futebol 32886245
    articulistas Articulistas 21454410
    piadistas-infames piadistas_infames 13674852
    """

    for l in all_lists:
        #print "Checking list %s" % l.slug
        # lists that I want to promote
        if not l.slug.lower() in [
            'linux',
            'ff',
            'python',
            'ultrafofos'
        ]:
            continue
        print "\n ###### Parsing list: %s ###### " % l.slug
        FFS[l.slug.lower()] = []
        members = api.GetListMembers(list_id=l.id)
        #print members
        for m in members:
            if isLucky():
                FFS[l.slug].append(m.screen_name)
            else:
                CONTROLE[m.screen_name] = 1
        print "Total: %d" % len(FFS[l.slug])

    try:
       msg = "Automated python-twitter-" + tag + " mode=on"
       if not dryrun:
          api.PostUpdates(msg)
       else:
          print msg
    except twitter.TwitterError as e:
       if ( re.search('Status is a duplicate.', str(e.message)) ):
          pass

    """
    Processing the main one, ff list
    """
    SendingList(api, tag, "ff")

    """
    Python list
    """
    SendingList(api, "#FFPython", "python")

    """
    Linux list
    """
    SendingList(api, "#FFLinux", "linux")

    """
    Ultrafofos list
    """
    SendingList(api, "#UltraFoFo", "ultrafofos")

    """
    Happy ending...
    """

    try:
       if not dryrun:
          api.PostUpdates("Python Twitter #rockz!!!")
          api.PostUpdates("Automated python-twitter-" + tag + " mode=off")
    except twitter.TwitterError as e:
       if ( re.search('Status is a duplicate.', e.message) ):
          pass

    time_e = time()
    print "[%s] finished twitter_friends... (%0.2f s)" % (ctime(), time_e - time_i)


if __name__ == '__main__':
    main()