import argparse
import socket
import messages


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", dest="address", type=str, default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    options = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((options.address, options.port))
    request = None
    while request is None:
        try:
            request = int(raw_input("Please enter an unsigned integer: \n"))
            if request < 0:
                raise ValueError
        except ValueError:
            print "Invalid input: Please enter an unsigned int"
            request = None

    print "raw request", request
    request = messages.fib_request.pack(request)
    print "packed request", repr(request)

    sock.sendall(request)
    response = sock.recv(1024)

    print "packed response", repr(response)
    response = messages.fib_response.unpack(response)
    print "unpacked response", response
    if response[0] == 200:
        print "The answer is: %r" % response[1]
    else:
        print "Server error: %r-%r" % (response[0], response[1])
        print "Please check server logs for more details."
    sock.close()
