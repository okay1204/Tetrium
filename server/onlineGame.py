

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


    def update(self, data, p):
        
        resting, piece, meter, meter_stage = data

        self.current_piece[p] = piece
        self.resting_blocks[p] = resting
        self.meters[p] = meter
        self.meter_stages[p] = meter_stage

    def restart(self):

        self.current_piece = [None, None]

        self.resting_blocks = [[], []]
        self.meters = [[], []]
        
    
    
    