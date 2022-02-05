#! /usr/bin/python3

import argparse
import requests
import re

GITHUB = "https://github.com"
PAUTAS = f"{GITHUB}/helioloureiro/canalunixloadon/tree/master/pautas"
RAWGITHUB = "https://raw.githubusercontent.com"


def curl(url):
    req = requests.get(url)
    if req.status_code == 200:
        return req.text
    raise Exception(f"Failed to fetch content from {url}")

def getHref(line):
    """
    <span class="css-truncate css-truncate-target d-block width-fit"><a class="js-navigation-open Link--primary" title="20220211.md" data-pjax="#repo-content-pjax-container" href="/helioloureiro/canalunixloadon/blob/master/pautas/20220211.md">20220211.md</a></span>
    """
    line = re.sub(".*href=\"", "", line)
    line = re.sub("\">.*", "", line)
    return line

def unblob(url):
    return re.sub("/blob", "", url)

class Pautas(object):
    def __init__(self): None

    def GetLatest(self):
        links = []
        pautas = curl(PAUTAS)
        for line in pautas.splitlines():
            if not re.search("js-navigation-open Link--primary", line):
                continue
            if re.search("template.md", line):
                continue
            line = getHref(line)
            links.append(line)
        self.latest = sorted(links)[-1]
        self.latest = unblob(self.latest)
        self.latestURL = f"{RAWGITHUB}{self.latest}"
        print("latest  :", self.latestURL)
        #print("expected: https://raw.githubusercontent.com/helioloureiro/canalunixloadon/master/pautas/20220210.md")

    def GetContentFromRaw(self, url):
        body = curl(url)
        content = []
        for line in body.splitlines():
            if line.startswith("*"):
                content.append(line)
                #print(line)
        self.lastContent = content


    def FetchLatestContent(self):
        self.GetLatest()
        self.GetContentFromRaw(self.latestURL)
        return self.lastContent



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

        if self.webURL is None or self.webURL == "latest":
            pauta = Pautas()
            pauta.GetLatest()
            self.webURL = pauta.latestURL


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

