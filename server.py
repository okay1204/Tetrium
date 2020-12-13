import socket
import _thread
from onlineGame import OnlineGame #type: ignore
import pickle
import traceback
from ip import IP


server = IP
port = 6969

timeout = 10.0

games = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((server, port))

blocksize = 16
sentinel = b'\x00\x00END_MESSAGE!\x00\x00'

def threaded_client(conn, player, game):

    # send player number to client right after connecting
    conn.send(str.encode(str(player)))

    name = None

    while True:

        gameId = game.id

        try:

            # procedure of recieving multiplepackets to combine into a singular data            
            try:
                blocks = []
                while True:
                    blocks.append(conn.recv(16))

                    if sentinel in b''.join(blocks):
                        break
                
                data = b''.join(blocks)
                data = data.replace(sentinel, b'')
                data = pickle.loads(data)
            except socket.timeout:
                print(f"Player {player} ({name}) in game {gameId} disconnected from timeout")
                break
            except:
                print(f"Player {player} ({name}) in game {gameId} forcefully disconnected")
                break

            if data == "disconnect":
                print(f"Player {player} ({name}) in game {gameId} safely disconnected")
                break


            if game.ready or not game.started:

                if not data:
                    break
                
                else:

                    if game.winner != None:
                        conn.settimeout(None)

                    elif game.ready and conn.gettimeout() != timeout:
                        conn.settimeout(timeout)



                    # data will be in order of
                    # resting, piece, meter, meter stage

                    if isinstance(data, list):
                        specials = data.pop(-1)
                
                        game._update(data, player)


                        for special in specials:

                            # sending junk
                            if special.startswith("junk"):

                                game._send_lines(int(special.split()[1]), player)

                            elif special == "game over":

                                game._end_game(player)

                                if player: opp = 0
                                else: opp = 1

                                conn.settimeout(None)

                                print(f'Player {opp} ({game.names[opp]}) beat Player {player} ({game.names[player]}) in game {gameId}')
                            
                            elif special == "rematch":
                                
                                game.rematch[player] = True

                                if all(game.rematch):
                                    game._reset()

                            elif special.startswith("chat"):
                                
                                game._send_chat(player, special)

                    elif data.startswith('name '):
                        game.names[player] = data[5:]
                        name = data[5:]
                        print(f"Player {player} in game {gameId} is called {name}")


                    sent_specials = game.specials[player].copy()

                    try:
                        # dumps data
                        sending = pickle.dumps(game)
                        for n in range(len(sending)//blocksize+1):
                            # sends portion of bytes
                            conn.send(sending[n*blocksize:(n+1)*blocksize])
                        # means end packets
                        conn.send(sentinel)
                    except:
                        print(f"Player {player} ({name}) in game {gameId} forcefully disconnected")
                        break

                    for special in sent_specials:
                        game.specials[player].remove(special)


            else: # game doesn't exist
                print(f"Player {player} ({name}) in game {gameId} disconnected safely from game closing")

                # dumps data
                sending = pickle.dumps('disconnect')
                for n in range(len(sending)//blocksize+1):
                    # sends portion of bytes
                    conn.send(sending[n*blocksize:(n+1)*blocksize])
                # means end packets
                conn.send(sentinel)
                break

        except Exception:
            traceback.print_exc()
            break
    
    if game.ready:
        game.ready = False
    else:
        games.remove(game)

        for index in range(len(games)):
            game.id = index

    conn.close()


s.listen()
print("Server Started, Waiting for connections")

version = "1.2"
# NOTE replace with download link to newer version
download_link = "https://tetrium.me/download"

while True:
        
    conn, addr = s.accept()

    # make sure client is running correct version first
    try:
        client_version = conn.recv(4096).decode()
        if version != client_version:
            print(f"{addr[0]} was disconnected because they were running version {client_version}")
            conn.send(str.encode(f"outdated version {version} {download_link}"))
            continue
    except:
        continue

    # if there is not a game with one player waiting
    if not games or games[-1].player:
        games.append(OnlineGame( len(games) ))
        player = 0

    else:
        games[-1].player = player = 1
        games[-1]._reset()
        games[-1].ready = True
        games[-1].started = True


    gameId = len(games) -1
    
    print(addr[0], "connected to game", gameId, "as player", player)

    _thread.start_new_thread(threaded_client, (conn, player, games[-1]))
