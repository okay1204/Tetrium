import time
import random

pieces = ["T", "L", "J", "S", "Z", "I", "O"]

def opp_player(number):
    if not number:
        return 1
    else:
        return 0

class OnlineGame:

    def __init__(self, gameId):

        self.id = gameId
        self.player = 0
        self.ready = False
        self.started = False


        self.round = 0

        # Player names
        self.names = [None, None]

        # Falling current piece of both players
        self.current_piece = [None, None]

        # All resting blocks of both players
        self.resting_blocks = [[], []]

        self.winner = None

        self.countdown = 0

        # Both players junk meter
        self.meters = [[], []]
        self.meter_stages = [1, 1]


        self.rematch = [False, False]

        self.starting_bag = pieces.copy()
        random.shuffle(self.starting_bag)


        self.specials = [[], []]

    
    def speed_level(self):
        return self.level
    
    
    def opp_piece_blocks(self, p):
        return self.current_piece[opp_player(p)]

    def opp_resting(self, p):
        return self.resting_blocks[opp_player(p)]

    def opp_meter(self, p):
        return self.meters[opp_player(p)]

    def opp_meter_stage(self, p):
        return self.meter_stages[opp_player(p)]

    def opp_name(self, p):
        return self.names[opp_player(p)]
    
    def opp_has_rematched(self, p):
        return self.rematch[opp_player(p)]


    def _update(self, data, p):
        
        resting, piece, meter, meter_stage = data

        self.current_piece[p] = piece
        self.resting_blocks[p] = resting
        self.meters[p] = meter
        self.meter_stages[p] = meter_stage


        self.level = min(int(((time.time() - self.time_started) // 30) + 1), 15)

    def _send_lines(self, amount, sender):

        self.specials[opp_player(sender)].append(f"junk {amount}")

    def _send_chat(self, p, message):

        self.specials[opp_player(p)].append(message)


    def _increase_meter(self, player):

        self.meter_stages[player] += 1

    def _end_game(self, loser):

        if loser: self.winner = 0
        else: self.winner = 1

    def _reset(self):
        self.rematch = [False, False]
        self.winner = None
        self.countdown = time.time() + 6
        self.time_started = time.time() + 5
        self.round += 1
        self.meters = [[], []]
        self.meter_stages = [1, 1]
        random.shuffle(self.starting_bag)
    
    
    