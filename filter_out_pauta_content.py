#! /usr/bin/python3

import argparse
import requests


class NewFilter(object):
    def __init__(self):
        self.ParseArgs()


    def ParseArgs(self):
        parser = argparse.ArgumentParser(description='Parse last content out from large content for Unix Load On.')
        parser.add_argument('--content', dest='content',
                            help='File with topics from last talkshow.')
        parser.add_argument('--webcontent', dest='webcontent',
                            help='URL with content to be filtered out')

        args = parser.parse_args()
        self.contentFile = args.content
        self.webURL = args.webcontent

    def Out(self):
        content = []
        with open(self.contentFile) as cFD:
            for line in cFD.readlines():
                content.append(line)
        req = requests.get(self.webURL)
        for line in req.text.splitlines():
            if not line in content:
                print(line)


if __name__ == '__main__':
    filter = NewFilter()
    filter.Out()
