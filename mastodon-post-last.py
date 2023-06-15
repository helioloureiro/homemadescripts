#! /usr/bin/env python3

from mastodon import Mastodon
import sys
import feedparser
from random import randrange
import requests
import configparser
import os
import time
import random
import argparse
import json


HOME = os.getenv('HOME')
CONFIG = f"{HOME}/.config/toot/config.json"
# old configuration
APICONFIG = f"{HOME}/.twitterc"


def ReverseLink(link):
    req = requests.get(link)
    if req.status_code != 200:
        print("Failed status code:", req.status_code)
        return None
    return req.url

def ShortMe(link, apikey):
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
           sleepMinutes(randomMinutes(5))
           print("Trying again")
       failure_counter += 1
       if failure_counter > 10:
          raise Exception("Failed to shortener link.")
   return shortened

def sleepMinutes(minutes):
    print(f'Sleeping {minutes} minutes')
    time.sleep(minutes * 60)

def randomMinutes(limit):
    return random.randint(1, limit)

def GetAPIKey():
    """
    Configuration from file ~/.twitterc
    """
    global apikey

    cfg = configparser.ConfigParser()
    print(f"Reading configuration: {APICONFIG}")
    if not os.path.exists(APICONFIG):
        print(f"Failed to find configuration file {APICONFIG}")
        exit(1)
    cfg.read(APICONFIG)
    apikey = cfg.get("SHORTENER", "APIKEY")
    return apikey

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='It posts the last published article')
    parser.add_argument("--userid", help="Your registered mastodon account at toot configuration")
    args = parser.parse_args()

    if args.userid is None:
        print('ERROR: missing --userid')
        parser.print_help()
        sys.exit(os.EX_NOINPUT)

    userid = args.userid

    print("Getting API key for shortener")
    apikey = GetAPIKey()

    print("Autenticating in Mastodon")
    with open(CONFIG) as tootConfig:
        config = json.load(tootConfig)

    mastodon = Mastodon(
        access_token = config['users'][userid]['access_token'], 
        api_base_url = config['users'][userid]['instance']
        )
    print('Mastodon login completed')

    print("Reading site's RSS")
    site = "http://helio.loureiro.eng.br/index.php?format=feed&type=rss"
    feed = feedparser.parse(site)

    try:
        rss = feed['entries'][0]
    except IndexError:
        print("No entries found in the rss feed")
        sys.exit(0)
    title = rss.title
    link = rss.link

    print("Shortening ", link)
    shortlink = ShortMe(link, apikey)
    print("5 seconds before posting - in case to cancel")
    time.sleep(5)
    print(f"Publishing: {title} {shortlink}")
    mastodon.toot(f"Novo post: {title} {shortlink}")
