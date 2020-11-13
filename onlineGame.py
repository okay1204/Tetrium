import time

class OnlineGame:

    def __init__(self, game_id):

        self.ready = False

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

        self._id = game_id

        self.rematch = [False, False]

    
    def speed_level(self):
        level = int(((time.time() - self.time_started) // 30) + 1)
        if level > 15: level = 15
        return level
    
    
    def opp_piece_blocks(self, p):
        if not p:
            return self.current_piece[1]
        else:
            return self.current_piece[0]

    def opp_resting(self, p):

        if not p:
            return self.resting_blocks[1]
        else:
            return self.resting_blocks[0]

    def opp_meter(self, p):
        if not p:
            return self.meters[1]
        else:
            return self.meters[0]

    def opp_meter_stage(self, p):
        if not p:
            return self.meter_stages[1]
        else:
            return self.meter_stages[0]

    
    def own_meter(self, p):
        return self.meters[p]

    def own_meter_stage(self, p):
        return self.meter_stages[p]

    def opp_name(self, p):

        if not p:
            return self.names[1]
        else:
            return self.names[0]
    
    def opp_has_rematched(self, p):

        if not p:
            return self.rematch[1]
        else:
            return self.rematch[0]


    def _update(self, data, p):
        
        resting, piece = data

        self.current_piece[p] = piece
        self.resting_blocks[p] = resting

    def _send_lines(self, amount, sender):

        # adding lines to opponent
        if not sender:
            reciever = 1
        else:
            reciever = 0
        
        self.meters[reciever].append(amount)

    def _clear_junk(self, amount, p):

        # clearing lines from sender
        meter = self.meters[p]

        while meter and amount > 0:
            meter[0] -= 1
            amount -= 1

            if meter[0] <= 0:
                meter.pop(0)
                self.meter_stages[p] = 1


    def _increase_meter(self, player):

        self.meter_stages[player] += 1

    def _reset_meter(self, player):

        self.meter_stages[player] = 1
        self.meters[player].pop(0)

    def _end_game(self, loser):

        if loser: self.winner = 0
        else: self.winner = 1

    def _reset(self):
        self.rematch = [False, False]
        self.winner = None
        self.countdown = time.time() + 5
        self.time_started = time.time()
        self.round += 1
        self.meters = [[], []]
        self.meter_stages = [1, 1]
    
    
    