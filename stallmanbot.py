#! /usr/bin/python3 -u
# -*- coding: utf-8 -*-

import os
import sys
import configparser
import re
import time
import shutil
import random
import pickle
import json
import syslog
import subprocess
import requests
import bs4
import telebot
from datetime import date, datetime
import threading

# pyTelegramBotAPI
# https://github.com/eternnoir/pyTelegramBotAPI
# pip3 install pyTelegramBotAPI


__version__ = "Fri Feb 28 13:43:12 CET 2020"

START_TIME = time.ctime()


# Message to send to @BotFather about its usage.
Commands_Listing = """

Open a talk to @BotFather and send these commands
using "/setcommands"

== Super ultra bot.==

oi - Hummm... então tá.
ultrafofos - Quem são, o que são e como vivem.
photo - Maravilhos nudes livres. Sério.
rtfm - O que todo mundo já devia saber.
distro - Use: distro <suadistro>. Uma fofurinha sobre sua distro favorita. Ou não.
xkcd - Sua dose diária de humor ácido do xkcd.
dilbert - Sua dose diária de humor corporativo.
vidadeprogramador - Sua dose diária de Alonzo.
vidadesuporte - Sua dose diária de chamados no helpdesk.
tirinhadorex - Tirinhas meio emo.
fofometro - Quão fofo você é? Tente.
fofondex - Ranking de fofura.
blobometro - Quão blob você é? Tente.
blobondex - Ranking de blobice.
fortune - A sorte do dia.  Ou não.
date - A data atual.
uptime - Somente os fortes entenderão.
mandanudes - Pura sensualidade.
mandafoods - Aquele nham-nham pra deixar seu dia mais alegre! 💞
nudes - Sensualidade dum jeito mais rápido.
foods - Fome de um jeito mais rápido.
emacs - Religião é coisa séria.  Principalmente a parte do vinho e pecado.
motivational - Pra melhorar *aquela* segunda-feira.
dia - Pra saber em qual dia da semana estamos. Ou não.
blob - Quem não precisa de firmware pra funcionar?
mimimi - Mande: /mimimi frase.
bomdia - Assim que se começa um dia de verdade.
fontes - Pra ter livre acesso ao conteúdo.
oiamor - Também te amo.
fuda - Os males do software livre.
hacked - Shame, shame, shame...
corona - status do corona virus
version - versão do bot
"""

DEBUG = True
CONFIG = ".twitterc"
HOME = os.environ.get('HOME')
PIDFILE = "%s/.stallmanbot.pid" % HOME
PAUTAS = "%s/canalunixloadon/pautas" % HOME
IMGDIR = "%s/motivational" % HOME
SCRIPTHOME = "%s/homemadescripts" % HOME
FOFODB = "%s/fofondex.db" % HOME
MANDAFOODSFILE = "%s/foodporn.json" % HOME
FOODPORNURL = "https://www.reddit.com/r/foodporn.json?sort=new"
simple_lock = False  # very simple lock way
botadm, cfg, key, configuration = None, None, None, None

GIFS = {
        "no_wait": [
                "https://media.giphy.com/media/3ohk2t7MVZln3z8rrW/giphy.gif",
                "https://media.giphy.com/media/l3fzIJxUF2EpGqk48/giphy.gif",
                "https://media.giphy.com/media/hbqoS6tq5CMtq/giphy.gif",
                "https://media.giphy.com/media/l3fzQLOZjieBbUGv6/giphy.gif"
                ],
        "popcorn": [
                "https://media.giphy.com/media/MSapGH8s2hoNG/giphy.gif",
                "https://media.giphy.com/media/51sOSwMffAAuY/giphy.gif",
                 "https://media.giphy.com/media/TrDxCdtmdluP6/giphy.gif"
                 ],
        "coffee": [
                "https://media.giphy.com/media/3owvK3nt6hDUbcWiI0/giphy.gif",
                "https://media.giphy.com/media/DrJm6F9poo4aA/giphy.gif",
                "https://media.giphy.com/media/MKkpDUqXFaL7O/giphy.gif",
                "https://media.giphy.com/media/oZEBLugoTthxS/giphy.gif"
                ],
        "shame": [
                "https://media.giphy.com/media/vX9WcCiWwUF7G/giphy.gif",
                   "https://media.giphy.com/media/eP1fobjusSbu/giphy.gif",
                   "https://media.giphy.com/media/SSX4Sj7oB0cWQ/giphy.gif",
                   "https://media.giphy.com/media/m6ljvZNi8xnvG/giphy.gif"
                   ],
        "boyola": [
                "https://media.giphy.com/media/3owvJYxTqRz6w5chwc/giphy.gif"
                ],
        "approval": [
                "https://media.giphy.com/media/xSM46ernAUN3y/giphy.gif",
                "https://media.giphy.com/media/3ohhwp0HAJ2R49xNks/giphy.gif",  # thumbs up
                "https://media.giphy.com/media/3owvK1HepTg3TnLRhS/giphy.gif"
                ],
        "ban": [
                "https://media.giphy.com/media/xT5LMDzs9xYtHXeItG/giphy.gif",
                "https://media.giphy.com/media/H99r2HtnYs492/giphy.gif",
                "https://media.giphy.com/media/l2JebrcLzSVLwCYEM/giphy.gif",
                "https://media.giphy.com/media/10A60gknFNLUVq/giphy.gif"
                ],
        "helio": [
            "https://media.giphy.com/media/l3fzBbBklSWVRPz9K/giphy.gif",  #colors
            "https://media.giphy.com/media/hbqoS6tq5CMtq/giphy.gif",  #facepalm
            "https://media.giphy.com/media/SYEskzoOgwxWM/giphy.gif",  #hacker
            "https://media.giphy.com/media/MKkpDUqXFaL7O/giphy.gif",  #coffee
            "https://media.giphy.com/media/KsW4LMQRO1YLS/giphy.gif",  #treta
            "https://media.giphy.com/media/qkXhEeRO3Rrt6/giphy.gif",  #tasqueopariu
            "https://media.giphy.com/media/51sOSwMffAAuY/giphy.gif",  #pipoca
            "https://media.giphy.com/media/3ohhwwnixgbdViKREI/giphy.gif", # kannelbulla
            "https://media.giphy.com/media/l378zoQ5oTatwi2li/giphy.gif", # eye sight
            "https://media.giphy.com/media/3ov9jNAyexHvu0Ela0/giphy.gif", # send bun
            "https://media.giphy.com/media/3ohhwp0HAJ2R49xNks/giphy.gif", # thumbs up
            "https://media.giphy.com/media/3ohhwneKeCkbALPcKk/giphy.gif", # tinder
            "https://media.giphy.com/media/xT9IgqIuvUoKD5oliw/giphy.gif", # irony
            "https://media.giphy.com/media/MSapGH8s2hoNG/giphy.gif"
                ],
        "nudes": [
            "https://media.giphy.com/media/PpNTwxZyJUFby/giphy.gif",
            "https://media.giphy.com/media/q4cdfs7GcvzG0/giphy.gif",
            "https://media.giphy.com/media/ERay9nmFB027m/giphy.gif",
            "https://media.giphy.com/media/t7NsoBIxIT4mQ/giphy.gif",
            "https://media.giphy.com/media/Hbutx0s2ZYZyw/giphy.gif",
            "https://media.giphy.com/media/l3vQWJaua7jOns9dC/giphy.gif",
            "https://media.giphy.com/media/3o6ZsTf2gnGE5liGdi/giphy.gif",
            "https://media.giphy.com/media/NK2UQa6mbtrW0/giphy.gif",
            "https://media.giphy.com/media/l0HlK37zDy1JsJnji/giphy.gif",
            "https://media.giphy.com/media/3oz8xWkBckB1SbmAXC/giphy.gif",
            "https://media.giphy.com/media/MFFyKHqLNe9cQ/giphy.gif",
            "https://media.giphy.com/media/l2JdXY0zQv7uN0uVG/giphy.gif",
            "https://media.giphy.com/media/GqxwTEeHIeMo0/giphy.gif",
            "https://media.giphy.com/media/10yqoCYci3xxn2/giphy.gif",
            "https://media.giphy.com/media/hx9SHiDED2nv2/giphy.gif"
            ],
        "aprigio": [
            "https://media.giphy.com/media/l3fzQbp5wdi2HiSCk/giphy.gif",
            "https://media.giphy.com/media/3o7aD1O0sr60srwU80/giphy.gif"
            ],
        "treta": [
            "https://media.giphy.com/media/KsW4LMQRO1YLS/giphy.gif"
            ],
        "anemonos": [
            "https://media.giphy.com/media/SYEskzoOgwxWM/giphy.gif"
            ],
        "tasqueopariu": [
            "https://media.giphy.com/media/qkXhEeRO3Rrt6/giphy.gif"
            ],
        "diego": [
            "https://media.giphy.com/media/3o7aDdlF3viwGzKJZ6/giphy.gif",
            "https://media.giphy.com/media/QN451Wg12SilkyRU3l/giphy.gif"
            ],
        "patola": [
            "https://media.giphy.com/media/1gdwLUi5QUzKDUx7U8/giphy.gif",
            "https://media.giphy.com/media/1qefNEESPpMthOeEZ8/giphy.gif"
            ],
        "spock": [
            "https://media.giphy.com/media/26vIdECBsGvzl9pxS/giphy.gif",
            "https://media.giphy.com/media/CSXoBa3YNXk0U/giphy.gif",
            "https://media.giphy.com/media/eSXWZ93nNrq00/giphy.gif",
            "https://media.giphy.com/media/AxgpnA3X092Zq/giphy.gif",
            "https://media.giphy.com/media/F2fv3bjPnYhKE/giphy.gif",
            "https://media.giphy.com/media/CSXoBa3YNXk0U/giphy.gif",
            "https://media.giphy.com/media/CidfkCKipW1sQ/giphy.gif",
            ],
        "bun": [
            "https://media.giphy.com/media/3ov9jNAyexHvu0Ela0/giphy.gif"
            ],
        "coc": [
            "https://media.giphy.com/media/OT5oCJMFLq0wZ2xuX8/giphy.gif"
            ],
        "mimimi": [
            "https://media.giphy.com/media/ylPWDQuapyexa/giphy.gif"
            ],
        "nanga": [
            "https://media.giphy.com/media/RCBQSWiMPTQly/giphy.gif"
            ],
        "tinder": [
            "https://media.giphy.com/media/3ohhwneKeCkbALPcKk/giphy.gif"
            ],
        "wtf": [
            "https://media.giphy.com/media/l378zoQ5oTatwi2li/giphy.gif"
            ], # eye sight
        "ironia": [
            "https://media.giphy.com/media/xT9IgqIuvUoKD5oliw/giphy.gif"
            ], # irony
        "segundas": [
            "https://media.giphy.com/media/nDZ3OkpknpElZdseUb/giphy.gif"
            ],
        "estudar": [
            "https://media.giphy.com/media/MSfMd1JFtnZfj644Tl/giphy.gif"
            ],
        "truta": [
            "https://media.giphy.com/media/EBTvp73wY274d1peTg/giphy.gif"
            ],
        "chora": [
            "https://img.devrant.com/devrant/rant/r_1195970_gW3o6.jpg"
            ],
        "cloud": [
            "https://img.devrant.com/devrant/rant/r_257328_MK4Rv.jpg"
            ],
        "non-free": [
            "https://img.devrant.com/devrant/rant/r_1857481_trzgo.jpg"
            ],
        "fe-amo": [
            "https://dinofauro.com.br/loja/wp-content/uploads/2016/05/Caneca-Fe-amo-3.png"
            ]
        }

GIFS["pipoca"] = GIFS["popcorn"]
GIFS["vergonha"] = GIFS["shame"]
GIFS["cafe"] = GIFS["coffee"]
GIFS["pera"] = GIFS["no_wait"]

FAILURES = [
    "https://media.giphy.com/media/LDay3WufGjxEA/giphy.gif",
    "https://media.giphy.com/media/5AlEvP1UEeecg/giphy.gif",
    "https://media.giphy.com/media/5xaOcLyxnN1UxgqDTuU/giphy.gif",
    "https://media.giphy.com/media/vPH4IIua3umxG/giphy.gif",
    "https://media.giphy.com/media/8LkXSrAACvLAA/giphy.gif",
    "https://media.giphy.com/media/nEovVMM8Z5H6U/giphy.gif"
    ]

RESPONSES_TEXT = {
    "starttime": START_TIME,
    "kkkk": "Hilário.",
    "hahaha": "Hilário.",
    "fonte": """Estou aqui com 100% de acesso ao conteúdo em:

https://github.com/helioloureiro/homemadescripts/blob/master/stallmanbot.py
""",
    "blob": """
Blob nosso que estais no kernel
codificado seja o vosso nome.
Venha a nós o vosso driver.
Seja feita integração com vontade,
assim no kernel como no shell.
O patch nosso de cada dia nos dai hoje.
Perdoai os nossos scripts,
assim com nós perdoamos a quem é ultrafofo.
Não nos deixei cair de uptime.
Mas livrai-nos do FUDA,

Amuleke!
""",
    "emacs": """
Linux nosso que estais no PC
Bem compilado seja o vosso Kernel
Venha a nós o vosso código
Seja feita a vossa tarball
Assim em casa como no trabalho
O bit nosso de cada dia seja escovado
Apagai com rm -rf
Para nunca mais recuperar o que foi perdido
E não nos deixeis errar a compilação
E livrai a todos da M$

Amém.
""",
    "ping": "ACK",
    "version": __version__,
    "starttime": START_TIME,
    "ultrafofo": """#UltraFofos é o grupo super fofis de defensores de software livre.
Veja mais em: https://www.youtube.com/watch?v=eIRk38d32vA
""",
    "help": """Precisa de ajuda?
Procure o CVV.

http://www.cvv.org.br
""",
    "rtfm": """Read The F*cking Manual.  Ou leia o Guia Foca GNU/Linux.

http://www.guiafoca.org/
"""
}

# Aliases
RESPONSES_TEXT[u"fontes"] = RESPONSES_TEXT["fonte"]
RESPONSES_TEXT[u"src"] = RESPONSES_TEXT["fonte"]
RESPONSES_TEXT[u"source"] = RESPONSES_TEXT["fonte"]
RESPONSES_TEXT[u"pong"] = RESPONSES_TEXT["ping"]
RESPONSES_TEXT[u"ajuda"] = RESPONSES_TEXT["help"]
RESPONSES_TEXT[u"ultrafofos"] = RESPONSES_TEXT["ultrafofo"]

LOGTAG = "StallNoMan"


# Refactoring
# Applying the concepts from clean code (thanks uncle Bob)
def set_debug():
    global DEBUG
    if DEBUG is False:
        if "DEBUG" in os.environ:
            DEBUG = True


def debug(*msg):
    if DEBUG and msg:
        timestamp = "[%s]" % time.ctime()
        allText = " ".join(str(x) for x in msg)
        try:
            print(timestamp, *msg)
            syslog.openlog(LOGTAG)
            syslog.syslog(syslog.LOG_DEBUG, allText)
        except Exception as e:
            print(f"{timestamp} DEBUG ERROR:", e)


def error(message):
    """Error handling for logs"""
    errormsg = "ERROR: %s" % message
    debug(errormsg)
    syslog.openlog(LOGTAG)
    syslog.syslog(syslog.LOG_ERR, errormsg)


def log(message):
    """Syslog handling for logs"""
    infomsg = "%s" % message
    debug(infomsg)
    syslog.openlog(LOGTAG)
    syslog.syslog(syslog.LOG_INFO, infomsg)


def read_file(filename):
    try:
        with open(filename) as myfile:
            return myfile.read()
    except FileNotFoundError:
        error("File not found: %s" % filename)
        return None
    except Exception as e:
        error("Failed to read file %s: %s" % (filename, e))
        return None


def check_if_run():
    pid = read_file(PIDFILE)
    current_pid = os.getpid()
    if pid is None:
        return
    if int(pid) > 0 and int(pid) != current_pid:
        if os.path.exists("/proc/%d" % int(pid)):
            log("[%s] Already running - keepalive done." % time.ctime())
            sys.exit(os.EX_OK)


def save_file(content, filename):
    """Snippet to write down data"""
    with open(filename, 'w') as fd:
        fd.write(content)


def read_configuration(config_file):
    """ Read configuration file and return object
    with config attributes"""
    cfg = configparser.ConfigParser()
    debug("Reading configuration: %s" % config_file)
    if not os.path.exists(config_file):
        error("Failed to find configuration file %s" % config_file)
        sys.exit(os.EX_CONFIG)
    with open(config_file) as fd:
        cfg.read_file(fd)
    return cfg


def get_telegram_key(config_obj, parameter):
    """Read a parameter from configuration object for TELEGRAM
    and return it or exit on failure"""
    debug("get_telegram_key()")
    config_section = "TELEGRAM"
    value = None
    try:
        value = config_obj.get(config_section, parameter)
    except configparser.NoOptionError:
        print("No %s session found to retrieve settings." % config_section)
        print("Check your configuration file.")
        # keep going and just return null
    debug(" * value=%s" % value)
    debug(" * Key acquired (%s=%s)." % (parameter, value))
    return value


def get_foodporn_json():
    """Retrieve json data from reddit"""
    debug("get_foodporn_json()")
    request = requests.get(FOODPORNURL)
    if request.status_code != 200:
        text = get_foodporn_json()
    else:
        text = requests.text
    return text


def dump_foodporn(json_data):
    """Save json data for later"""
    debug("dump_foodporn()")
    save_file(json_data, MANDAFOODSFILE)


def is_foodporn_outdated(days=10):
    """Check if modification time is too old or not."""
    stat = os.stat(MANDAFOODSFILE)
    foods_file_date = datetime.fromtimestamp(stat.st_mtime)
    now = datetime.now()
    delta = now - foods_file_date
    if delta > days:
        return True
    return False


def is_foodporn_empty():
    """Check file size and returns true if empty."""
    stat = os.stat(MANDAFOODSFILE)
    if stat.st_size == 0:
        return True
    return False


def GetFood():
    """
    Fetch foodporn json if current data is outdated (10 days)
    and store into the json file for reading later.
    This function is ready for threading.
    """
    debug("GetFood() started")
    file_exists = False
    text = None

    if not os.path.exists(MANDAFOODSFILE):
        debug(" * MANDAFOODSFILE doesn't exist")
        text = get_foodporn_json()
    else:
        debug(" * MANDAFOODSFILE is there")
        if is_foodporn_empty == 0:
            debug(" * MANDAFOODSFILE is empty")
            os.unlink(MANDAFOODSFILE)
            text = get_foodporn_json()
        else:
            if is_foodporn_outdated():
                debug(" * json outdated - downloading foodporn")
                text = get_foodporn_json()
            else:
                text = open(MANDAFOODSFILE).read()
                file_exists = True
    j = json.loads(text)
    if 'error' in j:
        debug(" * error found on json parsing")
        if file_exists:
            os.unlink(MANDAFOODSFILE)
        GetFood()
    else:
        debug(" * GetFood() is completed")
        if not file_exists:
            debug(" * Saving into MANDAFOODSFILE")
            dump_foodporn(text)


def get_answer(question):
    """ Search for a response from dictionary """
    if question.lower() in RESPONSES_TEXT:
        return RESPONSES_TEXT[question.lower()]
    return None


def reply_text(obj, session, text):
    """ Generic interface to answer """
    try:
        obj.reply_to(session, text)
    except Exception as e:
        error("%s" % e)


def StartUp():
    debug("Startup")
    if os.path.exists(SCRIPTHOME):
        os.chdir(SCRIPTHOME)
        oscmd = "git pull -f"
        debug(oscmd)
        os.system(oscmd)
        botname = "stallmanbot.py"
        debug(oscmd)
        # For debugging outside of the Raspberry Pi
        # oscmd = "diff -q %s %s/homemadescripts/%s" % (botname, HOME, botname)
        # Original Raspberry Pi command
        oscmd = "diff -q %s %s/bin/%s" % (botname, HOME, botname)
        res = os.system(oscmd)
        if res:
            # new version detected
            res = os.system("%s %s check" % (sys.executable, sys.argv[0]))
            if res != 0:
                debug("Versão bugada")
                sys.exit(os.EX_OSERR)
            debug("Updating bot...")
            shutil.copy(botname, "%s/bin/%s" % (HOME, botname))
            debug("Bot version updated.")
            # check first
            debug("Calling restart")
            python = sys.executable
            os.execl(python, python, *sys.argv)


def GetGif(theme):
    if theme not in GIFS:
        return None
    sizeof = len(GIFS[theme])
    if sizeof <= 1:
        return GIFS[theme][0]
    get_id = random.randint(0, sizeof - 1)
    return GIFS[theme][get_id]


def main():
    """Main settings"""
    check_if_run()
    save_file("%d\n" % os.getpid(), PIDFILE)
    StartUp()


def get_global_keys():
    """Read globa settings like telegram key API"""
    debug("get_global_keys()")
    global botadm, key, allowed_users
    configuration = "%s/%s" % (os.environ.get('HOME'), CONFIG)
    cfg = read_configuration(configuration)
    key = get_telegram_key(cfg, "STALLBOT")
    botadm = get_telegram_key(cfg, "STALLBOTADM")
    allowed_users = get_telegram_key(cfg, "ALLOWEDUSERS")


# Bot callbacks below #
def get_random_link(links_array):
    """Return random line w/ link (expected array of links)"""
    debug("get_random_link()")
    size = len(links_array)
    position = random.randint(0, size - 1)
    return links_array[position]


def send_animated_image_by_link_to_chat(obj, chat_id, image_link):
    """Send a specific animated gif to a chat"""
    debug("send_animated_image_by_link_to_chat()")
    try:
        obj.send_document(chat_id, image_link)
    except Exception as e:
        error("Failed to send image=%s to chat_id=%s: %s" % \
            (image_link, chat_id, e))


def send_message_to_chat(obj, chat_id, message):
    """Send a specific message to a chat"""
    debug("send_message_to_chat()")
    try:
        obj.send_message(chat_id, u"%s" % message)
    except Exception as e:
        error("Failed to send message=%s to chat_id=%s: %s" % \
            (message, chat_id, e))


def shit_happens(obj, chat_id, error):
    """Send error back"""
    debug("shit_happens()")
    gif = get_random_link(FAILURES)
    send_animated_image_by_link_to_chat(chat_id, gif)
    send_message_to_chat(obj, chat_id, str(error))


def hello_world(obj, cmd):
    debug("hello_world()")
    debug(cmd.text)
    if re.search("oiamor|teamo", cmd.text):
        fe_amo = GetGif("fe-amo")
        try:
            obj.send_photo(cmd.chat.id, fe_amo)
        except Exception as e:
            error("hello_world() failed to send photo: %s" % e)
            pass
        obj.reply_to(cmd, u"Te amo também.")
        return
    send_message_to_chat(obj, cmd.chat.id, "OSI world")

def Manda(obj, cmd):
    debug(cmd.text)
    args = cmd.text.split()
    opts = GIFS.keys()

    def GenerateButtons(chat_id):
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, selective=True)
        for key in sorted(opts):
            item = telebot.types.KeyboardButton("/manda %s" % key)
            markup.add(item)
        obj.reply_to(cmd, "Escolha a opção:", reply_markup=markup)

    if len(args) <= 1:
        try:
            size_GIFS = len(GIFS)
            GenerateButtons(cmd.chat.id)

        except Exception as e:
            try:
                obj.send_message(cmd.chat.id, u"Deu merda... %s" % e)
            except Exception as z:
                debug(u"%s" % z)
        return
    for theme in args[1:]:
        debug(u"Manda(): theme=%s" % theme)
        gif = GetGif(theme)
        if gif is None:
            GenerateButtons(cmd.chat.id)
            return
        try:
            debug(u"Manda(): sending gif=%s" % gif)
            if re.search(".(jpg|jpeg|JPG|JPEG|png|PNG)$", gif):
                obj.send_photo(cmd.chat.id, gif)
            else:
                obj.send_document(cmd.chat.id, gif)
        except Exception as e:
            try:
                obj.send_message(cmd.chat.id, "<img src=\"%s\">"% gif)
            except Exception as err2:
                try:
                    obj.send_message(cmd.chat.id, "Deu merda... %s" % err2)
                    obj.send_message(cmd.chat.id, "Link: %s" % gif)
                except Exception as z:
                    print(u"%s" % z)
        debug(u"Manda(): end of for interaction - can go next")
    debug(u"Manda(): end of loop for")
    # remove button if there
    try:
        debug(u"Manda(): Removing buttons...")
        markup = telebot.types.ReplyKeyboardRemove(selective=True)
        obj.send_message(cmd.chat.id, "", reply_markup=markup)
    except Exception as e:
        debug("Error at Manda(): %s" % e)
    debug(u"Manda(): end of function")


def PipocaGif(obj, cmd):
    gif = GetGif("popcorn")
    try:
        obj.send_document(cmd.chat.id, gif)
    except Exception as e:
        try:
            obj.send_message(cmd.chat.id, u"Deu merda... %s" % e)
        except Exception as z:
            print(u"%s" % z)
    debug("tchau")

def Reload(obj, cmd):
    global START_TIME
    debug(cmd.text)
    if not cmd.from_user.username == botadm:
        obj.reply_to(cmd, "Só patrão pode isso.")
        return
    try:
        debug(cmd)
        obj.reply_to(cmd, "Reloading...")

        if os.path.exists(SCRIPTHOME):
            os.chdir(SCRIPTHOME)
            oscmd = "git pull -f"
            debug(oscmd)
            os.system(oscmd)
            botname = "stallmanbot.py"
            debug(oscmd)
            oscmd = "diff -q %s %s/bin/%s" % (botname, HOME, botname)
            res = os.system(oscmd)
            if res:
                # new version detected
                res = os.system("%s %s" % (sys.executable, sys.argv[0]))
                if res != 0:
                    debug("Versão bugada")
                    obj.send_message(cmd.chat.id, "Python crashed.  Vou carregar saporra não.  Vai que...")
                    return
                debug("Updating bot...")
                shutil.copy(botname, "%s/bin/%s" % (HOME, botname))
                obj.send_message(cmd.chat.id, "Bot version updated.")
        # check first
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        try:
            obj.reply_to(cmd, u"Deu merda... %s" % e)
        except Exception as z:
            print(u"%s" % z)


def ToggleDebug(obj, cmd):
    global DEBUG
    debug(cmd.text)
    if not cmd.from_user.username == botadm:
        obj.reply_to(cmd, "Só patrão pode isso.")
        return
    try:
        debug(cmd)
        if DEBUG is True:
            DEBUG = False
            status = "disabled"
        elif DEBUG is False:
            DEBUG = True
            status = "enabled"
        obj.reply_to(cmd, "debug=%s" % status)
    except Exception as e:
        print(u"%s" % e)


def fuda(obj, cmd):
    debug("Running: %s" % cmd.text)
    try:
        resp = u"FUDA: Fear, Uncertainty, Doubt and Anahuac.  " + \
            u"Os males do software livre atualmente."
        obj.reply_to(cmd, "%s" % resp)
    except Exception as e:
        print(u"%s" % e)


def sanitize(message):
    debug("Called sanitize with: %s" % message)
    if len(message) < 2:
        return ""
    for i in message:
        debug("%s (%d)" % (i, ord(i)))
    if message[0] == '/':
        message = message[1:]
    sanitize = re.sub(";.*", "", message)
    debug("sanitize_1: %s" % sanitize)
    sanitize = re.sub("|.*", "", sanitize)
    debug("sanitize_2: %s" % sanitize)
    sanitize = re.sub("@.*", "", sanitize)
    debug("sanitize_3: %s" % sanitize)
    sanitize = re.sub("&.*", "", sanitize)
    debug("sanitize_4: %s" % sanitize)
    sanitize = re.sub("[^A-Za-z0-9./-]", " ", sanitize)
    debug("sanitize_5: %s" % sanitize)
    sanitize = re.sub("sudo ", "", sanitize)
    debug("sanitize_6: %s" % sanitize)
    sanitize = re.sub("su ", "", sanitize)
    debug("sanitize_7: %s" % sanitize)
    sanitize = re.sub("&%d;&%d; " % (ord('s'), ord('u')), "", sanitize)
    debug("sanitize_8: %s" % sanitize)
    sanitize = re.sub("&%d;&%d;&%d;&%d; " %
        (ord('s'), ord('u'), ord('d'), ord('o')),
        "",
        sanitize)
    debug("sanitize_9: %s" % sanitize)
    return sanitize


def SysCmd(obj, cmd):
    debug("Running: %s" % cmd.text)
    cleanedMessage = sanitize(cmd.text)
    if len(cleanedMessage) == 0:
        debug("Sanitization removed everything.")
        try:
            obj.reply_to(cmd, "Sanitization cleaned too much...")
        except Exception as e:
            debug(e)
            obj.reply_to(cmd, e)
        return
    debug("Sanitized: %s" % cleanedMessage)
    try:
        # resp = os.popen(sanitize[1:]).read()
        resp = subprocess.check_output(cleanedMessage.split())
        debug("Popen response: %s" % resp)
        resp = re.sub("GNU", "OSI", resp)
        debug("Response: %s" % resp)
        if len(resp) == 0:
            obj.reply_to(cmd, "Shell command returned empty...")
        else:
            obj.reply_to(cmd, "%s" % resp)
    except Exception as e:
        debug(e)
        try:
            obj.send_message(cmd.chat.id, "Deu merda... %s" % e)
        except Exception as z:
            print(u"%s" % z)
    debug("done here")


def Requer(obj, cmd):
    debug(cmd.text)
    try:
        if re.search("sudo rm -rf /", cmd.text):
            gif = "https://media.giphy.com/media/7cxkulE62EV2/giphy.gif"
            obj.send_document(cmd.chat.id, gif)
            return
        obj.reply_to(cmd, "Ah lá... achando que é réquer.")
    except Exception as e:
        try:
            obj.reply_to(cmd, "Deu merda... %s" % e)
        except Exception as z:
            print(u"%s" % z)


def Fortune(obj, cmd):
    fortune = os.popen("/usr/games/fortune").read()
    # avoid big answers
    while (len(fortune) > 200):
        fortune = os.popen("/usr/games/fortune").read()
    try:
        obj.reply_to(cmd, "%s" % fortune)
    except Exception as e:
        obj.reply_to(cmd, "Deu merda... %s" % e)


def Hacked(obj, cmd):
    try:
        obj.reply_to(cmd, u"This is the gallery of metions from those who dared to hack, and just made it true.")
        obj.reply_to(cmd, u"Helio is my master but Maycon is my hacker <3 (Hack N' Roll)")
        gif = "https://media.giphy.com/media/26ufcVAp3AiJJsrIs/giphy.gif"
        obj.send_document(cmd.chat.id, gif)
    except Exception as e:
        obj.reply_to(cmd, "Deu merda... %s" % e)


def AptCmds(obj, session):
    debug(session.text)
    if re.search("apt-get", session.text):
        try:
            obj.reply_to(session, "Esse bot tem poderes de super vaca.")
            counter = random.randint(0,10)
            while counter:
                counter -= 1
                time.sleep(random.randint(0,10))
                moo = "moo" + random.randint(0,10) * "o"
                obj.send_message(session.chat.id, moo)
        except Exception as e:
            obj.reply_to(session, "apt-get deu BSOD... %s" % e)
        return
    elif re.search("aptitude", session.text):
        try:
            obj.reply_to(session,
                "Palavra africana para: Eu não sei corrigir dependências.")
        except Exception as e:
            obj.reply_to(session, "Deu merda... %s" % e)
        return
    elif re.search("apt", session.text):
        debug("On apt")
        try:
            debug("Post on session")
            obj.reply_to(session,
                u"Palavra hipster para: Eu gosto de ver tudo colorido.")
        except Exception as e:
            debug(e)
            obj.reply_to(session, "Deu merda... %s" % e)
        return
    debug("Asking about it on apt loop.")
    obj.reply_to(session, u"Quê?")


def Dia(obj, cmd):
    debug(cmd.text)
    try:
        hoje = date.today()
        semana = hoje.weekday()

        if re.search("bom", cmd.text):
            obj.reply_to(cmd,
            u"""Bom dia pra todos vocês que usam blobs, e pra quem usa GNU também.

O nome do sistema operacional é OSI/Linux e os blobs nos representam.""")

        if semana == 0:
            obj.reply_to(cmd, u"Segunda-Feira sempre tem alguem assim: https://www.youtube.com/watch?v=rp34FE01Q3M")
        elif semana == 1:
            obj.reply_to(cmd, u"Terça Feira: https://www.youtube.com/watch?v=V7eR6wtjcxA")
        elif semana == 2:
            obj.reply_to(cmd, u"Quarta Feira")
        elif semana == 3:
            obj.reply_to(cmd, u"Quinta Feira")
        elif semana == 4:
            obj.reply_to(cmd, u"Sexta-Feira é o dia da Maldade: https://www.youtube.com/watch?v=qys5ObMiKDo")
        elif semana == 5:
            obj.reply_to(cmd, u"https://www.youtube.com/watch?v=rX2Bw-mwnOM")
        elif semana == 6:
            obj.reply_to(cmd, u"Domingo é dia de compilar um kernel")
    except Exception as e:
        obj.reply_to(cmd, "Deu merda... %s" % e)


def Photo(obj, cmd):
    debug("Photo")
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    SAVEDIR = "%s/weather/%s/%s" % (os.environ.get('HOME'), year, month)
    if not os.path.exists(SAVEDIR):
        debug(u"Sem fotos")
        obj.reply_to(cmd, u"Sem fotos no momento.")
        return
    photos = os.listdir(SAVEDIR)
    last_photo = sorted(photos)[-1]
    debug(u"Última foto: %s" % last_photo)
    tagname = os.path.basename(last_photo)
    try:
        obj.reply_to(cmd, "Última foto: %s" % tagname)
        ph = open("%s/%s" % (SAVEDIR, last_photo), 'rb')
        obj.send_photo(cmd.chat.id, ph)
        #bot.send_photo(cmd.chat.id,"FILEID")
    except Exception as e:
        obj.reply_to(cmd, "Deu merda: %s" % e)


def UnixLoadOn(obj, cmd):
    debug("Unix Load On")
    msg = None
    curdir = os.curdir
    def get_what_is():
        url = "https://helioloureiro.github.io/canalunixloadon/"
        www = requests.get(url)
        msg = www.text
        msg = msg.encode("utf-8")
        debug(msg)
        soup = bs4.BeautifulSoup(msg, "html")
        msg = ""
        for section in soup.findAll("section"):
            buf = section.getText(separator='\n')
            debug(buf)
            msg += buf
            msg += "\n"
        return msg

    def get_last_pauta():
        os.chdir(PAUTAS)
        os.system("git pull --rebase --no-commit --force")
        pautas = os.listdir(PAUTAS)
        last_pauta = sorted(pautas)[-1]
        if not re.search("^20", last_pauta):
            last_pauta = sorted(pautas)[-2]
        return last_pauta

    def read_pauta(filename=None):
        if filename is None:
            last_pauta = get_last_pauta()
        else:
            last_pauta = filename
        msg = open("%s/%s" % (PAUTAS, last_pauta)).read()
        #msg = "work in progress"
        return msg

    def sanitize(text):
        REPLACEMENTS = {
            "\(" : "&#40;",
            "\)" : "&#41;",
            "\*" : "&#42;",
            "\<" : "&#60;",
            "\>" : "&#62;",
            "\[" : "&#91;",
            "\]" : "&#93;"
            }
        for pattern in list(REPLACEMENTS):
            text = re.sub(pattern, REPLACEMENTS[pattern], text)
        return text

    def pauta_commit_push(pauta_name, message=None):
        os.chdir(PAUTAS)
        current_time = time.ctime()
        os.system("git add %s" % pauta_name)
        if message is None:
            os.system("git commit -m \"Adding pauta  content at %s\" %s" % (current_time, pauta_name))
        else:
            os.system("git commit -m \"%s\" %s" % (message, pauta_name))
        os.system("git push")


    def add_pauta(command):
        url = command.split()[-1]
        if not re.search("^http", url):
            return
        last_pauta = get_last_pauta()
        pauta_body = read_pauta(last_pauta)

        content = pauta_body.split("\n\n")

        req = requests.get(url)
        html = None
        if req.status_code == 200:
            html = req.text

        if html is not None:
            soup = bs4.BeautifulSoup(html, "html")
            title = sanitize(soup.title.text)
            md_text = "* [%s](%s)" % (title, url)
            content[0] += "\n%s" % md_text
        body = "\n\n".join(content)

        with open(last_pauta, 'w') as fd:
            fd.write(body)
        pauta_commit_push(last_pauta)

    def generate_serial(filename=None):
        if filename is None:
            # generate for next month
            timestamp = str(time.strftime("%Y%m0", time.localtime(time.time() + 30 * 24 * 60 * 60)))
        else:
            time_string = filename.split(".")[0]
            if time_string[0] != 2 or len(time_string) < 7:
                timestap =generate_serial()
            else:
                year = time_string[:4]
                month = time_string[4:6]
                if int(month) == 12:
                    year = str(int(year) + 1)
                    month = "01"
                else:
                    month = "%02d" % (int(month) + 1)
                timestamp = "%s%s" % (year, month)
        return timestamp

    def copy_template(filename):
        os.chdir(PAUTAS)
        template = "template.md"
        with open(template) as tpl:
            buf = tpl.read()
            with open(filename, 'w') as dest:
                dest.write(buf)

    def create_pauta():
        last_pauta = get_last_pauta()
        new_pauta = "%s.md" % generate_serial(last_pauta)
        copy_template(new_pauta)
        pauta_commit_push(new_pauta, "Adicionando nova pauta.")

    def is_allowed(username):
        if username is None or allowed_users is None:
            return False
        if username in allowed_users.split():
            return True
        return False

    def add_sugestao(msg, user):
        debug("add_sugestao()")
        msg = re.sub("^/addsugestao ", "", msg)
        last_pauta = get_last_pauta()
        pauta_body = read_pauta(last_pauta)

        content = pauta_body.split("\n\n")

        position = None
        for i in range(0, len(content)):
            if re.search("Sugestões via telegram", content[i]):
                position = i
                break
        content[position] += "\n%s | author=%s" % (msg, user)
        body = "\n\n".join(content)

        with open(last_pauta, 'w') as fd:
            fd.write(body)
        pauta_commit_push(last_pauta)
        return "sugestão adicionada"


    try:
        if re.search("unixloadon", cmd.text):
            debug("O que é Unix Load On")
            msg = get_what_is()

        elif re.search("^/pauta", cmd.text):
            debug("Lendo pautas")
            msg = read_pauta()

        elif re.search("^/addpauta", cmd.text):
            if is_allowed(cmd.from_user.username):
                add_pauta(cmd.text)
                msg = "Link adicionado com sucesso.  Use /pauta pra ler o conteúdo."
            else:
                msg = "Sem permissão pra enviar novas entradas."

        elif re.search("^/addsugestao", cmd.text):
            msg = add_sugestao(cmd.text, cmd.from_user.username)

        elif re.search("^/novapauta", cmd.text):
            if is_allowed(cmd.from_user.username):
                create_pauta()
                msg = read_pauta()
            else:
                msg = "Sem permissão pra enviar novas entradas."
        elif re.search("^/testauser", cmd.text):
            if is_allowed(cmd.from_user.username):
                msg = "Usuário %s é autorizado." % cmd.from_user.username
            else:
                msg = "Usuário %s não tem autorização pra enviar posts." % cmd.from_user.username

    except Exception as e:
        try:
            obj.reply_to(cmd, "Deu merda: %s" % e)
        except Exception as z:
            print(u"%s" % z)

    os.chdir(curdir)
    if not msg:
        return

    msg_queue = []
    MAXSIZE = 4000 # hardcoded value
    msg_size = len(msg)
    if msg_size > MAXSIZE:
        # it must send in two parts to avoid errors
        msg_lines = msg.split("\n")
        msg_buff = ""
        for line in msg_lines:
            if len(msg_buff + line + "\n") > MAXSIZE:
                msg_queue.append(msg_buff)
                msg_buff = ""
            else:
                msg_buff += line + "\n"
        if len(msg_buff) > 0:
            msg_queue.append(msg_buff)
    else:
        msg_queue.append(msg)

    for msg in msg_queue:
        try:
            obj.send_message(cmd.chat.id, msg)
        except Exception as e:
            obj.reply_to(cmd, "Deu merda: %s" % e)


def Distros(obj, cmd):
    debug(cmd.text)
    msg = None
    distro = cmd.text
    distro = distro.lower()
    #distro = re.sub(".*distro ", "", distro)
    distro = distro.split()[-1]
    if distro:
        debug(" * distro: %s" % distro)
        if os.path.exists("%s/%s.jpg" % (IMGDIR, distro)):
            img = open("%s/%s.jpg" % (IMGDIR, distro), "rb")
            obj.send_photo(cmd.chat.id, img)
            return
        else:
            debug(" * arquivo de imagem não encontrado em: %s/%s.jpg" % (IMGDIR, distro))
            if os.path.exists("%s/Stallman_Chora.jpg"):
                img = open("%s/Stallman_Chora.jpg" % IMGDIR, "rb")
                obj.send_photo(cmd.chat.id, img)
            obj.send_message(cmd.chat.id, "Distro %s não encontrada." % distro +
                "  Agradecemos a compreensão (e use outra).")
            return
    if re.search("/ubuntu", cmd.text) or re.search("distro ubuntu", cmd.text):
        debug("ubuntu")
        img = open("%s/ubuntu.jpg" % IMGDIR, "rb")
        obj.send_photo(cmd.chat.id, img)
        return
    elif cmd.text == "/distros":
        obj.send_message(cmd.chat.id, "Distros: ubuntu e debian")
        return

    obj.send_message(cmd.chat.id, "Ainda não fiz...  Mas já está no backlog.")


def GetContent(url):
    debug("GetContent() called")
    if not url:
        return
    req = requests.get(url)
    if req.status_code == 200:
        text = req.text
        proto, domain = url.split("://")
        debug("GetContent: proto=%s" % proto)
        domain = re.sub("/.*", "", domain)
        debug("GetContent: domain=%s" % domain)
        domain = "%s://%s" % (proto, domain)
        #text = re.sub(" src=//", " src=%s/" % domain, text)
        #text = re.sub(" src=\"//", " src=\"%s/" % domain, text)
        text = re.sub(" src=/", " src=%s/" % domain, text)
        text = re.sub(" src=\"/", " src=\"%s/" % domain, text)
        #debug("GetContent: Full Text\n%s" % text)
        return text
    else:
        debug(" * return code error: %d" % req.status_code)
    return ""


def GetImgUrl(pattern, text, step=0):
    """
    pattern = string to find
    text = html retrieved from site
    step = if in the same line or next (+1, +2, etc)
    """
    debug("GetImgUrl() called with pattern=%s and step=%d" %
        (pattern, step) )
    if text is None:
        return None
    buf = text.split("\n")
    i = 0
    url_img = None
    for lineNr in range(len(buf)):
        line = buf[lineNr]
        if re.search(pattern, line):
            url_img = buf[lineNr+step]
            debug("GetImgUrl: found=%s" % url_img)
            break

    if not url_img:
        debug("GetImgUrl: no images links found")
        return None

    url = None
    if re.search("<img ", url_img):
        debug("GetImgUrl: matched on \"<img \": %s" % url_img)
        params = url_img.split()
        for p in params:
            if re.search("src=", p):
                debug("GetImgUrl: matched on parameter: %s" % p)
                # tmp_img = p.split("=")[-1]
                tmp_img = re.sub("^src=", "", p)
                tmp_img = re.sub("\"", "", tmp_img)
                url = re.sub("^\/\/", "http://", tmp_img)
                url = re.sub("^\/", "http://", url)
                debug("GetImgUrl: final match: %s" % url)
                break
    elif re.search("http", url_img):
        params = url_img.split()
        for p in params:
            if not re.search("^http", p):
                continue
            url = p
            break
    debug("GetImgUrl: %s" % url)
    return url


def GetImg(url):
    if not url or url is None:
        return
    req = requests.get(url, stream=True)
    filename = os.path.basename(url)
    if not re.search(".gif|.jpg|.png", filename):
        filename = "%s.gif" % filename
    img = "/tmp/%s" % filename
    with open(img, 'wb') as out_file:
        shutil.copyfileobj(req.raw, out_file)
    return img


def Comics(obj, cmd):
    debug("Comics(): %s" % cmd.text)
    img = None
    if re.search("/xkcd", cmd.text):
        url = "http://xkcd.com"
        html = GetContent(url)
        img_link = GetImgUrl("Image URL \(for hotlinking\/embedding\)", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
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
    elif re.search("/tirinhadorex", cmd.text):
        # curl http://tirinhasdorex.com/ | grep "<p><img class=\"aligncenter size-full wp-image-"
        url = "http://tirinhasdorex.com/"
        html = GetContent(url)
        img_link = GetImgUrl("<p><img class=\"aligncenter size-full wp-image-", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
    elif re.search("tirinhas|strips", cmd.text):
        obj.send_message(cmd.chat.id, "No momento somente tem: /dilbert, /xkcd, /vidadeprogramador, /vidadesuporte")
        return
    elif re.search("nudes", cmd.text):
        url = "https://rms.sexy/?js#/img/"
        obj.send_message(cmd.chat.id, "Péra... já estou tirando a roupa e ligando a webcam...")
        html = GetContent(url)
        img_link = GetImgUrl("<a href=\"/\">", html)
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
        obj.send_message(cmd.chat.id, "Diretamente de %s" % url)
    elif re.search("foods", cmd.text):

        # We'll grab the images from /r/foodporn JSON file.
        # Which will be stored in the home folder, got a problem with requests

        # Get the post list
        debug("foods")
        th = threading.Thread(target=GetFood)
        th.start()

        #  waiting time
        counter = 5
        while counter >= 0:
            counter -= 1
            if th.isAlive() is False:
                break
            time.sleep(1)

        if not os.path.exists(MANDAFOODSFILE):
            obj.send_message(cmd.chat.id, "Deu alguma zica sinistra e o"
                " arquivo json não foi baixado do site.")
            return
        try:
            debug(" * reading json")
            json_data = json.loads(open(MANDAFOODSFILE).read())
        except Exception as e:
            debug(" * json failed: creating one: %s" % e)
            debug(" * thread is alive? %s" % th.isAlive())
            json_data = { "error" : 666, "message" : "error fazendo parsing do json" }
        if "error" in json_data:
            debug(" * found key error")
            obj.send_message(cmd.chat.id, u"Deu merda no Jasão: %s" % json_data["message"])
            debug(" * removing file")
            os.unlink(MANDAFOODSFILE)
            return

        seed = random.seed(os.urandom(random.randint(0,1000)))
        # Shuffling the posts
        post_number = random.randint(1, 25) # 0 is the pinned title post for the subreddit
        img_link = json_data["data"]["children"][post_number]["data"]["url"]
        obj.send_message(cmd.chat.id, "Nham nham! 🍔")
        debug("%s: %s" % (cmd.text, img_link))
        img = GetImg(img_link)
        obj.send_message(cmd.chat.id, "Direto de https://www.reddit.com/r/foodporn")

    if img:
        try:
            img_fd = open(img, 'rb')
            obj.send_photo(cmd.chat.id, img_fd)
        except Exception as e:
            obj.send_message(cmd.chat.id, "Ooopsss... deu merda! %s" % e)
        os.unlink(img)
    elif re.search("megazine", cmd.text):
        megazines = [ "xkcd", "dilbert", "vidadeprogramador",
    "vidadesuporte", "tirinhadorex" ]
        cmd_new = cmd
        for zine in megazines:
            cmd_new.text = "/%s" % zine
            Comics(obj, cmd_new)
    else:
        obj.send_message(cmd.chat.id, "É... foi não...")


def FofoMetrics(obj, cmd):
    debug(cmd.text)
    global fofondex, start_time
    #debug("Fofondex on call: %s" % fofondex)
    user_name = cmd.from_user.username
    user_id = cmd.from_user.id
    user_1stname = cmd.from_user.first_name

    user = user_name  # backward compatibility
    if not user_name:  # got None
        if not user_1stname:
            user_name = "Anonimo da Internet (%s)" % user_id
        else:
            user_name = "%s (%s)" % (user_1stname, user_id)
    if not user_1stname:
        user_1stname = user_name
    """"
    Data struct:
        user_id: {
            'user_1stname' : FirstName,
            'user_name' Username,
            'timestamp' : dateinseconds,
            'foforate' : pctg
            }
    """
    def DataRead():
        debug("DataRead")
        global simple_lock, fofondex
        # if data, skip to read since it is updated via memory
        if len(fofondex.keys()) > 0:
            #debug(" * It has data, so don't need to read.")
            #debug(" * Fofondex here: %s" % fofondex)
            return
        while simple_lock:
            time.sleep(random.random())
        simple_lock = True
        try:
            fofondex = pickle.load(open(FOFODB, "rb"))
        except IOError:
            debug("Error reading FOFODB")
            pass
        simple_lock = False
        if not fofondex:
            #debug("Using empty fofondex.")
            fofondex = {}
        #debug(" * DataRead.fofondex: %s" % fofondex)

    def DataWrite():
        debug("DataWrite")
        global simple_lock, fofondex, start_time
        current_time = time.time()
        #debug(" * Fofondex here: %s" % fofondex)
        # just save data if time > 5 minutes to preserve disk
        if (current_time - start_time < 5 * 60):
            #debug("Skipping write (timer < 5 minutes).")
            return
        else:
            start_time = current_time
        while simple_lock:
            time.sleep(random.random())
        simple_lock = True
        try:
            if not fofondex:
                #debug(" * DataWrite: removing database from disk.")
                os.unlink(FOFODB)
            else:
                #debug(" * DataWrite: pickle.dump()")
                #debug(" * DataWrite: data saved => %s" % fofondex)
                pickle.dump(fofondex, open(FOFODB, "wb"))
        except IOError:
            debug("Failed to save DB")
            pass
            # yap... we lost it...
        simple_lock = False

    def DataReset():
        global fofondex
        debug("DataReset")
        #debug("Before: %s" % fofondex)
        fofondex = {}
        DataWrite()
        #debug("After: %s" % fofondex)

    def RunTheDice(n=None):
        debug("RunTheDice")
        if n is not None and n >=0 and n <= 100:
            return n
        random.seed(os.urandom(random.randint(0,1000)))
        return random.randint(0,100)

    def TimeDelta(user_id):
        debug("TimeDelta")
        if user_id in fofondex:
            timestamp = fofondex[user_id]['timestamp']
            now = time.time()
            return now - int(timestamp)
        else:
            return 0
    def InitializeUser(pctg=None):
        debug("InitializeUser")
        if pctg is None:
            pctg = RunTheDice()
        return {
                'timestamp' : time.time(),
                'foforate' : pctg,
                'user_name' : user_name,
                'user_1stname' : user_1stname
        }
    def GetPctg(user_id):
        debug("GetPctg")
        DataRead()
        if user_id in fofondex:
            pctg = fofondex[user_id]['foforate']
        else:
            # initialize user
            pctg = RunTheDice()
            fofondex[user_id] = InitializeUser()
            DataWrite()
        return int(pctg)

    if re.search("/resetfofos", cmd.text):
        if user_name == botadm:
            obj.send_message(cmd.chat.id, u"Limpando o fundum que está por aqui." \
                + u"  Vou até jogar creolina.")
            DataReset()
        else:
            obj.send_message(cmd.chat.id, u"Vai aprender a sair do VI "\
            + "antes de querer vir aqui me dar ordem.")
        return

    if re.search("/(fof|blob)ometro", cmd.text):
        DataRead()
        if not user_id in fofondex:
            InitializeUser()
        if TimeDelta(user_id) < 24 * 60 * 60:
            pctg = GetPctg(user_id)
        else:
            pctg = RunTheDice()
            fofondex[user_id] = InitializeUser()
            DataWrite()
        #debug(" * Fofondex top: %s" % fofondex)

        if re.search("arrumasaporra", cmd.text):
            if user_name == botadm:
                obj.send_message(cmd.chat.id, u"Perdão patrão... Estava aqui " + \
                    u"compilando o emacs e me distraí.  Deixa eu fazer de novo.")
                if re.search("blob", cmd.text):
                    pctg = RunTheDice(n=0)
                    #bot.send_message(cmd.chat.id, u"Seu valor é=%d" % pctg)
                elif re.search("fofo", cmd.text):
                    pctg = RunTheDice(100)
                    #bot.send_message(cmd.chat.id, u"Seu valor é=%d" % pctg)
                #bot.send_message(cmd.chat.id, u"Inicializando com pctg=%d" % pctg)
                fofondex[user_id] = InitializeUser(pctg=pctg)
            else:
                obj.send_message(cmd.chat.id, u"Quem você pensa que é pra " + \
                    u"falar comigo dessa maneira?  Sabe quem eu sou???")
                obj.send_message(cmd.chat.id, u"Vou verificar de novo, " + \
                    u"mas só dessa vez.")
                pctg = RunTheDice()
                fofondex[user_id] = InitializeUser(pctg=pctg)

        pctg = fofondex[user_id]['foforate']
        try:
            #debug(" * Fofondex before publishing: %s" % fofondex)
            msg = u"Hoje %s tem %d%s de ultrafofura mas " % (user_name, pctg, '%')
            msg += u"aquele %d%s de blob binário no kernel." % (100 - pctg, '%',)
            if re.search("blob", cmd.text):
                msg = u"Hoje %s tem %d%s de blobice mas " % (user_name, 100 - pctg, '%')
                msg += u"aquele %d%s de linux-libre no kernel." % (pctg, '%',)
            debug(u'%s' % msg)
            DataWrite()
            obj.send_message(cmd.chat.id, u'%s' % msg)
        except Exception as e:
            obj.send_message(cmd.chat.id, "Deu ruim... %s" % e)
        return

    if re.search("/(fof|blob)ondex", cmd.text):
        if len(list(fofondex)) == 0:
            msg = u"Ninguém ainda teve coragem de tentar esse UltraFofo."
            obj.send_message(cmd.chat.id, u'%s' % msg)
            return
        msg = u"Ranking Dollyinho de #UltraFofos:\n"
        if re.search("blob", cmd.text):
            msg = u"Ranking Dollyinho de #Blobice:\n"
        ranking = {}
        isUpdated = False
        for u in list(fofondex):
            delta = TimeDelta(u)
            if delta > 24 * 60 * 60:
                # remove old data
                isUpdated = True
                del fofondex[u]
                continue
            ranking[u] = fofondex[u]['foforate']
        if isUpdated:
            DataWrite()
        i = 1
        if re.search("fofo", cmd.text):
            for u in sorted(ranking, key=ranking.get, reverse=True):
                pct = fofondex[u]['foforate']
                u_name = fofondex[u]['user_name']
                msg += u"%d) %s: %d%s\n" % (i, u_name, pct, '%')
                i += 1
        elif re.search("blob", cmd.text):
            for u in sorted(ranking, key=ranking.get, reverse=False):
                pct = fofondex[u]['foforate']
                u_name = fofondex[u]['user_name']
                msg += u"%d) %s: %d%s\n" % (i, u_name, 100 - pct, '%')
                i += 1
            del ranking
        try:
            debug(u'%s' % msg)
            obj.send_message(cmd.chat.id, u'%s' % msg)
        except Exception as e:
            obj.send_message(cmd.chat.id, "Deu ruim... %s" % e)
        return

    if re.search("/scoreblob", cmd.text):
        try:
            text, person = cmd.text.split()
        except Exception as e:
            obj.send_message(cmd.chat.id,  u"Manda: /scoreblob @usuario")
            return
        debug(u"/scoreblob: %s" % person)
        obj.send_message(cmd.chat.id,  u"Em construção...")



def Motivational(obj, cmd):
    debug(cmd.text)
    MOTIVATIONALDIR = "%s/motivational" % (os.environ.get('HOME'))
    if(os.path.exists(MOTIVATIONALDIR) == False):
        os.system('cd && git clone https://github.com/jeanlandim/motivational')

    photos = os.listdir(MOTIVATIONALDIR)
    motivational = ""
    while not re.search("(jpg|png|gif)", motivational):
        motivational = random.choice(photos)
        debug("Motivational picture: %s" % motivational)
    try:
        ph = open("%s/%s" % (MOTIVATIONALDIR, motivational), 'rb')
        obj.send_photo(cmd.chat.id, ph)
    except Exception as e:
        obj.reply_to(cmd, "Deu merda: %s" % e)


def DuckDuckGo(obj, cmd):
    debug(cmd.text)
    q = cmd.text.split()
    if len(q) == 1:
        return
    question = "+".join(q[1:])
    debug("Question=%s" % question)
    req = requests.get("https://duckduckgo.com/html/?q=%s" % question)
    answer = None
    html = bp.BeautifulSoup(req.text)
    responses = html.findAll("div", id="zero_click_abstract")
    try:
        answer = responses[0].text
    except Exception as e:
        print(e) # get internal
        pass
    if not answer:
        obj.reply_to(cmd, "Não tenho a menor idéia.  Tem de perguntar no google.")
        return
    try:
        obj.reply_to(cmd, answer)
    except Exception as e:
        obj.reply_to(cmd, "Deu merda: %s" % e)


def Mimimizer(obj, session):
    debug(session.text)
    param = session.text.split()
    if len(param) <= 1:
        return
    resp = " ".join(param[1:])
    resp = re.sub("a|e|o|u", "i", resp)
    resp = re.sub("A|E|O|U", "I", resp)
    resp = re.sub(u"á|é|ó|ú", u"í", resp)
    resp = re.sub(u"Á|É|Ó|Ú", u"Í", resp)
    obj.reply_to(session, u"%s" % resp)
    # Falta implementar quem...


def Ban(obj, session):
    debug(session.text)
    obj.reply_to(session, "Deixa que eu pego ele na hora da saída.")
    gif = "https://media.giphy.com/media/H99r2HtnYs492/giphy.gif"
    obj.send_document(session.chat.id, gif)
    # Falta implementar quem...

def is_command(message):
    try:
        u_message_text = "%s" % message.text
    except Exception as e:
        return False
    return re.search("^/[A-Za-z].*", u_message_text)


def GenericMessageHandler(obj, session):
    command = u"%s" % session.text[1:]
    command = command.split()[0]
    command = command.split("@")[0]
    debug(u"Generic calling for %s" % command)
    if get_answer(command):
        reply_text(obj, session, get_answer(command))


def WhatEver(obj, session):
    debug(session.text)
    if get_answer(session.text):
        reply_text(bot, session, get_answer(session.text))
        return
    elif re.search("bom dia", session.text.lower()):
        Dia(session)
        return
    #bot.reply_to(session, u"Dude... entendi foi é porra nenhuma.")


def clean_up_country(country):
        return country.strip().lower()


def getCountryCoronaData(country, dataJSON):
    debug("getCountryCoronaData()")
    debug(f" * Country: {country}")
    country_for_search = clean_up_country(country)
    for countryJSON in dataJSON:
        if "country" not in countryJSON:
            continue
        if clean_up_country(countryJSON["country"]) == country_for_search:
            return countryJSON
    return None


def generateWorldCoronaData(dataJSON):
    debug("generateWorldCoronaData()")
    """
    {"country":"China","cases":80928,"todayCases":34,"deaths":3245,"todayDeaths":8,"recovered":70420,"active":7263,"critical":2274,"casesPerOneMillion":56}
    """
    cases = 0
    todayCases = 0
    deaths = 0
    todayDeaths = 0
    recovered = 0
    active = 0
    critical = 0
    casesPerOneMillion = 0
    for data in dataJSON:
        if "cases" in data:
            cases += int(data["cases"])
        if "todayCases" in data:
            todayCases += int(data["todayCases"])
        if "deaths" in data:
            deaths += int(data["deaths"])
        if "todayDeaths" in data:
            todayDeaths += int(data["todayDeaths"])
        if "recovered" in data:
            recovered += int(data["recovered"])
        if "active" in data:
            active += int(data["active"])
        if "critical" in data:
            critical += int(data["critical"])
        if "casesPerOneMillion" in data:
            casesPerOneMillion += int(data["casesPerOneMillion"])
    result = """{
        "country":"World",
        "cases":%d,
        "todayCases":%d,
        "deaths":%d,
        "todayDeaths":%d,
        "recovered":%d,
        "active":%d,
        "critical":%d,
        "casesPerOneMillion":%d
        }""" % (
        cases,
        todayCases,
        deaths,
        todayDeaths,
        recovered,
        active,
        critical,
        casesPerOneMillion)
    return json.loads(result)

def generateReport(country=None):
    debug(f"generateReport(): country={country}")
    dataJSON = fetchCoronaData()

    if country is not None:
        myJSON = getCountryCoronaData(country, dataJSON)
    else:
        myJSON = generateWorldCoronaData(dataJSON)
        country = myJSON["country"]

    if myJSON is None:
        return None

    response =  "##################################\n"
    response += f"# Corona Virus em {country} #\n"
    response += "##################################\n"


    if "cases" in myJSON:
        response += " Casos no total: %s\n" % myJSON["cases"]
    if "todayCases" in myJSON:
        response += " Casos somente hoje: %s\n" % myJSON["todayCases"]
    if "deaths" in myJSON:
        response += " Mortes no total: %s\n" % myJSON["deaths"]
    if "todayDeaths" in myJSON:
        response += " Mortes somente hoje: %s\n" % myJSON["todayDeaths"]
    if "recovered" in myJSON:
        response += " Recuperados no total: %s\n" % myJSON["recovered"]
    if "critical" in myJSON:
        response += " Em estado crítico no total: %s\n" % myJSON["critical"]
    if "casesPerOneMillion" in myJSON:
        response += " Casos a cada milhão: %s\n" % myJSON["casesPerOneMillion"]

    return response


def fetchCoronaData():
    debug("fetchCoronaData()")
    URL = "https://coronavirus-19-api.herokuapp.com/countries"
    OUTPUT = "/tmp/corona-data.json"

    if os.path.exists(OUTPUT):
        fileStat = os.stat(OUTPUT)
        mtime = fileStat.st_mtime
        currentTime = time.time()

        oneDayinSeconds = 24 * 60 * 60
        delta = currentTime - mtime
        if delta < oneDayinSeconds:
            with open(OUTPUT) as dataJSON:
                return json.loads(dataJSON.read())

    req = requests.get(URL)
    if req.status_code != 200:
        raise Exception(f"Failed to fetch data from {URL} (status={req.status_code})")
    with open(OUTPUT, 'w') as dataJSON:
        dataJSON.write(req.text)
        dataJSON.write("\n")
    return json.loads(req.text)


def getAvailableCountries():
    dataJSON = fetchCoronaData()
    countries = []
    for data in dataJSON:
        countries.append(data["country"])
    return countries

def CoronaVirus(obj, session):
    debug(session.text)
    """
    Output: {"country":"Sweden","cases":1190,"todayCases":69,"deaths":7,"todayDeaths":0,"recovered":1,"critical":12}
    """
    command = session.text
    countries = command.split()[1:]
    if len(countries) == 0:
        response = generateReport()
        debug(response)
        reply_text(obj, session, response)

    for countryName in countries:
        response = generateReport(country=countryName)
        if response is not None:
            debug(response)
            reply_text(obj, session, response)
        else:
            debug("No matchig country")
            availableCountries = getAvailableCountries()
            reply_text(obj,
                session,
                "Países: " + ", ".join(sorted(availableCountries)))


# avoiding nulls
if __name__ == '__main__':
    fofondex = {}
    start_time = time.time()

    if sys.argv[-1] == "check":
        print("Ok")
        sys.exit(os.EX_OK)


    set_debug()
    debug("Starting bot")
    get_global_keys()
    bot = telebot.TeleBot(key)

    @bot.message_handler(commands=["oi", "hello", "helloworld", "oiamor", "teamo"])
    def handler(command):
        hello_world(bot, command)

    @bot.message_handler(commands=["manda", "manga"])
    def handler(command):
        Manda(bot, command)

    @bot.message_handler(commands=["pipoca"])
    def handler(command):
        PipocaGif(bot, command)

    @bot.message_handler(commands=["reload"])
    def handler(command):
        Reload(bot, command)

    @bot.message_handler(commands=["debug"])
    def handler(command):
        ToggleDebug(bot, command)

    @bot.message_handler(commands=["fuda"])
    def handler(command):
        fuda(bot, command)

    @bot.message_handler(commands=["uname", "uptime", "date", "df"])
    def handler(command):
        SysCmd(bot, command)

    @bot.message_handler(commands=["reboot", "shutdown", "sudo", "su"])
    def handler(command):
        Requer(bot, command)

    @bot.message_handler(commands=["fortune", "fortunes", "sorte"])
    def handler(command):
        Fortune(bot, command)

    @bot.message_handler(commands=["hacked", "pwn3d"])
    def handler(command):
        Hacked(bot, command)

    @bot.message_handler(commands=["apt-get", "aptitude", "apt"])
    def handler(command):
        AptCmds(bot, command)

    @bot.message_handler(commands=["dia", "bomdia"])
    def handler(command):
        Dia(bot, command)

    @bot.message_handler(commands=["photo"])
    def handler(command):
        Photo(bot, command)

    @bot.message_handler(commands=["unixloadon", "pauta", "pautas", "addpauta", "novapauta", "testauser", "addsugestao"])
    def handler(command):
        UnixLoadOn(bot, command)

    @bot.message_handler(commands=["distros", "distro", "ubuntu", "debian", "arch", "manjaro"])
    def handler(command):
        Distros(bot, command)

    @bot.message_handler(commands=["xkcd", "dilbert", "vidadeprogramador",
        "tirinhas", "strips", "vidadesuporte",
        "mandanudes", "nudes", "mandafoods", "foods",
        "tirinhadorex", "megazine"])
    def handler(command):
        Comics(bot, command)

    @bot.message_handler(commands=["fofometro", "fofondex", "resetfofos",
        "blobometro", "blobondex", "scoreblob"])
    def handler(command):
        FofoMetrics(bot, command)

    @bot.message_handler(commands=["motivationals", "motivational", "motivacional" ])
    def handler(command):
        Motivational(bot, command)

    @bot.message_handler(commands=["oquee", "oqueé"])
    def handler(command):
        DuckDuckGo(bot, command)

    @bot.message_handler(commands=["mimimi"])
    def handler(command):
        Mimimizer(bot, command)

    @bot.message_handler(commands=["ban"])
    def handler(command):
        Ban(bot, command)

    @bot.message_handler(commands=["corona", "coronavirus"])
    def handler(command):
        CoronaVirus(bot, command)

    @bot.message_handler(func=is_command, content_types=['text'])
    def handler(command):
        GenericMessageHandler(bot, command)

    @bot.message_handler(func=lambda m: True)
    def handler(command):
        WhatEver(bot, command)

    try:
        debug("Main()")
        main()
        debug("Polling...")
        bot.polling()
    except Exception as e:
        print("ERROR:", e)
    os.unlink(PIDFILE)

"""
{'delete_chat_photo': None, 'migrate_to_chat_id': None, 'text': u'/reload',
'sticker': None, 'pinned_message': None, 'forward_from_chat': None,
'migrate_from_chat_id': None, 'video': None, 'left_chat_member': None,
'chat': {'username': u'ultraOSI', 'first_name': None, 'last_name': None,
'title': u'UltraOSI - Free Software e Opensource sem FUDA e com blobs :)',
'all_members_are_administrators': None,
'type': u'supergroup',
'id': -1001109390847L},
'group_chat_created': None,
'new_chat_photo': None,
'forward_date': None,
'entities': [<telebot.types.MessageEntity instance at 0x74833c60>],
'supergroup_chat_created': None, 'photo': None, 'document': None,
'forward_from': None, 'location': None, 'edit_date': None,
'content_type': 'text',
'from_user': {'username': u'HelioLoureiro',
'first_name': u'[Helio@blobeiro.eng.br]>',
'last_name': None, 'id': 64457589},
'date': 1487941240,
'new_chat_member': None, 'voice': None, 'reply_to_message': None,
'venue': None, 'message_id': 11569, 'caption': None, 'contact': None,
'channel_chat_created': None, 'audio': None, 'new_chat_title': None}
"""
