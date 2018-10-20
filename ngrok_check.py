#!/usr/bin/env python3
""" check status """

import argparse
import base64
import http.server
import ngrok_status


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
            address = data[:data.rfind(b':')]
            if address == self.last_address:
                return

            received_hmac = data[data.rfind(b':') + 1:].decode('utf-8')
            calculated_hmac = ngrok_status.hmac(address, bytes(secret, 'utf-8'))

            if received_hmac != calculated_hmac:
                return

            self.last_address = address
            print("updated: %s" % self.last_address)

    socket = ('', port)
    httpd = http.server.HTTPServer(socket, Handler)
    httpd.serve_forever()


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('secret_file', metavar='secret-file')
    PARSER.add_argument('port', type=int)
    ARGS = PARSER.parse_args()
    SECRET = ngrok_status.read_file(ARGS.secret_file)
    main(SECRET, ARGS.port)
