import zmq

class Server(object):
	def __init__(self, chat_interface, chat_port):
        self.chat_interface = chat_interface
        self.chat_port = chat_port
        self.context = zmq.Context()
        self.chat_socket = None

    def bind_tcp_ports(self):
    	# Reply Module
        self.chat_socket = self.context.socket(zmq.REP)

        chat_socket_bind_string = 'tcp://{}:{}'.format(
            self.chat_interface, self.chat_port)
        self.chat_socket.bind(chat_socket_bind_string)