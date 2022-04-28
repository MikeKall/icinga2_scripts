#!/bin/python3
# -*- coding: utf-8 -*-

import json
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys
import logging
import logging.handlers
import subprocess
try:
    # For Python 3.0 and later
    from http.server import HTTPServer
    from http.server import BaseHTTPRequestHandler
except ImportError:
    # Fall back to Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler
    from BaseHTTPServer import HTTPServer as HTTPServer

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                   level=logging.INFO,
                   stream=sys.stdout)



class RequestHandler(BaseHTTPRequestHandler):
    """A POST request handler."""

    def do_POST(self):
        logging.info("Hook received")

        if sys.version_info >= (3,0):
            # get payload
            header_length = int(self.headers['Content-Length'])
        else:
            header_length = int(self.headers.getheader('content-length', "0"))

        json_payload = self.rfile.read(header_length)
        json_params = {}
        if len(json_payload) > 0:
            try:
                json_params = json.loads(json_payload)
                if json_params['action'] == 'start':
                    command = 'curl -k --cert /var/lib/icinga2/certs/winmonit-m01.cern.ch.crt --key /var/lib/icinga2/certs/winmonit-m01.cern.ch.key -H \'Accept: application/json\' -X POST \'https://localhost:5665/v1/actions/schedule-downtime\' -d "$(jo -p pretty=true type=Host filter="match(\\\"' + json_params["name"] + '*\\\", host.name)" all_services=true author=Downtime_Manager comment="Patching" fixed=true start_time=$(date +%s -d "+0 hour") end_time=$(date +%s -d "+1 hour"))"'
                    out = subprocess.check_output(command, shell=True, universal_newlines=True)
                    print(out)
                elif json_params['action'] == 'stop':
                    command = 'curl -k --cert /var/lib/icinga2/certs/winmonit-m01.cern.ch.crt --key /var/lib/icinga2/certs/winmonit-m01.cern.ch.key -H \'Accept: application/json\' -X POST \'https://localhost:5665/v1/actions/remove-downtime\' -d \'{"type":"Host", "filter":"host.name ==\\\"' + json_params["name"] + '\\\"", "pretty":true}\''
                    out = subprocess.check_output(command, shell=True, universal_newlines=True)
                    print(command + "\n")
                    print(out)
            except json.decoder.JSONDecodeError:
                print("Exception: " + json_payload)


        #print(command)
        self.send_response(200, "OK")
        self.end_headers()
        return
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.wfile.write(b" ")
        self.end_headers()


def get_parser():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--addr",
                        dest="addr",
                        default="0.0.0.0",
                        help="address where it listens")
    parser.add_argument("--port",
                        dest="port",
                        type=int,
                        default=8666,
                        metavar="PORT",
                        help="port where it listens")
    return parser


def main(addr, port):
    """Start an HTTPServer which waits for requests."""
    httpd = HTTPServer((addr, port), RequestHandler)
    try:
        logging.info("Server started")
        httpd.serve_forever()
    except:
        pass
    finally:
        logging.info("Server stoped")


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    main(args.addr, args.port)