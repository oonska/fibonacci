#!/usr/bin/env python
import argparse
import multiprocessing
import socket
import logging
import messages


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


def handle(connection, address):
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("connected %r at %r", connection, address)
        while True:
            request = connection.recv(1024)
            if request == "":
                logger.debug("socket closed remotely")
                break
            logger.debug("request recieved: %r", request)
            request = messages.fib_request.unpack(request)[0]
            logger.debug("request unpacked: %r", request)
            response = fib(request)
            logger.debug("response generated: %r", response)
            response = messages.fib_response.pack(200, response)
            connection.sendall(response)
            logger.debug("response sent: %r", response)
    except Exception as e:
        logger.exception("unexpected exception")
        logger.exception(e)
        response = messages.fib_response.pack(400, 0)
        connection.sendall(response)
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

    def stop(self):
        for process in multiprocessing.active_children():
            self.logger.info("process terminating: %r", process)
            process.terminate()
            process.join()
        self.logger.debug("closing socket")
        self.sock.close()

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
    except KeyboardInterrupt:
        logging.info("signal recieved")
    except Exception as e:
        logging.error("unexpected exception")
        logging.error(e)
    finally:
        logging.info("shutting down")
        server.stop()
