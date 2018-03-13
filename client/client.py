import zmq

import sys
import threading

class Client(object):

    def __init__(self, server_host, server_port, chat_pipe, username):
        self.server_host = server_host
        self.server_port = server_port
        
        self.chat_socket = None
        self.chat_pipe = chat_pipe

        self.username = username

        self.context = zmq.Context()
        self.poller = zmq.Poller()

    def connect_to_server(self):
        self.chat_socket = self.context.socket(zmq.REQ)

        connect_address = 'tcp://{}:{}'.format(
            self.server_host, self.server_port)
        self.chat_socket.connect(connect_address)

    def register_poller(self):
        self.poller.register(self.chat_socket, zmq.POLLIN)

    def reconnect_to_server(self):
    	# Reset connection
        self.poller.unregister(self.chat_socket)
        self.chat_socket.setsockopt(zmq.LINGER, 0)
        self.chat_socket.close()

        self.connect_to_server()
        self.register_poller()

    # Receive input from user
    def receive_input(self):
        return self.chat_pipe.recv_string()

    def send_message(self, message):
        data = {
            'username': self.username,
            'message': message,
        }
        self.chat_socket.send_json(data)

    def receive_reply(self):
        self.chat_socket.recv()

    def check_message(self):
        events = dict(self.poller.poll(3000))
        return events.get(self.chat_socket) == zmq.POLLIN

    def client_constant_loop(self):
        self.connect_to_server()
        self.register_poller()

        while True:
            message = self.receive_input()
            self.send_message(message)
            if self.check_message():
                self.receive_reply()
            else:
                self.reconnect_to_server()

    def run(self):
        thread = threading.Thread(target=self.client_constant_loop)
        thread.start()