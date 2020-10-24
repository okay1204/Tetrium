import socket
import _thread
from onlineGame import OnlineGame
import pickle
import traceback


server = "localhost"
port = 5555


idCount = 0
games = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((server, port))

def threaded_client(conn, player, gameId):

    global idCount

    # send player number to client right after connecting
    conn.send(str.encode(str(player)))
    
    while True:
        try:

            try:
                data = pickle.loads(conn.recv(4026))
            except:
                break

            if gameId in games.keys():

                game = games[gameId]

                if not data:
                    break
                
                else:
                    # data will be in order of
                    # resting, piece, meter, meter stage
                    if isinstance(data, tuple):
                        game._update(data, player)

                    elif data.startswith("junk"):

                        game._send_lines(data.split()[1], player)

                    elif data == "meter increase":

                        game._increase_meter(player)

                    conn.sendall(pickle.dumps(game))

            else:
                break
        except Exception:
            traceback.print_exc()
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
s.listen()
print("Server Started, Waiting for connections")

while True:
        
    conn, addr = s.accept()
    
    print("Connected to", addr)
    idCount += 1
    gameId = (idCount - 1)//2

    if idCount % 2 == 1:
        games[gameId] = OnlineGame(gameId)
        player = 0
    else:
        games[gameId].ready = True
        player = 1
        print("Started game", gameId)

    _thread.start_new_thread(threaded_client, (conn, player, gameId))
