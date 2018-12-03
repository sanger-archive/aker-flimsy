#!/usr/bin/env python

"""Very simple listener to receive POST requests and write them to a file.
"""

import os
import argparse
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    """Handler for incoming requests.
    The class variable output_file lets you record the
    received jobs to a local file."""
    output_file = None
    def do_POST(self):
        data = self.post_data()
        try:
            data = data['data'][0]['attributes']
            job_id = data['job_id']
        except KeyError:
            print "[This does not match my expectations of a job.]"
            job_id = ''
        data = json.dumps(data, indent=4)
        print "\n"
        print data
        if self.output_file:
            self.write_to_file(job_id, data)
        self.send_response(200)
    def post_data(self):
        n = int(self.headers.getheader('content-length', 0))
        return json.loads(self.rfile.read(n))
    def write_to_file(self, job_id, data):
        print "[Writing to %r]"%self.output_file
        with open(self.output_file, 'a') as fout:
            fout.write("===JOB %s===\n"%job_id)
            fout.write(data)
            fout.write('\n\n')

def confirm(prompt):
    """Ask the user a question until they answer yes or no.
    Returns true or false respectively."""
    print prompt
    while True:
        answer = raw_input('> ').strip().lower()
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        print "Press answer yes or no."

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-p', '--port', default=3400, type=int,
                            help="port to listen on (default is 3400)")
    parser.add_argument('-o', '--output', metavar='PATH', default='jobs.txt',
                            help="file to write to (default is jobs.txt)")
    write_mode_group = parser.add_mutually_exclusive_group(required=False)
    write_mode_group.add_argument('-f', '--force', action='store_true',
                                      help="overwrite file without asking")
    write_mode_group.add_argument('-a', '--append', action='store_true',
                                      help="append to the file")
    args = parser.parse_args()
    filename = args.output
    if os.path.isfile(filename):
        if not (args.force or args.append
                or confirm("File %r exists. OK to overwrite?"%filename)):
            return
    elif os.path.exists(filename):
        raise IOError("Path %r is not available."%filename)
    if not args.append:
        with open(filename, 'w'):
            pass # empty the file
    Handler.output_file = filename
    server = HTTPServer(('0.0.0.0', args.port), Handler)
    try:
        print "Listening on port %s ..."%args.port
        server.serve_forever()
    finally:
        print "Closing"
        server.socket.close()

if __name__=='__main__':
    main()
