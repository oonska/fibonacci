#!/usr/bin/env python
import argparse
import logging
import messages
import socket


class Client(object):
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.logger = logging.getLogger("client")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_request(self, request):
        try:
            request = int(request)
            if request < 0:
                raise ValueError
        except ValueError:
            return None
        self.logger.debug("request recieved: %r" % request)
        request = messages.fib_request.pack(request)
        try:
            self.sock.connect((self.address, self.port))
            self.logger.debug("client connected: %r:%r" % (self.address, self.port))
            self.sock.sendall(request)
            self.logger.debug("request sent: %r" % request)
            response = self.sock.recv(1024)
            self.logger.debug("response recieved: %r" % response)
        except socket.error:
            self.logger.error("unable to connect to server")
            return (400, 2)
        finally:
            self.sock.close()
            self.logger.debug("client disconnected")
        try:
            response = messages.fib_response.unpack(response)
        except messages.struct.error:
            self.logger.error("invalid response from server")
            return (400, 1)
        self.logger.debug("response unpacked: %r-%r" % (response[0], response[1]))
        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", dest="address", type=str, default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    options = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)

    client = Client(options.address, options.port)
    while True:
        response = None
        while response is None:
            request = raw_input("Please enter an unsigned integer: \n")
            response = client.send_request(request)
        if response[0] == 200:
            print "The answer is: %r" % response[1]
        else:
            raise Exception("Error: %r-%r" % (response[0], response[1]))
        rerun = raw_input("Would you like to test another number? [Y/n]")
        if rerun.lower() != "y":
            break
