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
import shutil
import random
import pickle

"""
Super ultra bot.

Message to sendo to @BotFather about its usage.

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
fofometro - Quão fofo você é?  Tente.
fofondex - Ranking de fofura.
fortune - A sorte do dia.  Ou não.
date - A data atual.
uptime - Somente os fortes entenderão.
mandanudes - Pura sensualidade.
nudes - Sensualidade dum jeito mais rápido.
emacs - Religião é coisa séria.  Principalmente a parte do vinho e pecado.
motivational - Pra melhorar *aquela* segunda-feira.

"""

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
SCRIPTHOME = "%s/homemadescripts" % HOME
FOFODB = "%s/fofondex.db" % HOME

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

def StartUp():
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
            res = os.system("%s %s" % (sys.executable, sys.argv[0]) )
            if res != 0:
                debug("Versão bugada")
                sys.exit(1)
            debug("Updating bot...")
            shutil.copy(botname, "%s/bin/%s" % (HOME, botname))
            debug("Bot version updated.")
    # check first
    python = sys.executable
    os.execl(python, python, *sys.argv)

debug("Starting bot for FreeSpeech")
bot = telebot.TeleBot(key)

@bot.message_handler(commands=["oi", "hello", "helloworld"])
def HelloWorld(cmd):
    debug(cmd.text)
    try:
        bot.send_message(cmd.chat.id, "GNU world")
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
        bot.send_message(cmd.chat.id, "#UltraFofos é o grupo super fofis de defensores de software livre." + \
            "Veja mais em: https://www.youtube.com/watch?v=eIRk38d32vA")
    except Exception as e:
        try:
            bot.send_message(cmd.chat.id, "Deu merda... %s" % e)
        except Exception as z:
            printz

@bot.message_handler(commands=["reload"])
def Reload(cmd):
    debug(cmd.text)
    if not cmd.from_user.username == 'HelioLoureiro':
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
                res = os.system("%s %s" % (sys.executable, sys.argv[0]) )
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
        bot.reply_to(cmd, "Precisa de ajuda?  Procure o CVV. http://www.cvv.org.br")
    except Exception as e:
        try:
            bot.reply_to(cmd, "Deu merda... %s" % e)
        except Exception as z:
            print z

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

@bot.message_handler(commands=["apt-get"])
def RTFM(cmd):
    try:
        bot.reply_to(cmd, "Esse bot tem poderes de super vaca.")
        counter = random.randint(0,10)
        while counter:
            counter -= 1
            time.sleep(random.randint(0,10))
            moo = "mo" + random.randint(0,10) * "o"
            bot.send_message(cmd.chat.id, moo)
    except Exception as e:
        bot.reply_to(cmd, "apt-get deu BSOD... %s" % e)

@bot.message_handler(commands=["aptitude"])
def RTFM(cmd):
    try:
        bot.reply_to(cmd, "Palavra africana para: Eu não sei corrigir dependências.")
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
    "mandanudes", "nudes"])
def Comics(cmd):
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
                    tmp_img = p.split("=")[-1]
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

@bot.message_handler(commands=["fofometro", "fofondex"])
def FofoMetrics(cmd):
    user = cmd.from_user.username
    try:
        fofondex = pickle.load( open( FOFODB, "rb" ) )
    except IOError:
        fofondex = {}

    """"
    Data struct:
        'username': {
            'timestamp' : dateinseconds,
            'foforate' : pctg
            }
    """

    def RunTheDice():
        return random.randint(0,100)

    def TimeDelta(user):
        if fofondex.has_key(user):
            timestamp = fofondex[user]['timestamp']
            now = time.time()
            return now - int(timestamp)
        else:
            return 0

    def GetPctg(user):
        if fofondex.has_key(user):
            pctg = fofondex[user]['foforate']
        else:
            pctg = RunTheDice()
            fofondex[user] = {
                'timestamp' : time.time(),
                'foforate' : pctg
                }
            pickle.dump( fofondex, open( FOFODB, "wb" ) )
        return int(pctg)

    if re.search("/fofometro", cmd.text):
        if TimeDelta(user) < 24 * 60 * 60:
            pctg = GetPctg(user)
        else:
            pctg = RunTheDice()
            fofondex[user] = {
                'timestamp' : time.time(),
                'foforate' : pctg
                }
            pickle.dump( fofondex, open( FOFODB, "wb" ) )
        try:
            msg = u"Hoje %s tem %d%s de ultrafofura mas " % (user, pctg, '%')
            msg += u"aquele %d%s de blob binário no kernel." % (100 - pctg, '%',)
            debug(u'%s' % msg)
            bot.send_message(cmd.chat.id, u'%s' % msg)
        except Exception as e:
            bot.send_message(cmd.chat.id, "Deu ruim... %s" % e)
        return

    if re.search("/fofondex", cmd.text):
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
        for u in sorted(ranking, key=ranking.get, reverse=True):
            pct = fofondex[u]['foforate']
            msg += u"%s: %d%s\n" % (u, pct, '%')
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

while True:
    try:
        debug("Polling...")
        bot.polling()
    except Exception as e:
        print e

os.unlink(PIDFILE)

