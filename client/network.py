import socket
import pickle
import struct
import traceback


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = int(self.connect())

        self.blocksize = 16
        # marks the end of packet sending
        self.sentinel = b'\x00\x00END_MESSAGE!\x00\x00'[:self.blocksize]

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(4096)
        except:
            pass

    def send(self, data):
        try:
            
            # dumps data
            data = pickle.dumps(data)
            for n in range(len(data)//self.blocksize+1):
                # sends portion of bytes
                self.client.send(data[n*self.blocksize:(n+1)*self.blocksize])
            # means end packets
            self.client.send(self.sentinel)




            # procedure of recieving multiplepackets to combine into a singular data            
            blocks = []
            while True:
                blocks.append(self.client.recv(16))
                if self.sentinel in b''.join(blocks):
                    blocks.pop()
                    break
            
            recieved = b''.join(blocks)
            recieved = pickle.loads(recieved)

            return recieved
        except socket.error as e:
            print(e)