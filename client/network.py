import socket
import pickle
import traceback
from ip import IP

version = "0.1"

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = IP
        self.port = 6969
        self.addr = (self.server, self.port)
        self.p = self.connect()

        self.blocksize = 16
        # marks the end of packet sending
        self.sentinel = b'\x00\x00END_MESSAGE!\x00\x00'

    def connect(self):
        try:
            self.client.connect(self.addr)

            # send version number after connecting
            self.client.send(str.encode(version))

            response = self.client.recv(4096).decode()

            if response.isdigit():
                response = int(response)

            # self.client.settimeout(2.0)
            return response

            
        except:
            return "no connection"

    def disconnect(self):
        # dumps data
        data = pickle.dumps('disconnect')
        for n in range(len(data)//self.blocksize+1):
            # sends portion of bytes
            self.client.send(data[n*self.blocksize:(n+1)*self.blocksize])
        # means end packets
        self.client.send(self.sentinel)



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
                    break
            
            recieved = b''.join(blocks)
            recieved.replace(self.sentinel, b'')
            recieved = pickle.loads(recieved)

            return recieved
        except socket.error as e:
            raise e


if __name__ == "__main__":
    import main