#!/usr/bin/env python
import argparse
import logging
import messages
import socket


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", dest="address", type=str, default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    options = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("client")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((options.address, options.port))
    request = None
    while request is None:
        try:
            request = int(raw_input("Please enter an unsigned integer: \n"))
            if request < 0:
                raise ValueError
        except ValueError:
            logger.error("Invalid input: Please enter an unsigned int")
            request = None
    logger.debug("request generated: %r" % request)
    request = messages.fib_request.pack(request)
    sock.sendall(request)
    logger.debug("request sent: %r" % request)

    response = sock.recv(1024)
    logger.debug("response recieved: %r" % response)
    response = messages.fib_response.unpack(response)
    logger.debug("response unpacked: %r-%r" % (response[0], response[1]))
    if response[0] == 200:
        logger.info("The answer is: %r" % response[1])
    else:
        logger.error("Server error: %r-%r" % (response[0], response[1]))
        logger.error("Please check server logs for more details.")
    sock.close()
