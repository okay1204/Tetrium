# pylint: disable=no-member

import pygame
import pieces as pieces_lib
from math import sin, cos, pi
import time
import sys
from random import shuffle, randint

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
        self.font = pygame.font.Font('assets/arial.ttf', 32)

        pygame.mixer.music.load('assets/background_audio.wav')
        #NOTE set volume to 0.15 in final version
        pygame.mixer.music.set_volume(0.15)
        pygame.mixer.music.play(-1)


        self.correct_rotateSFX = pygame.mixer.Sound('assets/move_effect_success.wav')
        self.holdSFX = pygame.mixer.Sound('assets/hold_effect.wav')
        # self.row_clearedSFX = pygame.mixer.Sound()
        # self.wrong_rotateSFX = pygame.mixer.Sound()

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
    

        self.continuous = True
        
        



    def render(self, pieces = None, held=None):
        
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
        if pieces:
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


        # for continuous movement indication
        if game.continuous: text = "On"
        else: text = "Off"

        text = self.font.render(f"Continuous Movement: {text}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (300, 780)
        self.screen.blit(text, textRect)


    def show_text(self):

        font = pygame.font.Font('arial.ttf', 32) 

        text = font.render('Whoah', True)
        textRect = text.get_rect() 
  
        # set the center of the rectangular object. 
        textRect.center = (self.width // 2, self.height // 2) 
        
        self.screen.blit(text, textRect)


    def add_to_hold(self):
        preview_piece


    def game_over(self):

        global bag, next_bag, rotations, speedLevel, current

        gameOver = True

        pygame.mixer.music.set_volume(0.03)
        
        while gameOver:
            #Game over loop

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_d:
                        gameOver = False
                        game.resting.clear()
                        game.removing.clear()
                        speedLevel = 0
                        bag = pieces.copy()
                        random.shuffle(bag)
                        next_bag = pieces.copy()
                        random.shuffle(next_bag)
                        rotations = 0
                        current = Piece(5, 1, bag.pop(0))
                        pygame.mixer.music.set_volume(0.15)


                

            s = pygame.Surface((game.width, game.height), pygame.SRCALPHA) # noqa pylint: disable=too-many-function-args
            s.fill((255,255,255, 2))      
            game.screen.blit(s, (0,0))
            game_over_font = pygame.font.Font('assets/arial.ttf', 60)
            text = game_over_font.render(f'Game Over', True, (0, 0 ,0), game.screen)
            textRect = text.get_rect() 
            textRect.center = (game.width // 2, game.height // 2) 
            game.screen.blit(text, textRect)
            pygame.display.update()

            game.clock.tick(60)
        
    
    def start_screen(self):
        
        bkg_img = pygame.image.load('assets/bkg_img.png')
        game_started = False

        pygame.mixer.music.set_volume(0.03)
        
        #It might seem confusing whats happeneing here but dw about it, just making sure blocks are spaced out
        x_pos = [0, 4, 8, 12, 0, 4, 8]
        shuffle(x_pos)

        pieces = [

            Piece(x_pos[0], randint(-9, -6), 'T'), 
            Piece(x_pos[1], randint(-6, -3), 'L'), 
            Piece(x_pos[2], randint(-3, 0), 'BL'), 
            Piece(x_pos[3], randint(0, 3), 'S'), 
            Piece(x_pos[4], randint(3, 6), 'BS'), 
            Piece(x_pos[5], randint(6, 9), 'I'),
            Piece(x_pos[6], randint(9, 15), 'O')
        ]
        
        
        last_falls = [time.time() for i in pieces]
        while not game_started:
            #Game over loop

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_s:
                        game_started = True
                        
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # noqa pylint: disable=too-many-function-args
            s.fill((255,255,255, 2))      
            self.screen.blit(s, (0,0))   
    

            for i, piece in enumerate(pieces):
                #means piece is off the screen
                if piece.y >= 28:
                    #Moves it back up
                    piece.move(0, randint(-35, -30))

                piece.render(False)
                if time.time() > last_falls[i]:
                    piece.move(0, 1)
                    last_falls[i] = time.time() + 0.75
                   

            pygame.display.update()

            game.clock.tick(60)




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
                        # game.row_clearedSFX.play()
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


    def _path_check(self, orgx, orgy, block_coords, x, y, maxcount):

        count = 0
        while self.check_overlap() and count < maxcount:
            self.move(x, y)
            count += 1

        if not self.check_overlap():
            game.correct_rotateSFX.play()
            return True

        # reset
        for index, block in enumerate(self.blocks):
            block.x, block.y = block_coords[index]
        self.x, self.y = orgx, orgy

        return False

    #0 means clockwise, 1 means counterclockwise
    def rotate(self, direct: int):
       

        if self.piece_type == "O": return game.correct_rotateSFX.play()

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
            
            if self._path_check(x, y, block_coords, 0, -1, 3): return

            # right first
            if direct == 0:

                if self._path_check(x, y, block_coords, 1, 0, 3): return

                if self._path_check(x, y, block_coords, 1, -1, 1): return

                if self._path_check(x, y, block_coords, -1, 0, 3): return

                if self._path_check(x, y, block_coords, -1, -1, 1): return

            # left first
            else:

                if self._path_check(x, y, block_coords, -1, 0, 3): return

                if self._path_check(x, y, block_coords, -1, -1, 1): return

                if self._path_check(x, y, block_coords, 1, 0, 3): return
            
                if self._path_check(x, y, block_coords, 1, 1, 1): return
        
            #TODO put reject rotation here

        else:
            game.correct_rotateSFX.play()
            
            
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

    def overlapping_blocks(self):

        for block in self.blocks:
            for resting in game.resting:
                if (block.x == resting.x and block.y == resting.y):
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
        
    
    def render(self, preview = True):
        # to render preview
        self.x, self.y
        
        if preview:
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