#!/usr/bin/env python -tt

"""Send product catalogue (read from a file) to a specified Aker url.
If messages don't get through, try unsetting the proxy in your shell.
"""

import argparse
import requests
import json

HEADERS = { 'Content-type': 'application/json', 'Accept': 'application/json' }

class Product(object):
    def __init__(self):
        self.name = None
        self.version = None
        self.desc = None
        self.unit_cost = None

def build_data(filename):
    product = None
    catalog_data = {'products':[]}
    with open(filename, 'r') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            if line.lower()=='product':
                product = {}
                catalog_data['products'].append(product)
                continue
            k,v = line.split(':', 1)
            k = k.strip()
            v = v.strip()
            if product is None:
                catalog_data[k] = v
            else:
                product[k] = v
    return catalog_data

def send_request(data, url, proxy):
    proxies = { 'http': proxy } if proxy else {}
    r = requests.post(url=url, data=data, proxies=proxies, headers=HEADERS)
    print r.status_code

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', '-u', metavar='AKER_URL', required=True,
                        help="url to post products to")
    parser.add_argument('--file', '-f', metavar='FILENAME', required=True,
                        help="file to read catalogue information from")
    parser.add_argument('--proxy', '-p', metavar='PROXY',
                        help="proxy to use for posts (default none)")
    args = parser.parse_args()
    print args
    req = build_data(args.file)
    print json.dumps(req, indent=4)
    send_request(json.dumps(req), args.url, args.proxy)
    
if __name__ == '__main__':
    main()
