#! /usr/bin/env python3
# 
# it uses configuration from toot
import os
import json
import argparse
import sys
import re
import random
from mastodon import Mastodon


HOME = os.getenv('HOME')
CONFIG = f"{HOME}/.config/toot/config.json"


class TootThursday:
    def __init__(self, userid):
        with open(CONFIG) as tootConfig:
            config = json.load(tootConfig)

        self.mastodon = Mastodon(
            access_token = config['users'][userid]['access_token'], 
            api_base_url = config['users'][userid]['instance']
            )
        self.me = self.mastodon.me()
        print('Login executed')
    

    def getFollowing(self):
        reference = self.mastodon.account_following(id=self.me.id)
        following = self.mastodon.fetch_remaining(reference)
        self.followingList = [ user.acct for user in  following]
        print(self.followingList)

    def doTheLottery(self):
        sizeOfFollowing = len(self.followingList)
        tenPct = int(sizeOfFollowing * .1)
        print('Total following:', sizeOfFollowing)
        print('Number of recommendations:', tenPct)

        awardedList = []
        while tenPct > 0:
            winner = random.choice(self.followingList)
            ## skip myself
            if re.search("helioloureiro", winner):
                continue
            awardedList.append(winner)
            self.followingList.remove(winner)
            tenPct-=1
        print('Awarded:', awardedList)
        self.followingList = awardedList

    def send(self):
        text = '#TT \n'
        footer = '\n#TootThursday'
        size_limit = 500 # from mastodon page
        for username in self.followingList:
            username = '@' + username + '\n'
            ## check message limit at every entry
            if len(text + username + footer) > size_limit:
                break
            text += username
        text += footer
        self.mastodon.toot(text)



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

    tt = TootThursday(args.userid)
    tt.getFollowing()
    tt.doTheLottery()
    tt.send()
