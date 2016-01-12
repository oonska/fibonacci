#!/usr/bin/env python
import unittest
#  import messages
import client


class MockSocket(object):
    """
    Mocks a socket connection
    """
    def __init__(self):
        """
        Initializes MockSocket and defines some configuration attributes:
            connect_fail: bool, if true mocksocket will raise an error on connect
            invalid_response: bool, if true MockSocket will return invalid data on recv
        """
        self.connect_fail = False
        self.invalid_response = False

    def connect(self, *args, **kwargs):
        """
        Mocks Socket.connect method

        Raises:
            socket.error: raised if self.connect_fail is True
        """
        if self.connect_fail:
            raise client.socket.error

    def sendall(self, *args, **kwargs):
        """
        Mocks Socket.sendall method
        """
        pass

    def recv(self, *args, **kwargs):
        """
        Mocks Socket.recv method

        Returns:
            str, if self.invalid_response is True
            messages.fib_response, if self.invalid_response if False
        """
        if self.invalid_response:
            return "shoes"
        else:
            return client.messages.fib_response.pack(200, 255)

    def close(self):
        """
        Mocks Socket.close method
        """
        pass


class MockClient(client.Client):
    """
    Client using a MockSocket interface
    """
    def __init__(self, address, port):
        """
        Initializes MockClient

        Args:
            address: str, server's IP address or Hostname
            port: int, server's TCP port number
        """
        client.Client.__init__(self, address, port)
        self.sock = MockSocket()


class TestClient(unittest.TestCase):
    """
    Client unittests
    """
    def setUp(self):
        """
        Set up test environment and initialize client connection through MockSocket
        """
        address = "127.0.0.1"
        port = 9090
        client.logging.basicConfig(level=client.logging.DEBUG)
        self.client = MockClient(address, port)

    def testSendRequest(self):
        """
        Test client is able to process a valid request

        This test passes when each sent request returns a status code of 200 and no errors are raised
        """
        self.assertEqual(self.client.send_request(9), (200, 255))
        self.assertEqual(self.client.send_request("3"), (200, 255))

    def testSendRequestInvalidInput(self):
        """
        Test client is able to handle a request containing invalid input

        This test passes when each sent request returns a value of None
        """
        self.assertEqual(self.client.send_request("nine"), None)
        self.assertEqual(self.client.send_request(-3), None)

    def testSendRequestConnectionError(self):
        """
        Test client is able to handle a connection error to server

        For this test MockSocket is configured to raise socket.error on the connect method being called.
        This will simulate a connection issue with a server

        This test passes if send_request returns a status code of 400,1
        """
        self.client.sock.connect_fail = True
        self.assertEqual(self.client.send_request(9), (400, 2))

    def testSendRequestRecieveInvalidResponse(self):
        """
        Test client is able to handle recieving an invalid response from the server

        For this test MockSocket is configured to return an incorrectly packed response on recv.
        This will simulate the server returning unexpected data.

        This test passes if send_request returns a status code of 400,2
        """
        self.client.sock.invalid_response = True
        self.assertEqual(self.client.send_request(9), (400, 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
