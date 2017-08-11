#! /usr/bin/python
# -*- coding: utf-8 -*-

import csv
import smtplib
import os

DB = "pyconse_talks.csv"

gmail_user = "helio.loureiro@gmail.com"
os.system("stty -echo")
gmail_pwd = raw_input("Enter your password for gmail: ")
os.system("stty echo")

"""
### GMAIL ###
smtp.gmail.com
Requer SSL: Sim
Requer TLS: Sim (se disponível)
Requer autenticação: Sim
Porta para SSL: 465
Porta para TLS/STARTTLS: 587
"""
smtpserver = smtplib.SMTP("smtp.gmail.com",587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user, gmail_pwd)

def make_body(author, title):
    return """
Hi %s,

The PyCon Sweden board regrets to inform you that yourproposed talk
"%s"
was not selected for PyCon Sweden 2017.

This was a tough decision but ultimately there were only a few slots available
to fill in the schedule.

We hope you can attend the conference! There will be a space for shorter
lightning talks with a signup sheet in the morning and I encourage you to sign
up to present your topic there.


Best Regards,
Helio Loureiro
in behalf of PyCon Sweden Board


""" % (author, title)

for line_array in csv.reader(open(DB).readlines()):
    (talk_id, score, title, author, email, talk_time, others) = line_array
    if int(talk_id) < 12:
        continue
    print "ID: %s" % talk_id
    print "\t%s - %s<%s>" % (title, author, email)
    destination = "%s<%s>" % (author, email)
    header = "To: %s\n" % destination
    header += "From: Helio Loureiro<%s>\n" % gmail_user
    header += "Cc: PyCon Sweden <info@pycon.se>\n"
    header += "Subject: Information about your proposed talk \"%s\" to PyCon Sweden 2017\n" % title
    print "%s) %s" % (talk_id, header)
    msg = header + make_body(author, title)
    smtpserver.sendmail(gmail_user, destination, msg)
    #print 'done!'

smtpserver.close()
