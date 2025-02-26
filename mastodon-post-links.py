#! /usr/bin/env python3
# 
# it uses configuration from toot
import os
import json
import argparse
import sys
from mastodon import Mastodon
import random
import configparser
import subprocess
import requests
import feedparser
import time
import re

HOME = os.getenv('HOME')
CONFIG = f"{HOME}/.config/toot/config.json"
# old configuration
APICONFIG = f"{HOME}/.twitterc"

FORTUNE = {
    "Linux": [ "/usr/games/fortune", "brasil" ],
    "Darwin": "/opt/homebrew/bin/fortune"
}

RSS_SITE = "http://helio.loureiro.eng.br/index.php?format=feed&type=rss"

# mastodon limits toots to 550 characters
POST_LIMIT_SIZE = 550
BRASIL_FORTUNE_MACOS = "/opt/homebrew/Cellar/fortune/9708/share/games/fortunes/brasil"

TRANSLATION_TABLE = {
    "Deus" : "cerveja",
    "God" : "beer",
    "Lord" : "beer"
}

def ReverseLink(link):
    req = requests.get(link)
    if req.status_code != 200:
        return None
    return req.url

def ShortMe(link, apikey=None):
   shortened = None
   failure_counter = 0
   while shortened is None:
       try:
           url = 'https://hl.eng.br/api.php?url=' + link
           if apikey is not None:
               url += '&key=' + apikey
           req = requests.get(url)
           if req.status_code == 200:
               reverse = ReverseLink(req.text)
               if reverse == link:
                   shortened = req.text
       except:
           print("WARNING: shortening failed.")
           sleepMinutes(5)
           print("WARNING: trying again")
       failure_counter += 1
       if failure_counter > 10:
          raise Exception("ERROR: Failed to shorten the link.")
   return shortened

def macosFortune():
    # after installed via brew
    # brasil file was copied from a Linux installation (debian)
    with open(BRASIL_FORTUNE_MACOS) as r:
        data = r.read()
    blocks = data.split('\n%\n')
    return random.choice(blocks)

def Fortune():
    """
    Generating a cute fortune.  550 chars longer at maximum.
    """
    platform = os.uname().sysname
    fortune = ""
    # MacOS hasn't brasil map, so it will require a bit more tricky here
    if platform == 'Linux':
        response = subprocess.check_output(FORTUNE[platform])
        fortune = response.encode('utf-8')
    elif platform == 'Darwin':
        fortune = macosFortune()

    if (len(fortune) == 0) or (len(fortune) > POST_LIMIT_SIZE):
        fortune = Fortune()
    
    for key, value in TRANSLATION_TABLE.items():
        fortune = re.sub(key, value, fortune)

    # avoiding misoginistic posts
    if re.search("mulher", fortune):
        fortune = Fortune()
    return fortune

def Lottery(percentage):
    result = random.randint(0, 100)
    if percentage > result:
        return True
    return False

def sleepMinutes(minutes):
    print(f'Sleeping {minutes} minutes')
    time.sleep(minutes * 60)

def randomMinutes(limit):
    return random.randint(1, limit)

class TootPostLink:
    def __init__(self, userid):
        with open(CONFIG) as tootConfig:
            config = json.load(tootConfig)

        self.mastodon = Mastodon(
            access_token = config['users'][userid]['access_token'], 
            api_base_url = config['users'][userid]['instance']
            )
        self.me = self.mastodon.me()
        print('Mastodon login completed')

        cfg = configparser.ConfigParser()
        cfg.read(APICONFIG)
        self.apikey = cfg.get("SHORTENER", "APIKEY")
    

    def send(self):
        text = '#TT '
        for username in self.followingList:
            text += '@' + username + ' '
        text += '\n\n#TootThursday'

        self.mastodon.toot(text)

    def getArticles(self):
        # read articles from rss link
        articles = feedparser.parse(RSS_SITE)
        self.articles = []
        print('selecting articles...')
        for rss in articles.entries:
            #rss = articles.entries[index]
            if Lottery(70):
                print('title:', rss.title)
                print(' * link:', rss.link)
                shortened = ShortMe(rss.link, self.apikey)
                print(' * shortened:', shortened)
                self.articles.append([rss.title, shortened])
        print('done!')

    def postMastodon(self):
        print('Posting articles')
        self.mastodon.toot("AutomagicToots de auto-promoção, " + \
                  "sem a menor vergonha na cara...")

        while self.articles:
            title, link = self.articles.pop()
            sleepMinutes(randomMinutes(10))
            print(f'Posting: {title}')
            self.mastodon.toot(f"#Lembra? {title}\n\nLink: {link}")
            if Lottery(70):
                sleepMinutes(randomMinutes(10))
                print('Posting fortune')
                self.mastodon.toot(Fortune())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs through your following list and recommend them')
    parser.add_argument("--userid", help="Your registered mastodon account at toot configuration")
    args = parser.parse_args()

    if args.userid is None:
        parser.print_usage()
        sys.exit(os.EX_NOINPUT)

    if not os.path.exists(CONFIG):
        print("ERROR: toot not configured yet.  Use toot to create your configuration.")
        sys.exit(os.EX_CONFIG)

    if not os.path.exists(APICONFIG):
        print("ERROR: no API token found for shortener")
        sys.exit(os.EX_CONFIG)

    toot = TootPostLink(args.userid)
    toot.getArticles()
    toot.postMastodon()

