#! /usr/bin/python3

import requests
import re
import random
from typing import List
from  http.server import BaseHTTPRequestHandler, HTTPServer

SITE = "https://github.com"
SITE_RAW = "https://raw.githubusercontent.com"
SITE_PATH = "/helioloureiro/canalunixloadon/tree/master/pautas"

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

def get_final_article() -> str:
    article = []
    latest_article = get_latest()
    print(SITE_RAW + latest_article)
    body = get_html(unblob(SITE_RAW + latest_article))
    for line in body.split("\n"):
        if not re.search("\*", line):
            continue
        article.append(line)
    if len(article) == 0:
        raise Exception("No articles found.")
    final_article = get_random_article(article)
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

def start():
    "src: https://www.programcreek.com/python/example/103649/http.server.BaseHTTPRequestHandler"
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            client_ip, client_port = self.client_address
            reqpath = self.path.rstrip()
            print(f"request from {client_ip}:{client_port} for {reqpath}")
            get_new_article_button = """
            <center>
            <form action="/newarticle" method="get">
             <input type="submit" value="New article">
            </form>
            </center>
            """
            if reqpath == "/newarticle?":
                article = get_final_article()
                title = get_title(article)
                link = get_link(article)
                print("title:", title)
                print("article:", article)
                response = f"""<title>{title}</title>
                <h1>Title: <a href="{link}">{title}</a></h1><br>
                <h2>Link: <a href="{link}">{link}</a></h2> """ + \
                get_new_article_button
            else:
                response = get_new_article_button
            content = bytes(response.encode("utf-8"))
            self.wfile.write(content)

    # Bind to the local address only.
    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    start()
