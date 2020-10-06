# pylint: disable=no-member

import pygame
import pieces as pieces_lib
from math import sin, cos, pi
import time

from pieces import preview_piece


color_key = {
    'green': (13, 252, 65),
    'blue': (13, 29, 252),
    'teal': (15, 246, 250),
    'red': (250, 15, 15),
    'orange': (255, 128, 43),
    'purple': (168, 24, 245),
    'yellow': (255, 223, 13)
}

class Game:

    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font('arial.ttf', 32)

        pygame.mixer.music.load('assets/background_audio.wav')
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)


        self.rotateSFX = pygame.mixer.Sound('assets/move_effect_success.wav')
        self.holdSFX = pygame.mixer.Sound('assets/hold_effect.wav')

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

        self.removing = []
    


        
        



    def render(self, pieces, held=None):
        
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (93, 110, 105), (100, 100, 300, 600))

        for block in self.resting:
            block.render()

        # for piece order
        for x in range(1, 4):
            pygame.draw.circle(self.screen, (93, 110, 105), (450, 130*x), 40)

        text = self.font.render('Next', True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (450, 60)
        self.screen.blit(text, textRect)

        # putting pieces in the circles
        position = 1
        for piece in pieces:
            for color, x, y, width, height in pieces_lib.preview_piece(450, position*130, piece):
                pygame.draw.rect(self.screen, color_key[color], (x, y, width, height))
            
            position += 1
    


        # for hold area
        pygame.draw.circle(self.screen, (93, 110, 105), (50, 130), 40)
        text = self.font.render('Hold', True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (50, 60)
        self.screen.blit(text, textRect)

        if held:
            for color, x, y, width, height in pieces_lib.preview_piece(50, 130, held):
                pygame.draw.rect(self.screen, color_key[color], (x, y, width, height))


    def show_text(self):

        font = pygame.font.Font('arial.ttf', 32) 

        text = font.render('Whoah', True)
        textRect = text.get_rect() 
  
        # set the center of the rectangular object. 
        textRect.center = (self.width // 2, self.height // 2) 
        
        self.screen.blit(text, textRect)


    def add_to_hold(self):
        preview_piece


game = Game()



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


        self.fade_increments = None
        self.fade_stage = 0
    
    def render(self):

        # normal
        if not self.fade_increments:
            darker = tuple(map(darken, self.color))
            pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
            pygame.draw.rect(game.screen, self.color, ((self.x-1) * self.size + 105, (self.y-1)* self.size + 105, 20, 20))

        # fading
        else:

            if self.fade_stage < 15:
                color = list(self.color)

                for index, add in enumerate(self.fade_increments):
                    color[index] = color[index] + add
                self.color = tuple(color)

                pygame.draw.rect(game.screen, self.color, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
                self.fade_stage += 1

            elif self.fade_stage >= 15:
                
                game.resting.remove(self)

                # going through each row
                for remove_row in game.removing:
        
                    # if in that row
                    if self in remove_row:
                        # check if all are ready to remove
                        for block in remove_row:
                            if block.fade_stage < 15:
                                return
                        break
                else:
                    return


                for block in game.resting:
                    if block.y < self.y:
                        block.y += 1

                for remove_row in game.removing:
                    if self in remove_row:
                        game.removing.remove(remove_row)
                        #TODO put row cleared sound effect here
                        break

                    


    def render_preview(self):
                                        # white
        pygame.draw.rect(game.screen, (255, 255, 255), ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
        pygame.draw.rect(game.screen, (93, 110, 105), ((self.x-1) * self.size + 103, (self.y-1)* self.size + 103, 24, 24))



class Piece(Game):

    def __init__(self, x, y, piece):

        self.x, self.y = x, y

        self.piece_type = piece

        self.blocks = list(map(lambda args: Block(*args), pieces_lib.get_piece(x, y, piece)))

    
    def move(self, x, y):

        self.x += x
        self.y += y

        for block in self.blocks:
            block.x += x
            block.y += y


    def _path_check(self, block_coords, x, y, maxcount):

        count = 0
        while self.check_overlap and count < maxcount:
            self.move(x, y)
            count += 1

        if not self.check_overlap: return True

        # reset
        for index, block in enumerate(self.blocks):
            block.x, block.y = block_coords[index]
            self.x, self.y = x, y

        return False

    #0 means clockwise, 1 means counterclockwise
    def rotate(self, direct: int):
       

        if self.piece_type == "O": return game.rotateSFX.play()

        block_coords = []

        x, y = self.x, self.y # noqa pylint: disable=unused-variable

        if direct == 0:
            #clockwise
            for block in self.blocks:
                #Math formula
                temp_x, temp_y = block.x, block.y
                block_coords.append((temp_x, temp_y))

                block.x = (-1*(temp_y-self.y) + self.x)
                block.y = ((temp_x - self.x) + self.y)
            

        else:
            #counter-clockwise
            
            for block in self.blocks:
                #Math formula
                temp_x, temp_y = block.x, block.y
                block_coords.append((temp_x, temp_y))
                block.x = (temp_y - self.y + self.x)
                block.y = (-1*(temp_x - self.x) + self.y)


        for block in self.blocks:

            if block.x < 1:
                self.move(1, 0)

            if block.x > 10:
                self.move(-1, 0)
            
            if block.y > 20:
                self.move(0, -1)


        if self.check_overlap():
            
            if self._path_check(block_coords, 0, -1, 3): return game.rotateSFX.play()

            # right first
            if direct == 0:

                if self._path_check(block_coords, 1, 0, 3): return game.rotateSFX.play()

                if self._path_check(block_coords, 1, -1, 1): return game.rotateSFX.play()

                if self._path_check(block_coords, -1, 0, 3): return game.rotateSFX.play()

                if self._path_check(block_coords, -1, -1, 1): return game.rotateSFX.play()

            # left first
            else:

                if self._path_check(block_coords, -1, 0, 3): return game.rotateSFX.play()

                if self._path_check(block_coords, -1, -1, 1): return game.rotateSFX.play()

                if self._path_check(block_coords, 1, 0, 3): return game.rotateSFX.play()
            
                if self._path_check(block_coords, 1, 1, 1): return game.rotateSFX.play()
        
            #TODO reject sound effect here

        else:
            game.rotateSFX.play()
            

        """
        First move piece in bounds if it is out of bounds.
        If there is any overlapping conflict, then do the following:

        Check if the piece is ok if it moves two blocks up, if not,
        Check if it can move right by two blocks if clockwise, or left if counterclockwise,
        if not,
        check the other direction.
        
        If all of these fail, then the rotation will not occur.
        """

    

    def check_overlap(self):

        for block in self.blocks:
            for resting in game.resting:

                if (block.x == resting.x and block.y == resting.y) or (block.y > 20 or block.x < 1 or block.x > 10):
                    return True
        
        return False

            
        
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
            if block.x < 2:
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