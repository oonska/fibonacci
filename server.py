#!/usr/bin/env python
import argparse
import multiprocessing
import socket
import struct
import logging


def handle(connection, address):
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == "":
                logger.debug("socket closed remotely")
                break
            logger.debug("data recieved: %r", data)
            connection.sendall(data)
            logger.debug("data sent: %r", data)
    except Exception as e:
        logger.exception("unexpected exception")
        logger.exception(e)
    finally:
        logger.debug("socket closing")
        connection.close()


class Server(object):
    def __init__(self, hostname, port):
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self):
        self.logger.debug("listening")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.hostname, self.port))
        self.sock.listen(1)
        while True:
            conn, address = self.sock.accept()
            self.logger.debug("connection recieved")
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()
            self.logger.debug("process spawned: %r", process)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", dest="address", type=str, default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    options = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    server = Server(options.address, options.port)
    try:
        logging.info("starting up")
        server.start()
    except Exception as e:
        logging.exception("unexpected exception")
        logging.exception(e)
    finally:
        logging.info("shutting down")
        for process in multiprocessing.active_children():
            logging.info("process terminating: %r", process)
            process.terminate()
            process.join()