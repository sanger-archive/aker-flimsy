#!/usr/bin/env python

"""Very simple listener to receive POST requests and print them out.
"""

import argparse
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

all_orders = []

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.post_data()
        data = json.dumps(data, indent=4)
        all_orders.append(data)
        print "\n"*5
        print "All orders received:"
        for i, order in enumerate(all_orders, 1):
            print "====== ORDER %s ======"%i
            print order
        self.send_response(200)
    def post_data(self):
        n = int(self.headers.getheader('content-length', 0))
        return json.loads(self.rfile.read(n))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-p', '--port', default=3400, type=int, help="port to listen on")
    args = parser.parse_args()
    server = HTTPServer(('0.0.0.0', args.port), Handler)
    try:
        print "Listening on port %s ..."%args.port
        server.serve_forever()
    finally:
        print "... Closing"
        server.socket.close()

if __name__=='__main__':
    main()
