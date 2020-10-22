class Game:

    def __init__(self, game_id):

        self.ready = False

        # Falling current piece of both players
        self.current_piece = [None, None]

        # All resting blocks of both players
        self.resting_blocks = [[], []]

        # Both players junk meter
        self.meters = [[], []]

        self._id = game_id
    
    
    def opp_piece(self, p):
        if not p:
            return self.current_piece[1]
        else:
            return self.current_piece[0]

    def opp_resting(self, p):
        if not p:
            return self.resting_blocks[1]
        else:
            return self.resting_blocks[0]

    def opp_meters(self, p):
        if not p:
            return self.meters[1]
        else:
            return self.meters[0]

    
    
    
    