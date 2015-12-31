import argparse
import socket


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", dest="address", type=str, default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    options = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((options.address, options.port))
    data = "some data"
    sock.sendall(data)
    result = sock.recv(1024)
    print result
    sock.close()
