import zmq

class Server(object):
	def __init__(self, chat_interface, chat_port):
		self.context = zmq.Context()

		self.chat_interface = chat_interface
		self.chat_port = chat_port
		self.chat_socket = None


	# Bind respective TCP ports to corresponding sockets
	def bind_tcp_ports(self):

		# Reply Module
		self.chat_socket = self.context.socket(zmq.REP)

		chat_socket_bind_string = 'tcp://{}:{}'.format(self.chat_interface, self.chat_port)
		self.chat_socket.bind(chat_socket_bind_string)


	# Return list based on received zmq message
	def get_message(self):
		msg = self.chat_socket.recv_json()
		username = msg['username']
		message = msg['message']

		return [username, message]

	# Constant loop to receive messages
	def constant_loop(self):
		self.bind_tcp_ports()

		while True:
			username, message = self.get_message()


