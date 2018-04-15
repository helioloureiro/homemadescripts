#! /usr/bin/python -u
"""
Just a simple script to retrieve playlists on YouTube as print as json.

Useful to gather from another program and create info to post on Twitter.

"""

import sys
import re
import curl       # install python-pycurl
import bs4        # install python-bs4
import simplejson # install python-simplejson

YOUTUBE = "https://www.youtube.com/playlist?list="
VIDEO = "https://www.youtube.com/watch?v="

def help(errno=None):
    print "Use: %s <playlist id>" % sys.argv[0]
    if errno:
        sys.exit(errno)
    sys.exit(1)

def retrieve_html(url):
    c = curl.Curl()
    c.get(url)
    return c.body()

def main(url):
    if url is None:
        help()
    playlist_id = url
    # clean from full url alike
    # https://www.youtube.com/playlist?list=PLQYPYhKQVTvcNqNnkEfEKhaMxUf2tn_CP
    playlist_id = re.sub(".*=", "", playlist_id)

    VIDEOS = {}
    body = retrieve_html("%s%s" % (YOUTUBE, playlist_id))
    #print body
    soup = bs4.BeautifulSoup(body, 'html.parser')

    table_trs = soup.findAll('tr')
    for tr in table_trs:
        title = tr['data-title']
        VIDEOS[title] = {}

        video_url = tr['data-video-id']
        VIDEOS[title]['url'] = "%s%s" % (VIDEO, video_url)
        tr_tds = tr.findAll('td')
        for td in tr_tds:
            #print " * * ", td['class']
            if td['class'][0] == "pl-video-thumbnail":
                thumb = td.img['data-thumb']
                VIDEOS[title]['thumb'] = thumb
    return VIDEOS

if __name__ == '__main__':
    try:
        link = sys.argv[1]
    except:
        help(errno=1)
    videos = main(link)
    print simplejson.dumps(videos, sort_keys=True, indent='    ')
