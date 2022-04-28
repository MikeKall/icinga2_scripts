#!/bin/python3
# Python script for icinga2 sms notifications
__author__ = "Mike Kalliafas"
import argparse
import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

parser = argparse.ArgumentParser()
parser.add_argument('-d','--datetime', required=True, help='Date time')
parser.add_argument('-g','--hostgroup',required=False, help='Hostgroup')
parser.add_argument('-l','--hostname',required=True, help='Hostname')
parser.add_argument('-p','--phone',required=True, help='Usermail')
parser.add_argument('-Hs','--hoststate',required=True, help='Host state')
parser.add_argument('-Ss','--servicestate',required=False, help='Service state')
parser.add_argument('-e','--servicename',required=False, help='Service Name')

args = parser.parse_args()

hostname = socket.gethostname()

if "test" in hostname:
    sender = "icinga-test@cern.ch"
else:
    sender = "icinga@cern.ch"

# Define email details
receiver = args.phone+"@mail2sms.cern.ch"
mail_server = "cernmx.cern.ch"
server = smtplib.SMTP(mail_server)
msg = MIMEMultipart()
msg["From"] = sender
msg["To"] = receiver
# =====================================

if args.servicestate:
    body = args.servicename + " is " + args.servicestate + "! (" + args.datetime + ")"
else:
    body = args.hostname + " is " + args.hoststate + "! (" + args.datetime + ")"

plain_text = MIMEText(body, _subtype='plain', _charset='UTF-8')
msg.attach(plain_text)


server.sendmail(sender, receiver, msg.as_string())

server.quit()