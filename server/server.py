import socket
import _thread
from game import Game
import pickle
import struct

server = "localhost"
port = 5555


idCount = 0
games = {}

def threaded_client(conn, player, gameId):

    global idCount

    # send player number to client right after connecting
    conn.send(str.encode(str(player)))
    
    while True:
        try:
            buf = b''
            while len(buf) < 4:
                buf += conn.recv(4 - len(buf))

            length = struct.unpack("!I", buf)[0]

            if gameId in games.keys():

                game = games[gameId]

                if not data:
                    break
                else:
                    # data will be in order of
                    # resting, piece, meter, meter stage
                    if isinstance(data, tuple):
                        game.update(data, player)

                    conn.sendall(pickle.dumps(game))

            else:
                break

        except Exception as e:
            print(e)
            break
    
    print("Connection lost to player", player, "lost in game", gameId)
    try:
        del games[gameId]
        print("Closed game", gameId)
    except:
        pass

    idCount -= 1
    conn.close()

player = 0

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server, port))
        s.listen()
        print("Server Started, Waiting for connections")
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
            print("Started game", gameId)

        _thread.start_new_thread(threaded_client, (conn, player, gameId))
