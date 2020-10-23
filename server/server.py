import socket
import _thread
from game import Game
import pickle

server = "localhost"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
    
except socket.error as e:
    print(e)

s.listen()
print("Server Started, Waiting for connections")

idCount = 0
games = {}

def threaded_client(conn, player, gameId):

    global idCount

    # send player number to client right after connecting
    conn.send(str.encode(str(player)))
    
    while True:
        try:
            data = conn.recv(2048).decode()

            if gameId in games.keys():

                game = games[gameId]

                if not data:
                    break
                else:
                    conn.sendall(pickle.dumps(game))

            else:
                break
        except Exception as e:
            print(e)
    
    print("Connection lost to player", player, "lost in game", game)
    try:
        del games[gameId]
        print("Closed game", gameId)
    except:
        pass

    idCount -= 1
    conn.close()

player = 0

while True:
    conn, addr = s.accept()
    print("Connected to", addr)

    idCount += 1
    gameId = (idCount - 1)//2

    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        player = 0
    else:
        games[gameId].ready = True
        player = 1

    _thread.start_new_thread(threaded_client, (conn, player, gameId))