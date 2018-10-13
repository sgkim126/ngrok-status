#!/usr/bin/env python3
""" check status """

import argparse
import time
import hashlib
import json
import requests


def main(target, secret, interval):
    """ main """
    last_address = None
    while True:
        try:
            try:
                ngrok_status = requests.get('http://127.0.0.1:4040/api/tunnels').json()
                address = ngrok_status['tunnels'][0]['public_url']
            except requests.exceptions.ConnectionError:
                continue
            except json.decoder.JSONDecodeError:
                continue
            if last_address == address:
                continue
            last_address = address
            print(last_address)
            blake = hashlib.blake2b(digest_size=16) # pylint: disable=E1123
            blake.update(bytes(last_address, 'utf-8'))
            blake.update(bytes(secret, 'utf-8'))
            requests.post(target, auth=(last_address, blake.hexdigest()))
        finally:
            time.sleep(interval)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('target')
    PARSER.add_argument('secret')
    PARSER.add_argument('interval', type=int)
    ARGS = PARSER.parse_args()
    main(ARGS.target, ARGS.secret, ARGS.interval)
