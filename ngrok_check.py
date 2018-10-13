#!/usr/bin/env python3
""" check status """

import argparse
import base64
import http.server
import hashlib


def main(secret, port):
    """ main """
    class Handler(http.server.BaseHTTPRequestHandler):
        """ Http handler """
        last_address = None

        """ handler """
        def do_POST(self): # pylint: disable=C0103
            """ handle post """
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'')

            data = base64.b64decode(self.headers.get('Authorization')[len('Basic '):])
            address = data[0:len(data) - 33]
            if address == self.last_address:
                return

            hmac = data[len(data) - 32:].decode('utf-8')

            blake = hashlib.blake2b(digest_size=16) # pylint: disable=E1123
            blake.update(address)
            blake.update(bytes(secret, 'utf-8'))
            if hmac != blake.hexdigest():
                return

            self.last_address = address
            print("updated: %s" % self.last_address)

    socket = ('', port)
    httpd = http.server.HTTPServer(socket, Handler)
    httpd.serve_forever()


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('secret')
    PARSER.add_argument('port', type=int)
    ARGS = PARSER.parse_args()
    main(ARGS.secret, ARGS.port)
