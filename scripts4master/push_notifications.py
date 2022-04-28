#!/bin/python3
# Python script for icinga2 push notifications
__author__ = "Mike Kalliafas"
import argparse
import socket
import requests

parser = argparse.ArgumentParser()
parser.add_argument('-d','--datetime', required=True, help='Date time')
parser.add_argument('-g','--hostgroup',required=True, help='Hostgroup')
parser.add_argument('-l','--hostname',required=True, help='Hostname')
parser.add_argument('-r','--usermail',required=True, help='Usermail')
parser.add_argument('-k','--key',required=True, help='API key')
parser.add_argument('-ch','--channel',required=True, help='Channel')

parser.add_argument('-t','--type',required=False, help='Notification type')
parser.add_argument('-Hs','--hoststate',required=False, help='Host state')
parser.add_argument('-Ho','--houtput',required=False, help='Host output')
parser.add_argument('-e','--servicename',required=False, help='Service Name')
parser.add_argument('-n','--hostdisplayname',required=False, help='Host display name')
parser.add_argument('-So','--soutput',required=False, help='Service output')
parser.add_argument('-Ss','--servicestate',required=False, help='Service state')
parser.add_argument('-u','--servicedisplayname',required=False, help='Service display name')
parser.add_argument('-4','--ipv4',required=False, help='Host ipv4 address')
parser.add_argument('-6','--ipv6',required=False, help='Host ipv6 address')
parser.add_argument('-b','--author',required=False, help='Notification author')
parser.add_argument('-c','--comment',required=False, help='Notification comment')

args = parser.parse_args()


hostname = socket.gethostname()

if "test" in hostname:
    sender = "icinga-test@cern.ch"
    icingaweb = "https://winmonit-w01-test.cern.ch/icingaweb2/authentication/login"
else:
    sender = "icinga@cern.ch"
    icingaweb = "https://winmonit-w01.cern.ch/icingaweb2/authentication/login"




url = 'https://api-notifications.app.cern.ch/notifications'

header = {
    'Content-Type': 'application/json', 
    'Authorization': 'Bearer ' +  args.key
    }


if args.servicestate is None:
    # Host notification

    if args.hoststate == "DOWN":
        
        color = "red"
        importance = "IMPORTANT"

    elif args.hoststate == "UP":
        
        color = "green"
        importance = "NORMAL"

    else:
        color = "purple"
        importance = "LOW"


    data = {
        'notification':
            {
                'target': args.channel,
                'summary': args.hostdisplayname + " is " + args.hoststate + "!",
                'priority': importance,
                'body':"""
                <table style="width:50%;text-align:center;font-size:16px;">
                    <tr style="width:100%"><td colspan="2"><strong>""" + args.hostdisplayname + """</strong> is <strong style="background-color:""" + color + """; color: white "> """ + args.hoststate + """ </strong></td></tr>
                    <tr style="width:100%"><td style="font-size:15px;padding: 5px;text-align: right;width: 50%;">Group:</td><td  style="font-size:15px;padding: 5px;text-align: left;width: 50%;"> <em>""" + args.hostgroup + """</em></td></tr>
                    <tr style="width:100%"><td style="font-size:15px;padding: 5px;text-align: right;width: 50%;">When: </td><td  style="font-size:15px;padding: 5px;text-align: left;width: 50%;"><em>"""  + args.datetime + """</em></td></tr>
                    <tr style="width:100%"><td style="font-size:15px;padding: 5px;text-align: right;width: 50%;">Host: </td><td  style="font-size:15px;padding: 5px;text-align: left;width: 50%;"><em>"""  + args.hostname + """</em></td></tr>
                </table>
                """
            }
    }
else:
    # Service Notification

    if args.servicestate == "CRITICAL":
        
        color = "red"
        importance = "IMPORTANT"

    elif args.servicestate == "OK":
        
        color = "green"
        importance = "NORMAL"
    else:
        color = "purple"
        importance = "LOW"

    data = {
        'notification':
            {
                'target': args.channel,
                'summary': args.servicedisplayname + " is " + args.servicestate + "!",
                'priority':importance,
                'body':"""
                <table style="width:50%;text-align:center;font-size:16px;">
                    <tr style="width:100%"><td colspan="2"><strong>""" + args.servicedisplayname + """</strong> is <strong style="background-color:""" + color + """; color: white ">""" + args.servicestate + """ </strong></td></tr>
                    <tr style="width:100%"><td style="font-size:15px;padding: 5px;text-align: right;width: 50%;">Group:</td><td  style="font-size:15px;padding: 5px;text-align: left;width: 50%;"> <em>""" + args.hostgroup + """</em></td></tr>
                    <tr style="width:100%"><td style="font-size:15px;padding: 5px;text-align: right;width: 50%;">When: </td><td  style="font-size:15px;padding: 5px;text-align: left;width: 50%;"><em>"""  + args.datetime + """</em></td></tr>
                    <tr style="width:100%"><td style="font-size:15px;padding: 5px;text-align: right;width: 50%;">Host: </td><td  style="font-size:15px;padding: 5px;text-align: left;width: 50%;"><em>"""  + args.hostname + """</em></td></tr>
                </table>
                """
            }
    }


x = requests.post(url, json = data, headers = header)

