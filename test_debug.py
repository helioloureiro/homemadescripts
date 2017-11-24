#! /usr/bin/python -u
# -*- coding: utf-8 -*-

# Isolating the problem parts from the main program.

import telebot
import ConfigParser
import os
import time
import requests

DEBUG = True
CONFIG = ".twitterc"
HOME = os.environ.get('HOME')

def debug(msg):
    if DEBUG and msg:
        try:
            print u"[%s] %s" % (time.ctime(), msg)
        except Exception as e:
            print u"[%s] DEBUG ERROR: %s" % (time.ctime(), e)

# Get configs from .twitterc
configuration = "%s/%s" % (os.environ.get('HOME'), CONFIG)
cfg = ConfigParser.ConfigParser()
debug("Reading configuration: %s" % configuration)
if not os.path.exists(configuration):
    print "Failed to find configuration file %s" % configuration
    sys.exit(1)
cfg.read(configuration)
try:
    key = cfg.get("TELEGRAM", "STALLBOT")
    botadm = cfg.get("TELEGRAM", "STALLBOTADM")
except ConfigParser.NoSectionError:
    print "No TELEGRAM session found to retrieve settings."
    print "Check your configuration file."
    sys.exit(1)
debug("Key acquired.")

debug("Starting bot for FreeSpeech")
bot = telebot.TeleBot(key)

# Function that gets the images from the listed sites.
# The error is in here somewhere
@bot.message_handler(commands=["xkcd", "dilbert", "vidadeprogramador",
    "tirinhas", "strips", "vidadesuporte", "angulodevista",
    "mandanudes", "nudes", "mandafoods", "foods",
    "tirinhadorex", "megazine"])
def Comics(cmd):
    debug(cmd.text)
    def GetContent(url):
        if not url:
            return
        req = requests.get(url)
        if req.status_code == 200:
            text = req.text
            proto = url.split("//")[0]
            debug("GetContent: proto=%s" % proto)
            domain = url.split("//")[1]
            domain = re.sub("/.*", "", domain)
            debug("GetContent: domain=%s" % domain)
            domain = "%s//%s" % (proto, domain)
            text = re.sub(" src=//", " src=%s/" % domain, text)
            text = re.sub(" src=\"//", " src=\"%s/" % domain, text)
            text = re.sub(" src=/", " src=%s/" % domain, text)
            text = re.sub(" src=\"/", " src=\"%s/" % domain, text)
            #debug("GetContent: Full Text\n%s" % text)
            return text
        return None

    def GetImgUrl(pattern, text, step=0):
        """
        pattern = string to find
        text = html retrieved from site
        step = if in the same line or next (+1, +2, etc)
        """
        buf = text.split("\n")
        i = 0
        url_img = None
        for i in range(len(buf)):
            line = buf[i]
            if re.search(pattern, line):
                url_img = buf[i+step]
                break

        if not url_img:
            debug("GetImgUrl: no images links found")
            return None

        url = None
        if re.search("<img ", url_img):
            params = url_img.split()
            for p in params:
                if re.search("src=", p):
                    #tmp_img = p.split("=")[-1]
                    tmp_img = re.sub("^src=", "", p)
                    tmp_img = re.sub("\"", "", tmp_img)
                    url = re.sub("^\/\/", "http://", tmp_img)
                    url = re.sub("^\/", "http://", url)
                    break
        debug("GetImgUrl: %s" % url)
        return url

    def GetImg(url):
        if not url:
            return
        req = requests.get(url, stream=True)
        filename = os.path.basename(url)
        if not re.search("\.gif|\.jpg|\.png", filename):
            filename = "%s.gif" % filename
        img = "/tmp/%s" % filename
        with open(img, 'wb') as out_file:
            shutil.copyfileobj(req.raw, out_file)
        return img

    debug(cmd.text)
    img = None
    if re.search("/xkcd", cmd.text):
        url = "http://xkcd.com"
        req = requests.get(url)
        body = req.text
        buf = body.split("\n")
        i = 0
        url_img = None
        for i in range(len(buf)):
            line = buf[i]
            if re.search("<div id=\"comic\">", line):
                url_img = buf[i+1]
                break
        tmp_img = None
        if re.search("<img ", url_img):
            params = url_img.split()
            for p in params:
                if re.search("src=", p):
                    tmp_img = p.split("=")[-1]
                    tmp_img = re.sub("\"", "", tmp_img)
                    tmp_img = re.sub("^\/\/", "http://", tmp_img)
                    break
        if tmp_img:
            debug("Tmp img: %s" % tmp_img)
            req = requests.get(tmp_img, stream=True)
            filename = os.path.basename(tmp_img)
            img = "/tmp/%s" % filename
            with open(img, 'wb') as out_file:
                shutil.copyfileobj(req.raw, out_file)

    elif re.search("/dilbert", cmd.text):
        url = "http://www.dilbert.com"
        html = GetContent(url)
        img_link = GetImgUrl("img class=\"img-responsive img-comic\"", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
    elif re.search("/vidadeprogramador", cmd.text):
        url = "http://vidadeprogramador.com.br"
        html = GetContent(url)
        img_link = GetImgUrl("div class=\"tirinha\"", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
    elif re.search("/vidadesuporte", cmd.text):
        url = "http://vidadesuporte.com.br"
        html = GetContent(url)
        img_link = GetImgUrl(" 100vw, 600px", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
    elif re.search("/angulodevista", cmd.text):
        # curl -s --user-agent "Mozilla/5.0" http://angulodevista.com/ | grep "div class=\"field field-name-field-image"
        url = "http://angulodevista.com/"
        html = GetContent(url)
        img_link = GetImgUrl("div class=\"field field-name-field-image", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
    elif re.search("/tirinhadorex", cmd.text):
        # curl http://tirinhasdorex.com/ | grep "<p><img class=\"aligncenter size-full wp-image-"
        url = "http://tirinhasdorex.com/"
        html = GetContent(url)
        img_link = GetImgUrl("<p><img class=\"aligncenter size-full wp-image-", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
    elif re.search("tirinhas|strips", cmd.text):
        bot.send_message(cmd.chat.id, "No momento somente tem: /dilbert, /xkcd, /vidadeprogramador, /vidadesuporte")
        return
    elif re.search("nudes", cmd.text):
        url = "https://rms.sexy"
        bot.send_message(cmd.chat.id, "Péra... já estou tirando a roupa e ligando a webcam...")
        html = GetContent(url)
        img_link = GetImgUrl("<a href=\"/\">", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
        bot.send_message(cmd.chat.id, "Diretamente de %s" % url)
    elif re.search("foods", cmd.text):
        url = "www.foodporndaily.com"
        bot.send_message(cmd.chat.id, "Nham nham! 🍔")
        html = GetContent(url)
        img_link = GetImgUrl("<img id=\"mainPhoto\"/>", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
        bot.send_message(cmd.chat.id, "Servido por %s" % url)

    if img:
        try:
            img_fd = open(img, 'rb')
            bot.send_photo(cmd.chat.id, img_fd)
        except Exception as e:
            bot.send_message(cmd.chat.id, "Ooopsss... deu merda! %s" % e)
        os.unlink(img)
    elif re.search("megazine", cmd.text):
        megazines = [ "xkcd", "dilbert", "vidadeprogramador",
    "vidadesuporte", "angulodevista", "tirinhadorex" ]
        cmd_new = cmd
        for zine in megazines:
            cmd_new.text = "/%s" % zine
            Comics(cmd_new)
    else:
        bot.send_message(cmd.chat.id, "É... foi não...")

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Stallmanbot Debug Mode")

# Start the bot using:
# $ python2 -u test_debug.py
def main():
    try:
        debug("Polling...")
        bot.polling()
    except Exception as e:
        print e
        debug(e)

main()
