#! /usr/bin/env python3
# 
# it uses configuration from toot
import os
import json
import argparse
import sys
from mastodon import Mastodon
import random


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
        self.followingList = [ user.acct for user in self.mastodon.account_following(id=self.me.id)]
        print(self.followingList)

    def doTheLottery(self):
        sizeOfFollowing = len(self.followingList)
        tenPct = int(sizeOfFollowing * .1)
        print('Total following:', sizeOfFollowing)
        print('Number of recommendations:', tenPct)

        awardedList = []
        while tenPct > 0:
            tenPct-=1
            winner = random.choice(self.followingList)
            awardedList.append(winner)
            self.followingList.remove(winner)
        print('Awarded:', awardedList)
        self.followingList = awardedList

    def send(self):
        text = '#TT '
        for username in self.followingList:
            text += '@' + username + ' '
        text += '\n\n#TootThursday'

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
