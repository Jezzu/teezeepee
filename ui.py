import argparse
import configparser
import sys
import threading
import zmq


class UI(object):

    def __init__(self, server_host, server_port, ui_pipe):
        self.server_host = server_host
        self.server_port = server_port
        self.context = zmq.Context()
        self.ui_sock = None
        self.ui_pipe = ui_pipe
        self.poller = zmq.Poller()

    def connect_to_server(self):
        self.ui_sock = self.context.socket(zmq.SUB)
        self.ui_sock.setsockopt_string(zmq.SUBSCRIBE, '')

        connect_address = 'tcp://{}:{}'.format(
            self.server_host, self.server_port)

        self.ui_sock.connect(connect_address)
        self.poller.register(self.ui_sock, zmq.POLLIN)

    def refresh(self):
        data = self.ui_sock.recv_json()
        username, message = data['username'], data['message']
        self.ui_pipe.send_string('{}: {}'.format(username, message))

    def check_message(self):
        events = self.poller.poll()
        return self.ui_sock in events

    def display_constant_loop(self):
        self.connect_to_server()
        while True:
            self.refresh()

    def run(self):
        thread = threading.Thread(target=self.display_constant_loop)
        thread.start()
