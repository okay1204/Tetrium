# pylint: disable=no-member

import pygame
import pieces
from math import sin, cos, pi

class Game:

    def __init__(self):
        pygame.init()

        self.width = 500
        self.height = 800

        self.running = True

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.icon = pygame.image.load('./tetris.jpg')
        pygame.display.set_icon(self.icon)

        self.caption = "Tetris"
        pygame.display.set_caption(self.caption)

        # 30px x 30px is one block

        self.resting = []
    

    def render(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (93, 110, 105), (100, 100, 300, 600))

        for block in self.resting:
            block.render()


game = Game()


color_key = {
    'green': (13, 252, 65),
    'blue': (13, 29, 252),
    'teal': (15, 246, 250),
    'red': (250, 15, 15),
    'orange': (255, 128, 43),
    'purple': (168, 24, 245),
    'yellow': (255, 223, 13)
}


def darken(value):

    value -= 60

    if value < 0: return 0
    else: return value

class Block(Game):

    def __init__(self, x, y, color, colorByName=True):

        self.x, self.y = x, y

        if colorByName:
            self.color = color_key[color]
        else:
            self.color = color

        self.size = 30

    
    def render(self):

        darker = tuple(map(darken, self.color))
        pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
        pygame.draw.rect(game.screen, self.color, ((self.x-1) * self.size + 105, (self.y-1)* self.size + 105, 20, 20))

    def render_preview(self):
                                        # white
        pygame.draw.rect(game.screen, (255, 255, 255), ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
        pygame.draw.rect(game.screen, (93, 110, 105), ((self.x-1) * self.size + 103, (self.y-1)* self.size + 103, 24, 24))




class Piece(Game):

    def __init__(self, x, y, piece):

        self.x, self.y = x, y

        self.piece_type = piece

        self.blocks = list(map(lambda args: Block(*args), pieces.get_piece(x, y, piece)))

    
    def move(self, x, y):

        self.x += x
        self.y += y

        for block in self.blocks:
            block.x += x
            block.y += y


    #0 means clockwise, 1 means counterclockwise
    def rotate(self, direct: int):

        if self.piece_type == "O": return

        if direct == 0:
            #clockwise
            for block in self.blocks:
                #Math formula
                temp_x, temp_y = block.x, block.y
                block.x = (-1*(temp_y-self.y) + self.x)
                block.y = ((temp_x - self.x) + self.y)

        else:
            #counter-clockwise
            for block in self.blocks:
                #Math formula
                temp_x, temp_y = block.x, block.y
                block.x = (temp_y - self.y + self.x)
                block.y = (-1*(temp_x - self.x) + self.y)

        
    def check_floor(self):

        for block in self.blocks:

            # if hits floor
            if block.y > 20:
                return True

            # if hits another block
            for resting_block in game.resting:
                if resting_block.x == block.x and resting_block.y == block.y:
                    return True
        
        return False


    def check_right(self):

        for block in self.blocks:
            
            # if hits wall
            if block.x > 9:
                return True

            # if hits another block
            for resting_block in game.resting:
                if resting_block.x == block.x+1 and resting_block.y == block.y:
                    return True
        
        return False


    def check_left(self):

        for block in self.blocks:
            
            # if hits wall
            if block.x <= 1:
                return True

            # if hits another block
            for resting_block in game.resting:
                if resting_block.x == block.x-1 and resting_block.y == block.y:
                    return True
        
        return False
        
    
    def render(self):
        # to render preview
        self.x, self.y
        
        downCount = 0
        while not self.check_floor():
            self.move(0, 1)
            downCount += 1
        self.move(0, -1)

        for block in self.blocks:
            block.render_preview()
        
        for x in range(downCount): # noqa pylint: disable=unused-variable
            self.move(0, -1)

        self.move(0, 1)
        


        # for actual piece
        for block in self.blocks:
            block.render()




if __name__ == "__main__":
    import main