#!/usr/bin/env python

"""Read a received work order from a local file,
and post a "complete work order" message for it.

If you supply the -s argument, e.g.
  -s http://my_server:3500
then the url used would be
  http://my_server:3500/api/v1/work_orders/[N]/complete
where [N] is the work order id.
"""

import os
import argparse
import re
import json
import sys
import requests
import random
import string

HEADERS = { 'Content-type': 'application/json', 'Accept': 'application/json' }

last_barcode_number = None

def new_barcode(num_digits=5, chars=string.digits+string.uppercase):
    """Generates a random barcode of the form FLIM-#####,
    where the # are alpha-numeric characters.
    That gives a random range of 60 million possible barcodes."""
    return 'FLIM-'+(''.join([random.choice(chars) for _ in xrange(num_digits)]))

def read_work_order(order_id, file):
    """Reads the work order from an orders file.
    The file must have lines like "===ORDER 6===" to announce its orders.
    If multiple orders matching are found, the latest is returned.
    Returns None if no matching order is found."""
    ptn = re.compile(r'^===ORDER ?([0-9]*)===')
    lines = None
    on = False
    with open(file, 'r') as fin:
        for line in fin:
            m = ptn.match(line)
            if m:
                g = m.group(1)
                if g and int(g)==order_id:
                    on = True
                    lines = []
                else:
                    on = False
            elif on:
                lines.append(line)
    if lines:
        return ''.join(lines)
    return None

def make_complete(order, cancel=False):
    """Starting from the given order (dict), creates a "complete order" message
    (another dict), containing updated material, new materials, and a new container."""
    order = order['work_order']
    materials = order['materials']
    updated_materials = []
    parent_ids = []
    if materials:
        m = materials[0]
        g = 'male' if m.get('gender')=='female' else 'female'
        updated_materials.append({'_id': m['_id'], 'gender': g})
        parent_ids = [m['_id'] for m in materials]
    barcode = new_barcode()
    new_materials = [
        {
            'container': {
                'barcode': barcode,
                'address': 'A:1',
            },
            'parents': parent_ids,
            'supplier_name': 'test1',
            'gender': 'male',
            'donor_id': 'my_donor_id',
            'phenotype': 'my_phenotype',
            'scientific_name': 'Mus musculus',
            'available': True
        },
        {
            'container': {
                'barcode': barcode,
                'address': 'A:2',
            },
            'parents': parent_ids,
            'supplier_name': 'test2',
            'gender': 'female',
            'donor_id': 'another_donor_id',
            'phenotype': 'another_phenotype',
            'scientific_name': 'Mus musculus',
            'available': True
        },
    ]
    containers = [
        {
          'barcode': barcode,
          'row_is_alpha': True, 'col_is_alpha': False,
          'num_of_rows': 4, 'num_of_cols': 6,
        }
    ]
    comment = 'We %s your order for you.'%('cancelled' if cancel else 'completed')
    result = {
        'work_order_id': order['work_order_id'],
        'comment': comment,
        'updated_materials': updated_materials,
        'new_materials': new_materials,
        'containers': containers,
    }
    return { 'work_order': result }


def send_request(data, url, proxy, cert=None, headers=None):
    """Posts some JSON to the given url."""
    session = requests.Session()
    session.trust_env = False
    session.proxies = { 'http': proxy } if proxy else {}
    session.headers = HEADERS if headers is None else headers
    if cert is not None:
        session.verify = cert
    r = session.post(url=url, data=data)
    print r.status_code
    print r.text

def make_url(site, order_id, cancel):
    if not site.endswith('/'):
        site += '/'
    return '{}api/v1/work_orders/{}/{}'.format(
        site, order_id, 'cancel' if cancel else 'complete'
    )

def complete_order(order_id, filename, url, proxy, cert, cancel):
    """Reads the order from a file; constructs a "complete order" message,
    and sends that to the given url (if a url is given).
    """
    order_json = read_work_order(order_id, filename)
    if order_json is None:
        raise LookupError("No order found with id %r"%order_id)
    order = json.loads(order_json)
    message = make_complete(order, cancel)
    data = json.dumps(message, indent=4)
    print data
    if url:
        send_request(data, url, proxy, cert)
    else:
        print "\nUse the --url or --site argument to specify destination"

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('order_id', metavar='ID', type=int,
                        help='work order ID to respond to')
    parser.add_argument('-f', '--file', default='orders.txt',
                        help="file to read orders from")
    parser.add_argument('-p', '--proxy',
                        help="proxy to use for posts (default none)")
    url_group = parser.add_mutually_exclusive_group(required=False)
    url_group.add_argument('-u', '--url',
                           help="exact url to post message to")
    url_group.add_argument('-s', '--site', help="site to post message to")

    parser.add_argument('--cancel', action='store_true',
                        help="send a cancel instead of a complete")
    
    args = parser.parse_args()

    if args.site:
        url = make_url(args.site, args.order_id, args.cancel)
    else:
        url = args.url
    cert = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cert.crt')
    if not os.path.isfile(cert):
        print "[No cert.crt file in folder -- proceeding without verification]"
        cert = False
    complete_order(args.order_id, args.file, url, args.proxy, cert, args.cancel)
    
if __name__ == '__main__':
    main()
