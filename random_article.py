#! /usr/bin/python3

import requests
import re
import random
from typing import List
from  http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
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

articles_done = []
articles_array = []
def start_webserver():
    "src: https://www.programcreek.com/python/example/103649/http.server.BaseHTTPRequestHandler"
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            global articles_done, article_array
            self.send_response(200)
            self.send_header("Content-type", "text/html;charset=utf-8")
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
                global articles_array, articles_done
                if len(articles_array) == 0:
                    articles_array = get_articles()
                    print("Nr de artigos:", len(articles_array))

                if len(articles_array) != len(articles_done):
                    article_selected = None
                    while True:
                        article_selected = get_random_article(articles_array)
                        if not article_selected in articles_done:
                            articles_done.append(article_selected)
                            break
                    save_line(article_selected)
                    title = get_title(article_selected)
                    link = get_link(article_selected)
                    print("title:", title)
                    print("article:", article_selected)
                    response = f"""<title>{title}</title>
                    <h1>Title: <a href="{link}">{title}</a></h1><br>
                    <h2>Link: <a href="{link}">{link}</a></h2> """ + \
                    get_new_article_button
                    print("Artigos lidos:", len(articles_done))
                else:
                    response = "<h1>Todos os artigos já foram lidos</h1>"
            else:
                response = get_new_article_button
            content = bytes(response.encode("utf-8"))
            self.wfile.write(content)

    # Bind to the local address only.
    print("Starting webserver on port 8080")
    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="It gets a random article to be read on Unix Load On")
    parser.add_argument("--web", action="store_true", help="It starts web interface (port 8080)")
    parser.add_argument("--output", action="store_true", help="It enables to save results.")
    args = parser.parse_args()
    if args.output:
        print("output saving to:", get_output_filename())
        globals()["save_output"] = True
    if args.web:
        start_webserver()
    else:
        print(get_final_article())
