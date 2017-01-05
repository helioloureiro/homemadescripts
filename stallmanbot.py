#! /usr/bin/python -u
# -*- coding: utf-8 -*-

import telebot
import os
import sys
import ConfigParser
import re
import time
import requests
import BeautifulSoup as bp

CONFIG = ".twitterc"
DEBUG = True
def debug(msg):
    if DEBUG and msg:
        try:
            print u"%s" % msg
        except Exception as e:
            print "DEBUG ERROR:", e
        
HOME = os.environ.get('HOME')
PIDFILE = "%s/.stallmanbot.pid" % HOME
PAUTAS = "%s/canalunixloadon/pautas" % HOME
IMGDIR = "%s/Pictures" % HOME

if os.path.exists(PIDFILE):
    try:
        pid = open(PIDFILE).read()
    except:
        pid = None
    if pid and int(pid) > 0 and int(pid) != os.getpid():
        if os.path.exists("/proc/%d" % int(pid)):
            print "Already running."
            sys.exit(0)

fd = open(PIDFILE, 'w')
fd.write("%d\n" % os.getpid())
fd.flush()
fd.close()

configuration = "%s/%s" % (os.environ.get('HOME'), CONFIG)
cfg = ConfigParser.ConfigParser()
debug("Reading configuration: %s" % configuration)
if not os.path.exists(configuration):
    print "Failed to find configuration file %s" % configuration
    sys.exit(1)
cfg.read(configuration)
key = cfg.get("TELEGRAM", "STALLBOT")
debug("Key acquired.")

debug("Starting bot for FreeSpeech")
bot = telebot.TeleBot(key)
    
@bot.message_handler(commands=["oi"])
def HelloWorld(cmd):
    debug(cmd.text)
    try:
        bot.reply_to(cmd, "GNU world")
    except:
        bot.reply_to(cmd, "Deu merda...")
        
@bot.message_handler(commands=["ultrafofo", "ultrafofos"])
def UltraFofo(cmd):
    debug(cmd.text)
    try:
        bot.reply_to(cmd, "#UltraFofos é o grupo super fofis de defensores de software livre." + \
            "Veja mais em: https://www.youtube.com/watch?v=eIRk38d32vA")
    except:
        bot.reply_to(cmd, "Deu merda...")
        
@bot.message_handler(commands=["reload"])
def Reload(cmd):
    debug(cmd.text)
    if not cmd.from_user.username == 'HelioLoureiro':
        bot.reply_to(cmd, "Só patrão pode isso.")
    try:
        debug(cmd)
        bot.reply_to(cmd, "Reloading...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["uname", "uptime", "date"])
def SysCmd(cmd):
    debug("Running: %s" % cmd.text)
    sanitize = re.sub(";.*", "", cmd.text)
    sanitize = re.sub("|.*", "", sanitize)
    try:
        resp = os.popen(sanitize[1:]).read()
        debug("Response: %s" % resp)
        bot.reply_to(cmd, "%s" % resp)
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["reboot", "shutdown", "sudo", "su"])
def Requer(cmd):
    debug(cmd.text)
    if re.search("sudo rm -rf /", cmd.text):
        vd = open("%s/sudo_rm_rf.gif" % IMGDIR, "rb")
        bot.send_photo(cmd.chat.id, vd)
        return
    try:
        bot.reply_to(cmd, "Ah lá... achando que é réquer.")
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["man", "info"])
def ManPages(cmd):
    debug("Running: %s" % cmd.text)
    sanitize = re.sub(";.*", "", cmd.text)
    sanitize = re.sub("|.*", "", sanitize)
    params = sanitize.split()
    page = " ".join(params[1:])
    try:
        resp = os.popen("man %s" % page).read()
        debug("Response: %s" % resp)
        buf = resp.split("\n")
        for i in range(0, len(buf), 10):
            output = "\n".join(buf[i:i+10])
            bot.reply_to(cmd, "%s" % output)
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["help", "ajuda"])
def Help(cmd):
    debug(cmd.text)
    try:
        bot.reply_to(cmd, "Precisa de ajuda?  Procure o CVV. http://www.cvv.org.br")
    except:
        bot.reply_to(cmd, "Deu merda...")
        
@bot.message_handler(commands=["fortune", "fortunes", "sorte"])
def Fortune(cmd):
    try:
        bot.reply_to(cmd, "%s" % os.popen("/usr/games/fortune").read())
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["rtfm", "RTFM"])
def RTFM(cmd):
    try:
        bot.reply_to(cmd, "Read The F*cking Manual.  Ou leia o Guia Foca GNU/Linux.")
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["photo"])
def Photo(cmd):
    debug("Photo")
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    SAVEDIR = "%s/weather/%s/%s" % (os.environ.get('HOME'), year, month)
    if not os.path.exists(SAVEDIR):
        debug("Sem fotos")
        bot.reply_to(cmd, "Sem fotos no momento.")
        return
    photos = os.listdir(SAVEDIR)
    last_photo = sorted(photos)[-1]
    debug("Última foto: %s" % last_photo)
    tagname = os.path.basename(last_photo)
    try:
        bot.reply_to(cmd, "Última foto: %s" % tagname)
        ph = open("%s/%s" % (SAVEDIR, last_photo), 'rb')
        bot.send_photo(cmd.chat.id, ph)
        #bot.send_photo(cmd.chat.id,"FILEID")
    except Exception as e:
        bot.reply_to(cmd, "Deu merda: %s" % e)

@bot.message_handler(commands=["unixloadon", "pauta", "pautas"])
def UnixLoadOn(cmd):
    debug("Unix Load On")
    msg = None
    if re.search("unixloadon", cmd.text):
        debug("O que é Unix Load On")
        url = "https://helioloureiro.github.io/canalunixloadon/"
        www = requests.get(url)
        msg = www.text
        msg = msg.encode("utf-8")
        debug(msg)
        soup = bp.BeautifulSoup(msg)
        msg = ""
        for section in soup.findAll("section"):
            buf = section.getText(separator='\n')
            debug(buf)
            msg += buf
            msg += "\n"
        
    elif re.search("^/pauta", cmd.text):
        pautas = os.listdir(PAUTAS)
        last_pauta = sorted(pautas)[-1]
        if not re.search("^20", last_pauta):
            last_pauta = sorted(pautas)[-2]
        msg = open("%s/%s" % (PAUTAS, last_pauta)).read()

    if not msg:
        return
    try:
        bot.send_message(cmd.chat.id, msg)
    except Exception as e:
        bot.reply_to(cmd, "Deu merda: %s" % e)

@bot.message_handler(commands=["distros", "distro", "ubuntu", "debian", "arch", "manjaro"])
def Distros(cmd):
    debug(cmd.text)
    msg = None
    distro = cmd.text
    distro = distro.lower()
    distro = re.sub(".*distro ", "", distro)
    if distro:
        debug("Distro: %s" % distro)
        if os.path.exists("%s/%s.jpg" % (IMGDIR, distro)):
            img = open("%s/%s.jpg" % (IMGDIR, distro), "rb")
            bot.send_photo(cmd.chat.id, img)
            return
        else:
            img = open("%s/Stallman_Chora.jpg" % IMGDIR, "rb")
            bot.send_photo(cmd.chat.id, img)
            bot.send_message(cmd.chat.id, "Distro não encontrada.  Agradecemos a compreensão (e use outra).")
            return
    if re.search("/ubuntu", cmd.text) or re.search("distro ubuntu", cmd.text):
        debug("ubuntu")
        img = open("%s/ubuntu.jpg" % IMGDIR, "rb")
        bot.send_photo(cmd.chat.id, img)
        return
    elif cmd.text == "/distros":
        bot.send_message(cmd.chat.id, "Distros: ubuntu e debian")
        return

    bot.send_message(cmd.chat.id, "Ainda não fiz...  Mas já está no backlog.")

try:
    debug("Polling...")
    bot.polling()
except Exception as e:
    print e
    os.unlink(PIDFILE)
