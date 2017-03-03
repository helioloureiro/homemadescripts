#! /usr/bin/python -u
# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser
import re
import time
import shutil
import random
import pickle
from datetime import date
import requests
import BeautifulSoup as bp
import telebot

# Message to send to @BotFather about its usage.
Commands_Listing = """

== Super ultra bot.==

oi - Hummm... então tá.
ultrafofos - Quem são, o que são e como vivem.
photo - Maravilhos nudes livres.  Sério.
rtfm - O que todo mundo já devia saber.
distro - Use: distro <suadistro>. Uma fofurinha sobre sua distro favorita.  Ou não.
xkcd - Sua dose diária de humor ácido do xkcd.
dilbert - Sua dose diária de humor corporativo.
vidadeprogramador - Sua dose diária de Alonzo.
vidadesuporte - Sua dose diária de chamados no helpdesk.
angulodevista - Sua dose diária de vida.  Infelizmente.
tirinhadorex - Tirinhas meio emo.
fofometro - Quão fofo você é?  Tente.
fofondex - Ranking de fofura.
fortune - A sorte do dia.  Ou não.
date - A data atual.
uptime - Somente os fortes entenderão.
mandanudes - Pura sensualidade.
nudes - Sensualidade dum jeito mais rápido.
emacs - Religião é coisa séria.  Principalmente a parte do vinho e pecado.
motivational - Pra melhorar *aquela* segunda-feira.
dia - Pra saber em qual dia da semana estamos.  Ou não.
blob - Quem não precisa de firmware pra funcionar?
mimimi - Mande: /mimimi frase.
bomdia - Assim que se começa um dia de verdade.
fontes - Pra ter livre acesso ao conteúdo.
"""

CONFIG = ".twitterc"
DEBUG = True
def debug(msg):
    if DEBUG and msg:
        try:
            print u"%s" % msg
        except Exception as e:
            print u"DEBUG ERROR: %s" % e

HOME = os.environ.get('HOME')
PIDFILE = "%s/.stallmanbot.pid" % HOME
PAUTAS = "%s/canalunixloadon/pautas" % HOME
IMGDIR = "%s/Pictures" % HOME
SCRIPTHOME = "%s/homemadescripts" % HOME
FOFODB = "%s/fofondex.db" % HOME
simple_lock = False # very simple lock way

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
try:
    key = cfg.get("TELEGRAM", "STALLBOT")
    botadm = cfg.get("TELEGRAM", "STALLBOTADM")
except ConfigParser.NoSectionError:
    print "No TELEGRAM session found to retrieve settings."
    print "Check your configuration file."
    sys.exit(1)
debug("Key acquired.")

def StartUp():
    debug("Startup")
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
                sys.exit(1)
            debug("Updating bot...")
            shutil.copy(botname, "%s/bin/%s" % (HOME, botname))
            debug("Bot version updated.")
            # check first
            debug("Calling restart")
            python = sys.executable
            os.execl(python, python, *sys.argv)

debug("Starting bot for FreeSpeech")
bot = telebot.TeleBot(key)

@bot.message_handler(commands=["oi", "hello", "helloworld"])
def HelloWorld(cmd):
    debug(cmd.text)
    try:
        bot.send_message(cmd.chat.id, "OSI world")
    except Exception as e:
        try:
            bot.send_message(cmd.chat.id, "Deu merda... %s" % e)
        except Exception as z:
            print z
    debug("tchau")

@bot.message_handler(commands=["ping"])
def Ping(cmd):
    debug(cmd.text)
    try:
        bot.send_message(cmd.chat.id, "ACK")
    except Exception as e:
        try:
            bot.send_message(cmd.chat.id, "Deu merda... %s" % e)
        except Exception as z:
            print z
    debug("tchau")

@bot.message_handler(commands=["ultrafofo", "ultrafofos"])
def UltraFofo(cmd):
    debug(cmd.text)
    try:
        bot.send_message(cmd.chat.id,
            "#UltraFofos é o grupo super fofis de defensores de software livre." + \
            "Veja mais em: https://www.youtube.com/watch?v=eIRk38d32vA")
    except Exception as e:
        try:
            bot.send_message(cmd.chat.id, "Deu merda... %s" % e)
        except Exception as z:
            printz

@bot.message_handler(commands=["reload"])
def Reload(cmd):
    debug(cmd.text)
    if not cmd.from_user.username == botadm:
        bot.reply_to(cmd, "Só patrão pode isso.")
        return
    try:
        debug(cmd)
        bot.reply_to(cmd, "Reloading...")
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
                    bot.send_message(cmd.chat.id, "Python crashed.  Vou carregar saporra não.  Vai que...")
                    return
                debug("Updating bot...")
                shutil.copy(botname, "%s/bin/%s" % (HOME, botname))
                bot.send_message(cmd.chat.id, "Bot version updated.")
        # check first
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        try:
            bot.reply_to(cmd, "Deu merda... %s" % e)
        except Exception as z:
            print z

@bot.message_handler(commands=["uname", "uptime", "date"])
def SysCmd(cmd):
    debug("Running: %s" % cmd.text)
    sanitize = re.sub(";.*", "", cmd.text)
    sanitize = re.sub("|.*", "", sanitize)
    sanitize = re.sub("@.*", "", sanitize)
    try:
        resp = os.popen(sanitize[1:]).read()
        resp = re.sub("GNU", "OSI", resp)
        debug("Response: %s" % resp)
        bot.reply_to(cmd, "%s" % resp)
    except Exception as e:
        try:
            bot.send_message(cmd.chat.id, "Deu merda... %s" % e)
        except Exception as z:
            print z
    debug("done here")

@bot.message_handler(commands=["reboot", "shutdown", "sudo", "su"])
def Requer(cmd):
    debug(cmd.text)
    try:
        if re.search("sudo rm -rf /", cmd.text):
            vd = open("%s/sudo_rm_rf.gif" % IMGDIR, "rb")
            bot.send_photo(cmd.chat.id, vd)
            return
        bot.reply_to(cmd, "Ah lá... achando que é réquer.")
    except Exception as e:
        try:
            bot.reply_to(cmd, "Deu merda... %s" % e)
        except Exception as z:
            print z

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
        output = "\n".join(buf[0:10])
        bot.reply_to(cmd, "%s" % output)
    except Exception as e:
        try:
            bot.reply_to(cmd, "Deu merda... %s" % e)
        except Exception as z:
            print z


@bot.message_handler(commands=["help", "ajuda"])
def Help(cmd):
    debug(cmd.text)
    try:
        bot.reply_to(cmd, u"Precisa de ajuda?  Procure o CVV. http://www.cvv.org.br")
        bot.send_message(cmd.chat.id, Commands_Listing)
    except Exception as e:
        try:
            bot.reply_to(cmd, u"Deu merda... %s" % e)
        except Exception as z:
            print z

@bot.message_handler(commands=["fortune", "fortunes", "sorte"])
def Fortune(cmd):
    fortune = os.popen("/usr/games/fortune").read()
    # avoid big answers
    while (len(fortune) > 200):
        fortune = os.popen("/usr/games/fortune").read()
    try:
        bot.reply_to(cmd, "%s" % fortune)
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["rtfm", "RTFM"])
def RTFM(cmd):
    try:
        bot.reply_to(cmd, "Read The F*cking Manual.  Ou leia o Guia Foca GNU/Linux.")
        bot.reply_to(cmd, "http://www.guiafoca.org/")
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["apt-get", "aptitude", "apt"])
def AptCmds(session):
    debug(session.text)
    if re.search("apt-get", session.text):
        try:
            bot.reply_to(session, "Esse bot tem poderes de super vaca.")
            counter = random.randint(0,10)
            while counter:
                counter -= 1
                time.sleep(random.randint(0,10))
                moo = "moo" + random.randint(0,10) * "o"
                bot.send_message(session.chat.id, moo)
        except Exception as e:
            bot.reply_to(session, "apt-get deu BSOD... %s" % e)
        return
    elif re.search("aptitude", session.text):
        try:
            bot.reply_to(session,
                "Palavra africana para: Eu não sei corrigir dependências.")
        except:
            bot.reply_to(session, "Deu merda...")
        return
    elif re.search("apt", session.text):
        debug("On apt")
        try:
            debug("Post on session")
            bot.reply_to(session,
                u"Palavra hipster para: Eu gosto de ver tudo colorido.")
        except Exception as e:
            debug(e)
            bot.reply_to(session, "Deu merda... %s" % e)
        return
    debug("Asking about it on apt loop.")
    bot.reply_to(session, u"Quê?")

@bot.message_handler(commands=["dia", "bomdia"])
def Dia(cmd):
    debug(cmd.text)
    try:
        hoje = date.today()
        semana = hoje.weekday()

        if re.search("bom", cmd.text):
            bot.reply_to(cmd,
            u"""Bom dia pra todos vocês que usam blobs, e pra quem usa GNU também.

O nome do sistema operacional é OSI/Linux e os blobs nos representam.""")

        if semana == 0:
            bot.reply_to(cmd, u"Segunda-Feira sempre tem alguem assim: https://www.youtube.com/watch?v=rp34FE01Q3M")
        elif semana == 1:
            bot.reply_to(cmd, u"Terça Feira: https://www.youtube.com/watch?v=V7eR6wtjcxA")
        elif semana == 2:
            bot.reply_to(cmd, u"Quarta Feira")
        elif semana == 3:
            bot.reply_to(cmd, u"Quinta Feira")
        elif semana == 4:
            bot.reply_to(cmd, u"Sexta-Feira é o dia da Maldade: https://www.youtube.com/watch?v=qys5ObMiKDo")
        elif semana == 5:
            bot.reply_to(cmd, u"https://www.youtube.com/watch?v=rX2Bw-mwnOM")
        elif semana == 6:
            bot.reply_to(cmd, u"Domingo é dia de compilar um kernel")
    except:
        bot.reply_to(cmd, "Deu merda...")

@bot.message_handler(commands=["photo"])
def Photo(cmd):
    debug("Photo")
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    SAVEDIR = "%s/weather/%s/%s" % (os.environ.get('HOME'), year, month)
    if not os.path.exists(SAVEDIR):
        debug(u"Sem fotos")
        bot.reply_to(cmd, u"Sem fotos no momento.")
        return
    photos = os.listdir(SAVEDIR)
    last_photo = sorted(photos)[-1]
    debug(u"Última foto: %s" % last_photo)
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
    curdir = os.curdir
    try:
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
            debug("Lendo pautas")
            os.chdir(PAUTAS)
            os.system("git pull --rebase --no-commit")
            pautas = os.listdir(PAUTAS)
            last_pauta = sorted(pautas)[-1]
            if not re.search("^20", last_pauta):
                last_pauta = sorted(pautas)[-2]
            msg = open("%s/%s" % (PAUTAS, last_pauta)).read()
            #msg = "work in progress"
        elif re.search("^/addpauta", cmd.text):
            os.chdir(PAUTAS)
            os.system("git pull --rebase --no-commit")
            msg = "work in progress"
    except Exception as e:
        try:
            bot.reply_to(cmd, "Deu merda: %s" % e)
        except Exception as z:
            print z

    os.chdir(curdir)
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
    #distro = re.sub(".*distro ", "", distro)
    distro = distro.split()[-1]
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

@bot.message_handler(commands=["xkcd", "dilbert", "vidadeprogramador",
    "tirinhas", "strips", "vidadesuporte", "angulodevista",
    "mandanudes", "nudes", "tirinhadorex"])
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

    if img:
        try:
            img_fd = open(img, 'rb')
            bot.send_photo(cmd.chat.id, img_fd)
        except Exception as e:
            bot.send_message(cmd.chat.id, "Ooopsss... deu merda! %s" % e)
        os.unlink(img)
    else:
        bot.send_message(cmd.chat.id, "É... foi não...")
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
@bot.message_handler(commands=["fofometro", "fofondex", "resetfofos"])
def FofoMetrics(cmd):
    user_name = cmd.from_user.username
    user_id = cmd.from_user.id
    user_1stname = cmd.from_user.first_name

    user = user_name  # backward compatibility
    if not user_name:  # got None
        user_name = "Anonimo da Internet (%s)" % user_id
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
        global simple_lock
        while simple_lock:
            time.sleep(random.random())
        simple_lock = True
        fofondex = None
        try:
            fofondex = pickle.load(open(FOFODB, "rb"))
        except IOError:
            debug("Error reading FOFODB")
            pass
        simple_lock = False
        if not fofondex:
            debug("Using empty fofondex.")
            fofondex = {}
        return fofondex

    def DataWrite(dict_information=None):
        debug("DataWrite")
        global simple_lock
        while simple_lock:
            time.sleep(random.random())
        simple_lock = True
        try:
            if dict_information == None:
                os.unlink(FOFODB)
            else:
                pickle.dump(dict_information, open(FOFODB, "wb"))
        except IOError:
            debug("Failed to save DB")
            pass
            # yap... we lost it...
        simple_lock = False

    def RunTheDice(n=None):
        if n:
            return n
        random.seed(os.urandom(random.randint(0,1000)))
        return random.randint(0,100)

    def TimeDelta(user_id):
        if fofondex.has_key(user_id):
            timestamp = fofondex[user_id]['timestamp']
            now = time.time()
            return now - int(timestamp)
        else:
            return 0
    def InitializeUser(pctg=None):
        if not pctg:
            pctg = RunTheDice()
        return {
                'timestamp' : time.time(),
                'foforate' : pctg,
                'user_name' : user_name,
                'user_1stname' : user_1stname
        }
    def GetPctg(user_id):
        fofondex = DataRead()
        if fofondex.has_key(user_id):
            pctg = fofondex[user_id]['foforate']
        else:
            # initialize user
            pctg = RunTheDice()
            fofondex[user_id] = InitializeUser()
            DataWrite(fofondex)
        return int(pctg)

    if re.search("/resetfofos", cmd.text):
        if user_name == botadm:
            bot.send_message(cmd.chat.id, u"Limpando o fundum que está por aqui." \
                + u"  Vou até jogar creolina.")
            DataWrite()
        else:
            bot.send_message(cmd.chat.id, u"Vai aprender a sair do VI "\
            + "antes de querer vir aqui me dar ordem.")
        return

    if re.search("/fofometro", cmd.text):
        fofondex = DataRead()
        if TimeDelta(user_id) < 24 * 60 * 60:
            pctg = GetPctg(user_id)
        else:
            pctg = RunTheDice()
            fofondex[user_id] = InitializeUser()
            DataWrite(fofondex)

        if re.search("arrumasaporra", cmd.text):
            fofondex = DataRead()
            if user_name == botadm:
                bot.send_message(cmd.chat.id, u"Perdão patrão... Estava aqui " + \
                    u"compilando o emacs e me distraí.  Deixa eu fazer de novo.")
                pctg = RunTheDice(100)
                fofondex[user_id] = InitializeUser(pctg=pctg)
            else:
                bot.send_message(cmd.chat.id, u"Quem você pensa que é pra " + \
                    u"falar comigo dessa maneira?  Sabe quem eu sou???")
                bot.send_message(cmd.chat.id, u"Vou verificar de novo, " + \
                    u"mas só dessa vez.")
                pctg = RunTheDice()
                fofondex[user_id] = InitializeUser(pctg=pctg)
        try:
            msg = u"Hoje %s tem %d%s de ultrafofura mas " % (user_name, pctg, '%')
            msg += u"aquele %d%s de blob binário no kernel." % (100 - pctg, '%',)
            debug(u'%s' % msg)
            DataWrite(fofondex)
            bot.send_message(cmd.chat.id, u'%s' % msg)
        except Exception as e:
            bot.send_message(cmd.chat.id, "Deu ruim... %s" % e)
        return

    if re.search("/fofondex", cmd.text):
        fofondex = DataRead()
        msg = u"Ranking Dollyinho de #UltraFofos:\n"
        ranking = {}
        isUpdated = False
        for u in fofondex.keys():
            delta = TimeDelta(u)
            if delta > 24 * 60 * 60:
                # remove old data
                isUpdated = True
                del fofondex[u]
                continue
            ranking[u] = fofondex[u]['foforate']
        if isUpdated:
            pickle.dump( fofondex, open( FOFODB, "wb" ) )
        i = 1
        for u in sorted(ranking, key=ranking.get, reverse=True):
            pct = fofondex[u]['foforate']
            u_name = fofondex[u]['user_name']
            msg += u"%d) %s: %d%s\n" % (i, u_name, pct, '%')
            i += 1
        del ranking
        try:
            debug(u'%s' % msg)
            bot.send_message(cmd.chat.id, u'%s' % msg)
        except Exception as e:
            bot.send_message(cmd.chat.id, "Deu ruim... %s" % e)

@bot.message_handler(commands=["motivationals", "motivational", "motivacional" ])
def Motivational(cmd):
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
        bot.send_photo(cmd.chat.id, ph)
    except Exception as e:
        bot.reply_to(cmd, "Deu merda: %s" % e)

@bot.message_handler(commands=["oquee", "oqueé"])
def DuckDuckGo(cmd):
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
        print e # get internal
        pass
    if not answer:
        bot.reply_to(cmd, "Não tenho a menor idéia.  Tem de perguntar no google.")
        return
    try:
        bot.reply_to(cmd, answer)
    except Exception as e:
        bot.reply_to(cmd, "Deu merda: %s" % e)

@bot.message_handler(commands=["emacs"])
def Emacs(cmd):
    debug(cmd.text)
    pray = """
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
"""
    try:
        bot.send_message(cmd.chat.id, pray)
    except Exception as e:
        bot.reply_to(cmd, "Um exu-tranca-sistema derrubou tudo aqui: %s" % e)

@bot.message_handler(commands=["mimimi"])
def Mimimizer(session):
    debug(session.text)
    param = session.text.split()
    if len(param) <= 1:
        return
    resp = " ".join(param[1:])
    resp = re.sub("a|e|o|u", "i", resp)
    resp = re.sub("A|E|O|U", "I", resp)
    resp = re.sub(u"á|é|ó|ú", u"í", resp)
    resp = re.sub(u"Á|É|Ó|Ú", u"Í", resp)
    bot.reply_to(session, u"%s" % resp)
    # Falta implementar quem...

@bot.message_handler(commands=["blob"])
def Mimimizer(session):
    debug(session.text)
    msg = u"""
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
"""
    bot.reply_to(session, u"%s" % msg)


@bot.message_handler(commands=["ban"])
def Ban(session):
    debug(session.text)
    bot.reply_to(session, u"Deixa que eu pego ele na hora da saída.")
    # Falta implementar quem...

@bot.message_handler(commands=["fonte", "fontes", "src", "source"])
def Source(session):
    debug(session.text)
    bot.reply_to(session, u"""Estou aqui com 100% de acesso ao conteúdo em:

https://github.com/helioloureiro/homemadescripts/blob/master/stallmanbot.py
""")

@bot.message_handler(func=lambda m: True)
def WhatEver(session):
    debug(session.text)
    if re.search(u"kkkkkk", session.text):
        bot.reply_to(session, u"Hilário.")
        return
    elif re.search(u"hahahaha", session.text):
        bot.reply_to(session, u"Hilário.")
        return
    elif re.search(u"bom dia", session.text.lower()):
        Dia(session)
        return
    #bot.reply_to(session, u"Dude... entendi foi é porra nenhuma.")

while True:
    StartUp()
    try:
        debug("Polling...")
        bot.polling()
    except Exception as e:
        print e
        debug(e)

os.unlink(PIDFILE)

