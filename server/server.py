import socket
import _thread
from onlineGame import OnlineGame
import pickle
import traceback


server = "localhost"
port = 6969


idCount = 0
games = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((server, port))

blocksize = 16
sentinel = b'\x00\x00END_MESSAGE!\x00\x00'

def threaded_client(conn, player, gameId):

    global idCount

    # send player number to client right after connecting
    conn.send(str.encode(str(player)))

    
    while True:
        try:

            # procedure of recieving multiplepackets to combine into a singular data            
            blocks = []
            while True:
                blocks.append(conn.recv(16))

                if sentinel in b''.join(blocks):
                    break
            
            data = b''.join(blocks)
            data = data.replace(sentinel, b'')
            data = pickle.loads(data)


            if gameId in games.keys():

                game = games[gameId]

                if not data:
                    break
                
                else:
                    # data will be in order of
                    # resting, piece, meter, meter stage

                    if isinstance(data, list):
                        specials = data.pop(2)
                
                        game._update(data, player)

                        for special in specials:

                            # sending junk
                            if special.startswith("junk"):

                                game._send_lines(int(special.split()[1]), player)

                            # clearing own junk
                            elif special.startswith("clear"):

                                game._clear_junk(int(special.split()[1]), player)

                            # increases meter stage
                            elif special == "meter increase":

                                game._increase_meter(player)

                            # resets meter
                            elif special == "meter reset":

                                game._reset_meter(player)

                    elif data.startswith('name '):
                        game.names[player] = data[5:]

                    # dumps data
                    sending = pickle.dumps(game)
                    for n in range(len(sending)//blocksize+1):
                        # sends portion of bytes
                        conn.send(sending[n*blocksize:(n+1)*blocksize])
                    # means end packets
                    conn.send(sentinel)

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
