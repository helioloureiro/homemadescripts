#! /usr/bin/env python3

from mastodon import Mastodon
import os
import sys
import feedparser
import requests
import argparse
import json
import pickle
import hashlib
import time
import random
import bs4
import tempfile
import shutil

# in the day nitter.net stops working... well... we will see.
RSS_FEED = "https://nitter.net/vagasVTNC/media/rss"
HOME = os.getenv('HOME')
CONFIG = f"{HOME}/.config/toot/config.json"
DBDATA = f"{HOME}/.config/toot/vagasVTNC.pickle"

def sleepMinutes(minutes):
    print(f'Sleeping {minutes} minutes')
    time.sleep(minutes * 60)

def randomMinutes(limit):
    return random.randint(1, limit)


def jsonPrettify(data):
    jsonData = json.loads(data)
    return json.dumps(jsonData, indent=4)

class VagasVTNCBot:
    def __init__(self, userid):
        with open(CONFIG) as tootConfig:
            config = json.load(tootConfig)

        print('Connecting to Mastodon')
        self.mastodon = Mastodon(
            access_token = config['users'][userid]['access_token'], 
            api_base_url = config['users'][userid]['instance']
            )
        self.me = self.mastodon.me()
        print('Mastodon login completed')
        print('Loading saved data')
        self.dbdata = self.loadData()
        self.posts = []

    def saveData(self, data):
        # save the last 100 entries
        if len(data) > 100:
            while len(data) > 100:
                data.remove(data[0])
        with open(DBDATA, 'wb') as dest:
            pickle.dump(data, dest)

    def loadData(self):
        # return empty structure
        if not os.path.exists(DBDATA):
            return []
        data = []
        with open(DBDATA, 'rb') as orig:
            try:
                data = pickle.load(orig, encoding='utf-8')
            except EOFError:
                print(' * empty data from DB')
                pass
        print('Existent hashes:', data)
        return data

    def getSHA256Sum(self, data):
        m = hashlib.sha256()
        try:
            m.update(data.encode('utf-8'))
        except UnicodeDecodeError as e:
            print('Failed to decode:', data)
            raise UnicodeDecodeError(e, data)
        return m.hexdigest()

    def getFeed(self):
        '''
        Read the data from twitter.
        '''
        print('Getting feed...')
        feed = feedparser.parse(RSS_FEED)
        self.rss = feed.entries

    def filterPictures(self, line):
        pictures = []
        b = bs4.BeautifulSoup(line, "html.parser")
        for img in  b.find_all('img'):
            pictures.append(img.attrs['src'])
        return pictures

    def preparePosts(self):
        '''
        From the posts found, removed the ones already sent and save state of the last one.
        '''
        print('Preparing the posts')
        # read it backwards
        self.rss.reverse()
        for r in self.rss:
            title = r.title
            message = r.title
            r_id = r.id
            link = r.link
            r_hash = self.getSHA256Sum(title + r.id)
            pictures = self.filterPictures(r.summary_detail.value)
            if not r_hash in self.dbdata:
                print(f' * adding hash: {r_hash}')
                self.posts.append({
                    "hash" : r_hash,
                    "message" : f"{message} \n\n {link}",
                    "images" : pictures
                })
            else:
                print(f'The post \"{title}\" already exists')

    def postMastodon(self):
        '''
        Post the buffered messages into Mastodon.
        '''
        for post in self.posts:
            savedFiles = self.getPictures(post['images'])
            mediaData = []
            for sf in savedFiles:
                print(f' * sending media: {sf}')
                result = self.mastodon.media_post(sf)
                print(' * media_post on mastodon:', jsonPrettify(result))
                mediaData.append(result.id)
            tootText = post['message']
            self.mastodon.status_post(tootText, media_ids=mediaData)
            self.cleanUpTempFiles(savedFiles)
            # add here info about successful posts
            self.dbdata.append(post["hash"])
            sleepMinutes(randomMinutes(5))

    def saveState(self):
        print(' * Saving data into DB')
        self.saveData(self.dbdata)

    def getPictures(self, imagesList):
        locaFiles = []
        for img in imagesList:
            imgName = tempfile.mktemp(suffix='.jpg')
            print(f' * Fetching {img} and saving into {imgName}')
            r = requests.get(img, stream=True)
            if r.status_code == 200:
                with open(imgName, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            locaFiles.append(imgName)
        return locaFiles

    def cleanUpTempFiles(self, fileNames):
        for f in fileNames:
            print(f' * Deleting: {f}')
            os.unlink(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='It posts the last published tweet')
    parser.add_argument("--userid", help="Your registered mastodon account at toot configuration")
    args = parser.parse_args()

    if args.userid is None:
        parser.print_help()
        sys.exit(os.EX_NOINPUT)

    bot = VagasVTNCBot(args.userid)
    bot.getFeed()
    bot.preparePosts()
    bot.postMastodon()
    bot.saveState()