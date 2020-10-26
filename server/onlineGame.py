

class OnlineGame:

    def __init__(self, game_id):

        self.ready = False

        # Falling current piece of both players
        self.current_piece = [None, None]

        # All resting blocks of both players
        self.resting_blocks = [[], []]

        # Both players junk meter
        self.meters = [[], []]
        self.meter_stages = [1, 1]

        self._id = game_id
    
    
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


    def _update(self, data, p):
        
        resting, piece = data

        self.current_piece[p] = piece
        self.resting_blocks[p] = resting

    def _send_lines(self, amount, sender):

        # clearing lines from sender
        temp = amount

        meter = self.meters[sender]

        while meter and temp > 0:
            meter[0] -= 1
            temp -= 1

            if meter[0] <= 0:
                meter.pop(0)
                self.meter_stages[sender] = 1


        # adding lines to opponent
        if not sender:
            reciever = 1
        else:
            reciever = 0
        
        self.meters[reciever].append(amount)

    def _increase_meter(self, player):

        self.meter_stages[player] += 1

    def _reset_meter(self, player):

        self.meter_stages[player] = 1
        self.meters[player].pop(0)

    def _restart(self):

        self.current_piece = [None, None]

        self.resting_blocks = [[], []]
        self.meters = [[], []]
        
    
    
    