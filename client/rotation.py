
    #0 means clockwise, 1 means counterclockwise
    def rotate(self, direct: int):

        if self.piece_type == "O": return

        if direct == 0:
            #clockwise
            
            for block in self.blocks:
                temp_x, temp_y = block.x, block.y
                block.x = (-1*(temp_y-self.y) + self.x)
                block.y = ((temp_x - self.x) + self.y)

        else:
            #counter-clockwise

            for block in self.blocks:
                temp_x, temp_y = block.x, block.y
                block.x = (temp_y - self.y + self.x)
                block.y = (-1*(temp_x - self.x) + self.y)
