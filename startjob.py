#!/usr/bin/env python

"""Start a job."""

import argparse
import requests
import os
from completejob import make_url, HEADERS

def put_request(url, proxy, cert):
    """Sends a put request."""
    print url
    session = requests.Session()
    session.trust_env = False
    session.proxies = { 'http': proxy } if proxy else {}
    session.headers = HEADERS
    if cert is not None:
        session.verify = cert
    r = session.put(url=url)
    print r.status_code
    if r.ok:
        print r.text
    elif r.text:
        error_file = 'error_from_start.txt'
        with open(error_file, 'w') as fout:
            fout.write(r.text)
        print "[See %s for response text.]"%error_file
    elif r.reason:
        print r.reason

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job_id', type=int, help='Job ID to start (an integer)')
    parser.add_argument('-p', '--proxy',
                        help="proxy to use for posts (default none)")
    url_group = parser.add_mutually_exclusive_group(required=False)
    url_group.add_argument('-u', '--url',
                           help="exact url to post message to")
    url_group.add_argument('-s', '--site', help="site to post message to")
    parser.add_argument('--local', help="local mode", action='store_true')
    args = parser.parse_args()
    if args.site:
        url = make_url(args.site, args.job_id, 'start', args.local)
    else:
        url = args.url
    if args.local and not url:
        url = make_url(None, args.job_id, 'start', args.local)
    if not url:
        exit("Use the --url or --site argument to specify a destination.")
    cert = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cert.crt')
    if not os.path.isfile(cert):
        print "[No cert.crt file in folder -- proceeding without verification]"
        cert = False

    args = parser.parse_args()
    put_request(url, args.proxy, cert)

if __name__ == '__main__':
    main()
