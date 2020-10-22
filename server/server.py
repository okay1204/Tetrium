import socket
import _thread

server = "192.168.1.100"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)

s.listen(2)
print("Server Started, Waiting for connection")

def threaded_client(conn):
    
    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")
        
            if not data:
                print("Disconnected")
                break
            else:
                print("Recieved:", reply)
                print("Sending:", reply)
            
            conn.sendall(str.encode(reply))
        except:
            break
    
    print("Connection Lost")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to", addr)

    _thread.start_new_thread(threaded_client, (conn,))