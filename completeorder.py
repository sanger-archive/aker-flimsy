#!/usr/bin/env python -tt

"""Read a received work order from a local file, and post a "complete work order" message for it.
"""

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

def make_complete(order):
    """Starting from the given order (dict), creates a "complete order" message
    (another dict), containing updated material, new materials, and a new container."""
    order = order['work_order']
    materials = order['materials']
    updated_materials = []
    parent_ids = []
    if materials:
        m = materials[0]
        g = 'male' if m.get('gender')=='female' else 'female'
        updated_materials.append({'material_id': m['material_id'], 'gender': g, 'donor_id': '1', 
            'common_name': 'Homo Sapiens', 'supplier_name': 'a name', 'phenotype': 'dd'})
        parent_ids = [m['material_id'] for m in materials]
    barcode = new_barcode()
    new_materials = [
        {
            'container': {
                'barcode': barcode,
                'address': 'A:1',
            },
            'supplier_name': 'test1',
            'parents': parent_ids,
            'gender': 'male',
            'donor_id': 'my_donor_id',
            'phenotype': 'my_phenotype',
            'common_name': 'Mouse',
        },
        {
            'container': {
                'barcode': barcode,
                'address': 'A:2',
            },
            'supplier_name': 'test2',
            'parents': parent_ids,
            'gender': 'female',
            'donor_id': 'another_donor_id',
            'phenotype': 'another_phenotype',
            'common_name': 'Mouse',
        },
    ]
    containers = [
        {
          'barcode': barcode,
          'row_is_alpha': True, 'col_is_alpha': False,
          'num_of_rows': 4, 'num_of_cols': 6,
        }
    ]
    result = {
        'work_order_id': order['work_order_id'],
        'comment': "Now with chocolate.",
        'updated_materials': updated_materials,
        'new_materials': new_materials,
        'containers': containers,
    }
    return { 'work_order': result }


def send_request(data, url, proxy, headers=None):
    """Posts some JSON to the given url."""
    session = requests.Session()
    session.trust_env = False
    session.proxies = { 'http': proxy } if proxy else {}
    session.headers = HEADERS if headers is None else headers
    r = session.post(url=url, data=data)
    print r.status_code

def complete_order(order_id, filename, url, proxy):
    """Reads the order from a file; constructs a "complete order" message,
    and sends that to the given url (if a url is given).
    """
    order_json = read_work_order(order_id, filename)
    if order_json is None:
        raise LookupError("No order found with id %r"%order_id)
    order = json.loads(order_json)
    message = make_complete(order)
    data = json.dumps(message, indent=4)
    print data
    if url:
        send_request(data, url, proxy)
    else:
        print "\nUse the --url argument to specify destination"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('order_id', metavar='ID', type=int,
                        help='work order ID to respond to')
    parser.add_argument('-f', '--file', default='orders.txt',
                        help="file to read orders from")
    parser.add_argument('-u', '--url',
                        help="url to post message to")
    parser.add_argument('-p', '--proxy',
                        help="proxy to use for posts (default none)")
    args = parser.parse_args()
    complete_order(args.order_id, args.file, args.url, args.proxy)
    
if __name__ == '__main__':
    main()
