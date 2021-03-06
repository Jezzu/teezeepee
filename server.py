import zmq

import argparse
import configparser

class Server(object):
	def __init__(self, chat_interface, chat_port, show_interface, show_port):
		self.context = zmq.Context()

		self.chat_interface = chat_interface
		self.chat_port = chat_port
		self.show_interface = show_interface
		self.show_port = show_port

		self.chat_socket = None
		self.show_socket = None


	# Bind respective TCP ports to corresponding sockets
	def bind_tcp_ports(self):

		# Reply Module
		self.chat_socket = self.context.socket(zmq.REP)

		chat_socket_bind_string = 'tcp://{}:{}'.format(self.chat_interface, self.chat_port)
		self.chat_socket.bind(chat_socket_bind_string)

		self.show_socket = self.context.socket(zmq.PUB)
		show_bind_string = 'tcp://{}:{}'.format(self.show_interface, self.show_port)
		self.show_socket.bind(show_bind_string)


	# Return list based on received zmq message
	def get_message(self):
		msg = self.chat_socket.recv_json()
		username = msg['username']
		message = msg['message']

		return [username, message]

	# Refresh screen
	def refresh(self, username, message):
		data = {
			'username' : username,
			'message' : message,
        }

		self.chat_socket.send(b'\x00')
		self.show_socket.send_json(data)

	# Constant loop to receive messages
	def forever_loop(self):
		self.bind_tcp_ports()

		while True:
			username, message = self.get_message()
			self.refresh(username, message)

# Function to parse argument in the command line
def parse_args():
    parser = argparse.ArgumentParser(description='Server for teezeepee')

    parser.add_argument('--config-file',
                        type=str,
                        help='Default path for configuration file.')

    return parser.parse_args()


if '__main__' == __name__:
    try:
        args = parse_args()
        config_file = args.config_file if args.config_file is not None else 'tzp.cfg'

        config = configparser.ConfigParser()
        config.read(config_file)
        config = config['default']

        server = Server('*', config['chat_port'], '*', config['display_port'])
        server.forever_loop()

    except KeyboardInterrupt:
        pass


