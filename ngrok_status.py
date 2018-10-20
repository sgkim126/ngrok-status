#!/usr/bin/env python3
""" check status """

import argparse
import binascii
import hashlib
import time
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
            calculated_hmac = hmac(bytes(last_address, 'utf-8'), bytes(secret, 'utf-8'))
            requests.post(target, auth=(last_address, calculated_hmac))
        finally:
            time.sleep(interval)


def hmac(address, secret):
    return binascii.hexlify(hashlib.pbkdf2_hmac('sha256', address, secret, 8)).decode('utf-8')


def read_file(file_name):
    """ read contents of file """
    with open(file_name, 'r') as file:
        return file.read()


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('target')
    PARSER.add_argument('secret_file', metavar='secret-file')
    PARSER.add_argument('interval', type=int)
    ARGS = PARSER.parse_args()
    SECRET = read_file(ARGS.secret_file)
    main(ARGS.target, SECRET, ARGS.interval)
