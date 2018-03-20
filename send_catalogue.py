#!/usr/bin/env python

"""Sends a JSON catalogue as a message to a RabbitMQ instance."""

import pika
import argparse

def send_message(args):
    """Configure the connection and send the contents of the catalogue file"""
    params = pika.ConnectionParameters(host=args.host, port=args.port, virtual_host=args.vhost)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    with open(args.catalogue) as catalogue:
        channel.basic_publish(exchange='aker.catalogues.tx',
                              routing_key='aker.catalogues.new',
                              body=catalogue.read())

    connection.close()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', '-H', default='localhost',
                        help="RabbitMQ host address")
    parser.add_argument('--port', '-p', type=int, default='5672',
                        help="RabbitMQ host port")
    parser.add_argument('--vhost', '-v', default='aker',
                        help="RabbitMQ virtual host name")
    parser.add_argument('--catalogue', '-c', default='catalogue.JSON',
                        help="File containing catalogue JSON")
    args = parser.parse_args()

    send_message(args)

if __name__ == '__main__':
    main()
