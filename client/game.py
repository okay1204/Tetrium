# pylint: disable=no-member

import pygame
import pieces as pieces_lib
import math
import time
import sys
from random import shuffle, randint
from network import Network

from pieces import preview_piece


color_key = {
    'green': (13, 252, 65),
    'blue': (13, 29, 252),
    'teal': (15, 246, 250),
    'red': (250, 15, 15),
    'orange': (255, 128, 43),
    'purple': (168, 24, 245),
    'yellow': (255, 223, 13),
    'gray': (107, 115, 120)
}


def darken(value):

    value -= 60

    if value < 0: return 0
    else: return value

class Game:

    def __init__(self):

        self.volume = 0.05
        self.lowered_volume = 0.025

        pygame.init()
        self.font = pygame.font.Font('assets/arial.ttf', 32)

        pygame.mixer.music.load('assets/background_audio.wav')
        #NOTE set volume to 0.15 in final version
        pygame.mixer.music.set_volume(self.lowered_volume)
        pygame.mixer.music.play(-1)


        self.correct_rotateSFX = pygame.mixer.Sound('assets/move_effect_success.wav')
        self.holdSFX = pygame.mixer.Sound('assets/hold_effect.wav')
        self.row_clearedSFX = pygame.mixer.Sound('assets/row_cleared.wav')
        self.row_clearedSFX.set_volume(0.5)
        # self.wrong_rotateSFX = pygame.mixer.Sound()

        self.width = 750
        self.height = 800

        self.running = True
        self.muted = False

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.icon = pygame.image.load('./tetris.jpg')
        pygame.display.set_icon(self.icon)

        self.caption = "Tetrium"
        pygame.display.set_caption(self.caption)

        # 30px x 30px is one block

        self.resting = []

        self.removing = []
    

        self.continuous = True


        self.level = 1
        self.score = 0
        self.lines = 0


        self.time_started = 0


        # list of numbers, with numbers being attack amounts
        self.meter = []
        self.meter_stage = 1


        self.opp_resting = self.opp_meter = self.opp_meter_stage = self.opp_piece_blocks = None
        
        


    def render(self, pieces=None, held=None):
        
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

        self.score = int(self.score)
        text = self.font.render(f"Score: {self.score}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (250, 725)
        self.screen.blit(text, textRect)

        font = pygame.font.Font('assets/arial.ttf', 25)

        text = font.render(f"Level: {self.level}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (420, 725)
        self.screen.blit(text, textRect)

        text = font.render(f"Lines: {self.lines}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (75, 725)
        self.screen.blit(text, textRect)

        font = pygame.font.Font('assets/arial.ttf', 20)

        time_elapsed = math.floor(time.time() - self.time_started)

        minutes = time_elapsed // 60
        remaining_seconds = time_elapsed % 60

        time_elapsed = f"{minutes}m {remaining_seconds}s"

        text = font.render(f"Time Elapsed: {time_elapsed}", True, (255, 255 ,255))
        textRect = text.get_rect()
        textRect.center = (250, 50)
        self.screen.blit(text, textRect)


        # junk line meter
        pygame.draw.rect(self.screen, (255, 255, 255), (32, 394, 36, 306))
        pygame.draw.rect(self.screen, (93, 110, 105), (35, 397, 30, 300))

        meter_block = 0
        for index, amount in enumerate(self.meter):


            if not index:
                if self.meter_stage == 1:
                    color = color_key["yellow"]
                elif self.meter_stage  == 2:
                    color = color_key["orange"]
                elif self.meter_stage  == 3:
                    color = color_key["red"]
            else:
                color = color_key["gray"]

            darkened = (tuple(darken(color) for color in color))

            for block in range(amount):

                if meter_block >= 10:
                    break
                pygame.draw.rect(self.screen, darkened, (35, 667 - (30 * meter_block), 30, 30))
                pygame.draw.rect(self.screen, color, (40, 672 - (30 * meter_block), 20, 20))
                meter_block += 1

        
        self.render_second_screen()


    def render_second_screen(self):
        pygame.draw.rect(self.screen, (93, 110, 105), (570, 250, 150, 300))

        if self.time_started + 1 > time.time():
            return
        
        for x, y, color in self.opp_resting:
            Block(x, y, color, colorByName=False).render_second()

        
        for x, y, color in self.opp_piece_blocks:
            Block(x, y, color, colorByName=False).render_second()
        
        # junk line meter
        pygame.draw.rect(self.screen, (255, 255, 255), (539, 398, 17, 152))
        pygame.draw.rect(self.screen, (93, 110, 105), (540, 399, 15, 150))


        meter_block = 0
        for index, amount in enumerate(self.opp_meter):


            if not index:
                if self.opp_meter_stage == 1:
                    color = color_key["yellow"]
                elif self.opp_meter_stage  == 2:
                    color = color_key["orange"]
                elif self.opp_meter_stage  == 3:
                    color = color_key["red"]
            else:
                color = color_key["gray"]

            darkened = (tuple(darken(color) for color in color))

            for block in range(amount):

                if meter_block >= 10:
                    break
                pygame.draw.rect(self.screen, darkened, (540, 534 - (15 * meter_block), 15, 15))
                pygame.draw.rect(self.screen, color, (542, 536 - (15 * meter_block), 11, 11))
                meter_block += 1




    def start_screen(self):

        connected = False

        def draw_start_button():
            nonlocal start_button_text_color, connected

            if not connected:
                #if mouse hovering make it lighter
                if start_button_pos[0] <= mouse[0] <= start_button_pos[0] + start_button_dimensions[0] and start_button_pos[1] <= mouse[1] <= start_button_pos[1] + start_button_dimensions[1]: 
                    pygame.draw.rect(self.screen, (255,255,255), (start_button_pos, start_button_dimensions)) 
                    start_button_text_color = (0, 0, 0)
                
                else: 
                    pygame.draw.rect(self.screen, (0,0,0), (start_button_pos, start_button_dimensions))
                    start_button_text_color = (255, 255, 255)


        def draw_text():

            nonlocal connected

            if not connected:
                start_button_text = self.font.render('START', True, start_button_text_color)
                start_button_coords = (start_button_pos[0] + 20, start_button_pos[1] + 3)
            else:
                start_button_text = self.font.render('Waiting for opponent...', True, start_button_text_color)
                start_button_coords = (start_button_pos[0] - 80, start_button_pos[1])

            title_text = title_font.render('TETRIUM', True, start_button_text_color) 
            self.screen.blit(start_button_text, start_button_coords)
            self.screen.blit(title_text, (self.width/2 - 150, self.height/2 - 200)) 


        def draw_mute_button_background():
            pygame.draw.circle(self.screen, (255,255,255), mute_button_pos,  mute_button_radius)
           

        def check_mute_and_draw_icons():
            draw_mute_button_background()
            if self.muted:
                self.lowered_volume, self.volume = 0, 0
                self.screen.blit(volume_off_icon, volume_icon_pos)
            
            else:
                self.lowered_volume, self.volume = 0.03, 0.1
                self.screen.blit(volume_on_icon, volume_icon_pos)

            

        game_started = False
        
        #It might seem confusing whats happeneing here but dw about it, just making sure blocks are spaced out
        x_pos = [0, 4, 8, 12, 0, 4, 8]
        shuffle(x_pos)

        pieces = [

            Piece(x_pos[0], randint(-9, -6), 'T'), 
            Piece(x_pos[1], randint(-6, -3), 'L'), 
            Piece(x_pos[2], randint(-3, 0), 'J'), 
            Piece(x_pos[3], randint(0, 3), 'S'), 
            Piece(x_pos[4], randint(3, 6), 'Z'), 
            Piece(x_pos[5], randint(6, 9), 'I'),
            Piece(x_pos[6], randint(9, 15), 'O')
        ]
        

        last_falls = [time.time() for _ in pieces]
        start_button_dimensions = (140 ,40)
        start_button_pos = (self.width/2 - 70, self.height/2)
        start_button_text_color = (255, 255, 255)
        mute_button_pos = (int(self.width/2), int(self.height/2 + 100))
        mute_button_radius = 35
        volume_on_icon = pygame.image.load('assets/volume-high.png')
        volume_off_icon = pygame.image.load('assets/volume-off.png')
        volume_icon_pos = (mute_button_pos[0] - 25, mute_button_pos[1] - 25)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # noqa pylint: disable=too-many-function-args
        title_font = pygame.font.Font('assets/arial.ttf', 75)
      

        left_controls = {
            "A":"Move Left",
            "S": "Soft Drop",
            "D": "Move Right",
            "G": "Toggle Movement",
            "M": "Mute Music"
        }

        right_controls = {
            "'/→":"Rotate Clockwise",
            "P/↑": "Hold Piece",
            ";/↓": "Hard Drop",
            "L /←": "Rotate Counter-Clockwise"
        }

        font = pygame.font.Font('assets/arial.ttf', 20)

        while not game_started:

            mouse = pygame.mouse.get_pos() 

            #Game over loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and not connected:
                   
                    if start_button_pos[0] <= mouse[0] <= start_button_pos[0] + start_button_dimensions[0] and start_button_pos[1] <= mouse[1] <= start_button_pos[1] + start_button_dimensions[1]:  
                        
                        
                        self.n = Network()
                        self.player = self.n.p
                        connected = True

                        pygame.mixer.music.set_volume(self.volume)
                        self.screen.fill((0, 0, 0))

                    elif mute_button_pos[0] - mute_button_radius <= mouse[0] <= mute_button_pos[0] + mute_button_radius and mute_button_pos[1] - mute_button_radius <= mouse[1] <=  mute_button_pos[1] + mute_button_radius: 
                        self.muted = not self.muted
                    
                        
           
            pygame.mixer.music.set_volume(self.lowered_volume)
           
            
          
            s.fill((255,255,255, 2))
            self.screen.blit(s, (0, 0))  

        
            for i, piece in enumerate(pieces):
                #means piece is off the screen
                if piece.y >= 28:
                    #Moves it back up
                    piece.move(0, randint(-35, -30))

                piece.render(False)
                if time.time() > last_falls[i]:
                    piece.move(0, 1)
                    last_falls[i] = time.time() + 0.75

            
            check_mute_and_draw_icons()

            if not connected:
                draw_start_button()
                
            draw_text()

            # for controls on left side
            for index, values in enumerate(left_controls.items()):
                key, description = values

                text = font.render(f"{key}: {description}", True, (0, 0, 0))
                textRect = text.get_rect()
                textRect.center = (100, index*-50+750)
                self.screen.blit(text, textRect)


            # for controls on right side
            for index, values in enumerate(right_controls.items()):
                key, description = values

                text = font.render(f"{key} {description}", True, (0, 0, 0))
                textRect = text.get_rect()
                textRect.center = (350, index*-50+750)
                self.screen.blit(text, (game.width- textRect.center[0] + 60, textRect[1]))



            # checking if game started
            if connected and self.n.send('get').ready:
                break

                
            pygame.display.update()

            self.clock.tick(60)

        self.time_started = time.time()
    
        



game = Game()


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


        self.flash_color = None
        self.flash_stage = 0
        self.flash_increments = None
    
    def render(self):

        # normal
        if not self.fade_increments and not self.flash_color:
    
            darker = tuple(map(darken, self.color))
            pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
            pygame.draw.rect(game.screen, self.color, ((self.x-1) * self.size + 105, (self.y-1)* self.size + 105, 20, 20))
      
        # fading
        elif self.fade_increments:

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

        # flashing
        else:

            if self.flash_stage < 7:

                # increasing brightness
                for index, additive in enumerate(self.flash_increments):
                    
                    self.flash_color[index] += additive # noqa pylint: disable=unsupported-assignment-operation

            elif self.flash_stage < 14:

                # decreasing brightness
                for index, additive in enumerate(self.flash_increments):
                    
                    self.flash_color[index] -= additive # noqa pylint: disable=unsupported-assignment-operation


            
            self.flash_stage += 1

            # drawing the rect
            darker = tuple(map(darken, self.flash_color))
            pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
            pygame.draw.rect(game.screen, tuple(self.flash_color), ((self.x-1) * self.size + 105, (self.y-1)* self.size + 105, 20, 20))
            

            if self.flash_stage >= 14:
                self.flash_stage = 0
                self.flash_color = None


    # for putting blocks on second screen
    def render_second(self):

        darker = tuple(map(darken, self.color))
        pygame.draw.rect(game.screen, darker, ((self.x-1) * self.size/2 + 570, (self.y-1)* self.size/2 + 250, 15, 15))
        pygame.draw.rect(game.screen, self.color, ((self.x-1) * self.size/2 + 572, (self.y-1)* self.size/2 + 252, 11, 11))                    


    def render_preview(self):
                                        # white
        pygame.draw.rect(game.screen, (255, 255, 255), ((self.x-1) * self.size + 100, (self.y-1)* self.size + 100, 30, 30))
        pygame.draw.rect(game.screen, (93, 110, 105), ((self.x-1) * self.size + 103, (self.y-1)* self.size + 103, 24, 24))



class Piece(Game):

    def __init__(self, x, y, piece):

        self.x, self.y = x, y

        self.piece_type = piece

        self.blocks = list(map(lambda args: Block(*args), pieces_lib.get_piece(x, y, piece)))

        self.rotation = "0"

        
        if piece == "T":
            self.corners = {"point left": [x-1, y-1], "point right": [x+1, y-1], "flat left": [x-1, y+1], "flat right": [x+1, y+1]}

        elif piece == "I":
            self.x += 0.5
            self.y += 0.5

    
    def move(self, x, y):

        self.x += x
        self.y += y

        for block in self.blocks:
            block.x += x
            block.y += y

        if self.piece_type == "T":
            for coords in self.corners.values():
                coords[0] += x 
                coords[1] += y


    def _set_rotation_value(self, direct):

        if direct == 0:
            
            if self.rotation == "0":
                self.rotation = "R"
            
            elif self.rotation == "R":
                self.rotation = "2"
            
            elif self.rotation == '2':
                self.rotation = 'L'

            elif self.rotation == 'L':
                self.rotation = '0'

        else:
            if self.rotation == "0":
                self.rotation = "L"
            
            elif self.rotation == "L":
                self.rotation = "2"
            
            elif self.rotation == '2':
                self.rotation = 'R'

            elif self.rotation == 'R':
                self.rotation = '0'


    def _path_check(self, direct, x, y):

        # invert y direction
        y *= -1

        self.move(x, y)

        if not self.check_overlap():
            game.correct_rotateSFX.play()
            return True

        # reset
        self.move(-1*x, -1*y)
        
        return False



    #0 means clockwise, 1 means counterclockwise
    def rotate(self, direct: int):
       

        if self.piece_type == "O": return game.correct_rotateSFX.play()

        org_block_coords = []

        x, y = self.x, self.y # noqa pylint: disable=unused-variable

        if direct == 0:
            #clockwise
            for block in self.blocks:
                #Math formula
                temp_x, temp_y = block.x, block.y
                org_block_coords.append((temp_x, temp_y))

                block.x = (-1*(temp_y-self.y) + self.x)
                block.y = ((temp_x - self.x) + self.y)

            if self.piece_type == "T":

                org_corner_coords = []
                for coords in self.corners.values():
                    temp_x, temp_y = coords
                    org_corner_coords.append([temp_x, temp_y])

                    coords[0] = (-1*(temp_y-self.y) + self.x)
                    coords[1] = ((temp_x - self.x) + self.y)

            

        else:
            #counter-clockwise
            
            for block in self.blocks:
                #Math formula
                temp_x, temp_y = block.x, block.y
                org_block_coords.append((temp_x, temp_y))
                block.x = (temp_y - self.y + self.x)
                block.y = (-1*(temp_x - self.x) + self.y)

            if self.piece_type == "T":

                org_corner_coords = []
                for coords in self.corners.values():
                    temp_x, temp_y = coords
                    org_corner_coords.append([temp_x, temp_y])

                    coords[0] = (temp_y - self.y + self.x)
                    coords[1] = (-1*(temp_x - self.x) + self.y)


        old_rotation = self.rotation

        self._set_rotation_value(direct)

        if self.check_overlap():

            # all following SRS Tetris guideline

            if self.piece_type == "I":
                
                # clockwise
                if direct == 0:
                    
                    # 0 -> R
                    if old_rotation == "0":
                        if self._path_check(direct, -2, 0): return
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, -2, -1): return
                        if self._path_check(direct, 1, 2): return


                    # R -> 2
                    elif old_rotation == 'R':
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, 2, 0): return
                        if self._path_check(direct, -1, 2): return
                        if self._path_check(direct, 2, -1): return
                    
                    # 2 -> L
                    elif old_rotation == '2':
                        if self._path_check(direct, 2, 0): return
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, 2, 1): return
                        if self._path_check(direct, -1, -2): return

                    # L -> 0
                    elif old_rotation == "L":
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, -2, 0): return
                        if self._path_check(direct, 1, -2): return
                        if self._path_check(direct, -2, 1): return


                # counterclockwise
                else:

                    # R -> 0
                    if old_rotation == "R":
                        if self._path_check(direct, 2, 0): return
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, 2, 1): return
                        if self._path_check(direct, -1, -2): return

                    # 2 -> R
                    elif old_rotation == "2":
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, -2, 0): return
                        if self._path_check(direct, 1, -2): return
                        if self._path_check(direct, -2, 1): return

                    # L -> 2
                    elif old_rotation == "L":
                        if self._path_check(direct, -2, 0): return
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, -2, -1): return
                        if self._path_check(direct, 1, 2): return
                    
                    # 0 -> L
                    elif old_rotation == "0":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, 2, 0): return
                        if self._path_check(direct, -1, 2): return
                        if self._path_check(direct, 2, -1): return



            else:

                # clockwise
                if direct == 0:

                    
                    # 0 -> R
                    if old_rotation == "0":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, -1, 1): return
                        if self._path_check(direct, 0, -2): return
                        if self._path_check(direct, -1, -2): return


                    # R -> 2
                    elif old_rotation == 'R':
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, 1, -1): return
                        if self._path_check(direct, 0, 2): return
                        if self._path_check(direct, 1, 2): return
                    
                    # 2 -> L
                    elif old_rotation == '2':
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, 1, 1): return
                        if self._path_check(direct, 0, -2): return
                        if self._path_check(direct, 1, -2): return

                    # L -> 0
                    elif old_rotation == "L":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, -1, -1): return
                        if self._path_check(direct, 0, 2): return
                        if self._path_check(direct, -1, 2): return


                # counterclockwise
                else:

                    # R -> 0
                    if old_rotation == "R":
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, 1, -1): return
                        if self._path_check(direct, 0, 2): return
                        if self._path_check(direct, 1, 2): return

                    # 2 -> R
                    elif old_rotation == "2":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, -1, 1): return
                        if self._path_check(direct, 0, -2): return
                        if self._path_check(direct, -1, -2): return

                    # L -> 2
                    elif old_rotation == "L":
                        if self._path_check(direct, -1, 0): return
                        if self._path_check(direct, -1, -1): return
                        if self._path_check(direct, 0, 2): return
                        if self._path_check(direct, -1, 2): return
                    
                    # 0 -> L
                    elif old_rotation == "0":
                        if self._path_check(direct, 1, 0): return
                        if self._path_check(direct, 1, 1): return
                        if self._path_check(direct, 0, -2): return
                        if self._path_check(direct, 1, -2): return
            

            # if all tests fail
            self.rotation = old_rotation
            
            # reset
            for index, block in enumerate(self.blocks):
                block.x, block.y = org_block_coords[index]

            if self.piece_type == "T":
                for index, coords in enumerate(self.corners.values()):
                    coords = org_corner_coords[index]
  

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

            if block.y > 20 or block.x < 1 or block.x > 10:
                return True


            for resting in game.resting:

                if block.x == resting.x and block.y == resting.y:
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