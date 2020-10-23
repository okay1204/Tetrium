import socket
import pickle
import struct


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(4096)
        except:
            pass

    def send(self, data):
        try:
            # packet = pickle.dumps(data)
            # length = struct.pack('!I', len(packet))
            # packet = length + packet

            # self.client.send(packet)

            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))
        except socket.error as e:
            print(e)

