#!/usr/bin/env python

import pika
import argparse

""""Sends a JSON catalogue as a message to a RabbitMQ instance"""

def send_message(args):
    """Configure the connection and send the contents of the catalogue file"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.host, port=args.port, virtual_host=args.vhost))
    channel = connection.channel()

    with open(args.catalogue) as catalogue:
        channel.basic_publish(exchange='aker.catalogues.tx',
                              routing_key='aker.catalogues.new',
                              body=catalogue.read())

    connection.close()

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', '-H', type=str, default='localhost',
                        help="RabbitMQ Host Address")
    parser.add_argument('--port', '-p', type=str, default='5672',
                        help="RabbitMQ Host Port")
    parser.add_argument('--vhost', '-vh', type=str, default='aker',
                        help="RabbitMQ Virtual Host Name")
    parser.add_argument('--catalogue', '-c', type=str, default='catalogue.JSON',
                        help="File containing catalogue JSON")
    args = parser.parse_args()

    send_message(args)

if __name__ == '__main__':
    main()
