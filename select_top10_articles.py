#! /usr/bin/env python3

import requests
import re
import random
from typing import List
#import argparse
import time

SITE = "https://github.com"
SITE_RAW = "https://raw.githubusercontent.com"
SITE_PATH = "/helioloureiro/canalunixloadon/tree/master/pautas"

save_output = False
output_filename = None

def get_html(url: str) -> str:
    req = requests.get(url)
    if req.status_code != 200:
        raise Exception(req.text)
    return req.text


def line_match(line: str) -> bool:
    if not re.search("span", line):
        return False
    if not re.search("\.md", line):
        return False
    if not re.search("[0-9]\.md", line):
        return False
    return True

def line_html_sanitize(line: str) -> str:
    line = re.sub(".* href=\"", "", line)
    line = re.sub("\">.*", "", line)
    return line

def get_latest() -> str:
    article = []
    body = get_html(SITE + SITE_PATH)

    print(" = Articles =")
    for line in body.split('\n'):
        if not line_match(line):
            continue
        line = line_html_sanitize(line)
        print(" *", line)
        article.append(line)

    print("Latest:", sorted(article)[-1])
    return sorted(article)[-1]

def unblob(url: str) -> str:
    return re.sub("/blob", "", url)

Array = List[str]
def get_random_article(article_array: Array) -> str:
    return random.choice(article_array)

def get_articles() -> Array:
    articles = []
    latest_article = get_latest()
    print(SITE_RAW + latest_article)
    body = get_html(unblob(SITE_RAW + latest_article))
    for line in body.split("\n"):
        if not re.search("\*", line):
            continue
        articles.append(line)
    if len(articles) == 0:
        raise Exception("No articles found.")
    return articles

def get_final_article() -> str:
    articles = get_articles()
    final_article = get_random_article(articles)
    print("Article selected:", final_article)
    return final_article

def get_title(article: str) -> str:
    article = re.sub(".*\[", "", article)
    article = re.sub("\].*", "", article)
    return article

def get_link(article: str) -> str:
    article = re.sub(".*\(", "", article)
    article = re.sub("\).*", "", article)
    return article

def get_output_filename() -> str:
    if globals()["output_filename"] is None:
        output_filename = time.strftime("random_article_output-%Y-%m-%d-%H:%M:%S.log")
        globals()["output_filename"] = output_filename
    return output_filename

def save_line(article: str) -> None:
    if globals()["save_output"] is True:
        with open(output_filename, "a") as output:
            output.write(article + "\n")

def getTop(articles, nr=10):
    selected = []
    for i in range(nr):
        art = get_random_article(articles)
        print(i,") art:", art)
        articles.remove(art)
        selected.append(art)
    return {"pautas" : selected,
            "proxima" : articles }

def generatePauta(dic_articles):
    text = '''
Assuntos | link | comentários
=============================
'''
    for item in dic_articles['pautas']:
        text += item + '\n'
    text += '''

Sugestões via google forms
==========================

Sugestões via telegram
======================

Que pode ir parar no próximo programa se não der tempo
=======================================================
'''
    for item in dic_articles['proxima']:
        text += item + '\n'
    text += '''

Pra fechar
==========


'''
    return text

def printArticles():
    articles = get_articles()
    result = getTop(articles, 15)
    print(generatePauta(result))


if __name__ == '__main__':
    #parser = argparse.ArgumentParser(description="It gets a random article to be read on Unix Load On")
    #parser.add_argument("--output", action="store_true", help="It enables to save results.")
    #args = parser.parse_args()

    printArticles()

