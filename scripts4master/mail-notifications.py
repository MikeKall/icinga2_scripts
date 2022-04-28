#!/bin/python3
# Python script for icinga2 mail notifications
__author__ = "Mike Kalliafas"
import argparse
import socket
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Email_Notification:

    def __init__(self, args_datetime, args_hostgroup, args_hostname, args_usermail, args_type, args_hoststate, args_houtput, args_servicename,
                                args_hostdisplayname, args_soutput, args_servicestate ,args_servicedisplayname ,args_ipv4 ,args_ipv6 ,args_author , args_comment ): # 0
        
        self.datetime                = args_datetime
        self.hostgroup               = args_hostgroup
        self.hostname                = args_hostname
        self.usermail                = args_usermail
        self.type                    = args_type
        self.host_state              = args_hoststate
        self.host_output             = args_houtput
        self.service_name            = args_servicename
        self.host_display_name       = args_hostdisplayname
        self.service_output          = args_soutput
        self.service_state           = args_servicestate
        self.service_display_name    = args_servicedisplayname
        self.ipv4                    = args_ipv4
        self.ipv6                    = args_ipv6 
        self.author                  = args_author
        self.comment                 = args_comment

    def construct_email(self):
        hostname = socket.gethostname()

        if "test" in hostname:
            sender = "icinga-test@cern.ch"
            icingaweb = "https://winmonit-w01-test.cern.ch/icingaweb2/authentication/login"
        else:
            sender = "icinga@cern.ch"
            icingaweb = "https://winmonit-w01.cern.ch/icingaweb2/authentication/login"

        # Define email details
        mail_server = "cernmx.cern.ch"
        server = smtplib.SMTP(mail_server)
        receiver = self.usermail
        message = MIMEMultipart("alternative")
        message["From"] = sender
        message["To"] = receiver
        # =====================================


        if self.service_state is None:
            # Host Notification

            message["Subject"] = "[" + self.type + "]" +  " host " + self.host_display_name + " is " + self.host_state + "!"

            html = """\
            <html>
                <head>
                    <style>
                        table {
                            width:50%;
                            text-align:center;
                            font-size:16px;
                            border: 1px solid black;
                            /*background-color: #0095bf;*/
                        }
                        .details {
                            font-size:15px;
                            padding: 5px;
                            text-align: right;
                            width: 40%;
                        }
                        #subdetails {
                            text-align: left;
                            width: 60%;
                        }
                        tr {
                            width:100%
                        }
                        td {
                            padding: 10px;
                            word-spacing: 10px;
                        }
                        th {
                            font-size:22px;
                        }
                    </style>
                </head>
                <body>
                    <center>
                    <table>
                        <tr><td colspan="2"><hr noshade size="2px" width="50%" color=""" + self.message_color(self.host_state) + """></td></tr> 
                        <tr><th colspan="2"> ICINGA2 REPORT </th></tr>
                        <tr><td colspan="2"><a href="https://winmonit-w01.cern.ch/icingaweb2/authentication/login" style="word-spacing: 2px;">Icinga2 Web</a></td></tr>
                        <tr><td colspan="2"><strong>""" + self.host_display_name + """</strong>   is <strong style="background-color:""" + self.message_color(self.host_state) + """; color:white">""" + self.host_state + """ </strong></td></tr>
                        <tr><td class="details">Group:</td><td class="details" id="subdetails"> <em>"""
                        
            for item in self.hostgroup:
                html += item + " " 
            
            html += """</em></td></tr>
                        <tr><td class="details">When: </td><td class="details" id="subdetails"><em>"""  + self.datetime + """</em></td></tr>
                        <tr><td class="details">Host: </td><td class="details" id="subdetails"><em>"""  + self.hostname + """</em></td></tr>
                    """
            
            formated_output = re.split('\n', self.host_output)
        else:
            # Service Notification

            message["Subject"] = "[" + self.type + "]" +  self.service_display_name + " on " + self.host_display_name + " is " + self.service_state + "!"

            html = """\
                <html>
                    <head>
                        <style>
                            table {
                                width:50%;
                                text-align:center;
                                font-size:16px;
                                border: 1px solid black;
                                /*background-color: #0095bf;*/
                            }
                            .details {
                                font-size:15px;
                                padding: 5px;
                                text-align: right;
                                width: 40%;
                            }
                            #subdetails {
                                text-align: left;
                                width: 60%;
                            }
                            tr {
                                width:100%
                            }
                            td {
                                padding: 10px;
                                word-spacing: 10px;
                            }

                            th {
                                font-size:22px;
                            }
                        </style>
                    </head>
                    <body>
                        <center>
                        <table>
                            <tr><td colspan="2"><hr noshade size="2px" width="50%" color=""" + self.message_color(self.service_state) + """></td></tr> 
                            <tr><th colspan="2"> ICINGA2 REPORT </th></tr>
                            <tr><td colspan="2"><a href=" """ + icingaweb + """ " style="word-spacing: 2px;">Icinga2 Web</a></td></tr>
                            <tr><td colspan="2"><strong style="word-spacing: 2px;">""" + self.service_display_name + """</strong> on <strong>""" + self.host_display_name + """</strong> 
                            is <strong style="background-color:""" + self.message_color(self.service_state) + """; color:white">""" + self.service_state + """ </strong></td></tr>
                            
                            <tr><td class="details">Group:</td><td class="details" id="subdetails"> <em>""" 
            for item in self.hostgroup:
                html += item + " " 

            html += """</em></td></tr>
                            <tr><td class="details">When: </td><td class="details" id="subdetails"><em>"""  + self.datetime + """</em></td></tr>
                            <tr><td class="details" style="word-spacing: 2px;">Service: <td class="details" id="subdetails"><em>"""  + self.service_display_name + """</em></td></tr>
                            <tr><td class="details">Host: </td><td class="details" id="subdetails"><em>"""  + self.hostname + """</em></td></tr>
                        """

            formated_output = re.split('\n', self.service_output)

        if self.ipv4:
            html += """<tr><td class="details">IPv4: </td><td class="details" id="subdetails"><em>"""  + self.ipv4 + """</em></td></tr>"""


        if self.comment:
            html += """<tr><td class="details"><strong>""" + self.author + """</strong> says: </td><td class="details" id="subdetails">""" + self.comment + """</td></tr>"""
            html += """<tr><td colspan="2" style="text-decoration: underline; padding:10px">Output</td></tr>"""
        else:
            html += """<tr><td colspan="2" style="text-decoration: underline; padding:10px">Output</td></tr>"""


        

        for line in formated_output:
            html += """<tr><td colspan="2" style="padding:5px">""" + line + """</tr></td>"""

        html +="</table></center><br><br><br><br><br><br><br><br><br><br><br><br><br></body></html>"

        self.send_email(html, message, server, sender, receiver)

    def message_color(self, state):
        if state == "OK" or state == "UP":
            color = "green"
        elif state == "WARNING":
            color = "orange"
        elif state == "CRITICAL" or state == "DOWN":
            color = "red"
        else:
            color = "purple"
        
        return color


    def send_email(self, html, message, server, sender, receiver):
        print("Sending...")
        part1 = MIMEText(html, "html")

        message.attach(part1)

        server.sendmail(sender, receiver, message.as_string())
        #print ("Email Sent: "+ str(datetime.now()))

        server.quit()
        print("Sent")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--datetime', required=True, help='Date time')
    parser.add_argument('-g','--hostgroup',required=True, help='Hostgroup', action='append')
    parser.add_argument('-l','--hostname',required=True, help='Hostname')
    parser.add_argument('-r','--usermail',required=True, help='Usermail')
    parser.add_argument('-t','--type',required=True, help='Notification type')
    
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
    notification  = Email_Notification(args.datetime, args.hostgroup, args.hostname, args.usermail, args.type, args.hoststate, args.houtput, args.servicename,
                                args.hostdisplayname, args.soutput, args.servicestate ,args.servicedisplayname ,args.ipv4 ,args.ipv6 ,args.author , args.comment)
    notification.construct_email()


