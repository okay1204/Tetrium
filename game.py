# pylint: disable=no-member, unused-wildcard-import, no-name-in-module
import pygame
import pieces as pieces_lib
import math
import time
import sys
from random import shuffle, randint, choice
import network
import json
from oooooooooooooooooooooooooooooooooooooooooooootils import *
import _thread
import asyncio
import ntpath
from pyautogui import size as screen_size
from webbrowser import open_new


# these two lines saved my life
import nest_asyncio
nest_asyncio.apply()


if __name__ == "__main__":
    import main


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


class Game:


    def __init__(self):

        #############################
        #############################
        self.dev = False #############
        #############################
        #############################

        if self.dev:
            print("IN DEVELOPMENT MODE: DISABLES DISCORD RPC")


        self.presence_connected = None

        if not self.dev:
            # creates a new asyncio loop
            self.discord_rpc_loop = asyncio.new_event_loop()

            # initializes the discord RPC with this new loop
            self.RPC = pypresence.Presence(
                client_id="778689610263560212",
                loop=self.discord_rpc_loop
            )

            # use a thread to start this loop and run forever
            _thread.start_new_thread(self.start_background_loop, ())

            # then run the task on this loop
            asyncio.run_coroutine_threadsafe(self.start_connect_presence(), self.discord_rpc_loop)

        pygame.init()
        self.font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 32)
        self.time_opened = time.time()


        self.width = 750
        self.height = 800


        self.running = True

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height), flags = pygame.RESIZABLE)

        self.icon = pygame.image.load(get_path('assets/images/tetrium.png'))
        pygame.display.set_icon(self.icon)

        self.caption = "Tetrium"
        pygame.display.set_caption(self.caption)

        # 30px x 30px is one block

        self.resting = []
        self.last_time = 0
        self.continuous = True

        self.round = 1

        self.level = 1
        self.score = 0
        self.lines = 0


        self.time_started = 0


        self.fullscreen = False


        # list of numbers, with numbers being attack amounts
        self.meter = []
        self.meter_stage = 1
 

        self.opp_resting = self.opp_meter = self.opp_meter_stage = self.opp_piece_blocks = None
        self.opp_name = None

        self.rows_cleared = []

        self.small_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 15)
        self.medium_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 20)
        self.big_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 30)
        self.very_big_medium_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 70)
        self.very_big_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 75)


        self.enormous_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 120)
        

        self.default_controls = {
            "Move Right": "d",
            "Move Left": "a",
            "Soft Drop": "s",
            "Hard Drop": "down",
            "Hold Piece": "up",
            "Rotate Clockwise": "right",
            "Rotate Counter-Clockwise": "left",
            "Toggle Movement": "g",
            "Toggle Music": "m",
            "Toggle Fullscreen": "f11"
        }

        with open(get_path('settings.json')) as f:
            settings = json.load(f)

        self.initial_nickname = settings['name']

        self.music = settings['audio']['main'] * settings['audio']['music']
        self.sfx = settings['audio']['main'] * settings['audio']['sfx']


        self.sounds = {
            "correct rotate": pygame.mixer.Sound(get_path('assets/sfx/move_effect_success.wav')),
            "hold": pygame.mixer.Sound(get_path('assets/sfx/hold_effect.wav')),
            "row cleared": pygame.mixer.Sound(get_path('assets/sfx/row_cleared.wav')),
            "meter send": pygame.mixer.Sound(get_path('assets/sfx/meter_send.wav')),
            "meter recieve": pygame.mixer.Sound(get_path('assets/sfx/meter_recieve.wav')),
            "countdown": pygame.mixer.Sound(get_path('assets/sfx/countdown.wav')),
            "countdown go": pygame.mixer.Sound(get_path('assets/sfx/countdown_go.wav')),
            "garbage recieve": pygame.mixer.Sound(get_path('assets/sfx/garbage_recieve.wav'))
        }

        self.sfx_channel = pygame.mixer.Channel(1)
        self.sfx_channel.set_volume(self.sfx)

        # list of all files in music folder
        self.tracks = [get_path(f'assets/music/{filename}') for filename in os.listdir(get_path('assets/music'))]
        self.current_track = settings['track']
        self.random_track = False

        if self.current_track == 'random':
            self.current_track = randint(0, len(self.tracks)-1)
            self.random_track = True
            _thread.start_new_thread(self.cycle_music, ())

        pygame.mixer.music.load(self.tracks[self.current_track])

        pygame.mixer.music.set_volume(self.music)

        if self.random_track:
            pygame.mixer.music.play(0)
        else:
            pygame.mixer.music.play(-1)
       
        self.left_controls = {
            "Move Left": settings["controls"]["Move Left"],
            "Move Right": settings["controls"]["Move Right"],
            "Soft Drop": settings["controls"]["Soft Drop"],
            "Toggle Movement": settings["controls"]["Toggle Movement"],
            "Toggle Music": settings["controls"]["Toggle Music"]
        }

        self.right_controls = {
            "Rotate Clockwise": settings["controls"]["Rotate Clockwise"],
            "Rotate Counter-Clockwise": settings["controls"]["Rotate Counter-Clockwise"],
            "Hold Piece": settings["controls"]["Hold Piece"],
            "Hard Drop": settings["controls"]["Hard Drop"],
            "Toggle Fullscreen": settings["controls"]["Toggle Fullscreen"],
        }

        self.fullscreen_key = settings["controls"]["Toggle Fullscreen"]

        #first tuple is rgb of background color, second is foreground
        self.themes = [
            ['Default', (0, 0, 0), (101, 142, 156)],
            ['Random', (0, 0, 0), (255, 255, 255)],
            ['Blue Mystique', (0, 20, 39), (101, 142, 156)],
            ['Sky High', (39, 38, 53), (177, 229, 242)],
            ['Jungle Adventure', (1, 38, 34), (184, 242, 230)],   
            ['Sahara Desert', (30, 47, 35), (179, 156, 77)],
            ['Cotton Candy', (61, 64, 91), (202, 156, 225)],
            ['Velvety Mango', (60, 21, 24), (255, 140, 66)],
            ['Road to Heaven', (17, 20, 25), (92, 200, 255)],
            ['Night Sky', (0, 0, 0), (0, 20, 39)],
            ['Camouflage', (13, 27, 30), (101, 104, 57)],
            ['Coral Reef', (38, 70, 83), (42, 157, 143)],
            ['Tropical Sands', (38, 70, 83), (233, 196, 106)],
        ]


        try:
            self.theme_index = settings['theme']
        
        except:
            self.theme_index = 0

            with open(get_path('settings.json')) as f:
                full_dict = json.load(f)

            full_dict['theme'] = self.theme_index

            with open(get_path('settings.json'), 'w') as f:
                json.dump(full_dict, f, indent=2)


        theme =  self.themes[self.theme_index]
        self.background_color = theme[1]
        self.foreground_color = theme[2]
        self.set_grid_color(self.foreground_color)
        self.set_text_color(self.foreground_color)
        self.theme_text = theme[0]
        self.random_theme = True if self.theme_text == 'Random' else False
        self.resize_screen_setup()


    
    def cycle_music(self):
        
        try:
            while self.random_track:

                if not pygame.mixer.music.get_busy():

                    self.current_track += 1
                    if self.current_track >= len(self.tracks): self.current_track = 0

                    pygame.mixer.music.load(self.tracks[self.current_track])
                    pygame.mixer.music.play(0)
                    pygame.mixer.music.set_volume(self.music)
        except:
            pass



    def play_sound(self, sound):

        if not self.sfx_channel.get_busy():
            self.sfx_channel.play(self.sounds[sound])
        else:
            self.sounds[sound].set_volume(self.sfx_channel.get_volume())
            self.sounds[sound].play()
            self.sounds[sound].set_volume(1)
       

       
   
    def set_grid_color(self, color):
        self.grid_color = tuple(darken(i, 10) for i in color)
    
    @staticmethod
    def complimentary_color(color: tuple): 
        
        def contrast(val):
            return int(abs((val + 255/2) - 255))
        
        return tuple(contrast(i) for i in color)


    def set_text_color(self, color):
        contrast = self.complimentary_color(color)
        self.text_color = color
        self.preview_color = contrast
        
    def render(self, pieces=None, held=None):
        
        self.screen.fill(self.background_color)
        pygame.draw.rect(self.screen, self.foreground_color, self.playing_field_rect)
        self.draw_grid(self.playing_field_rect, 30, self.grid_color)

        for block in self.resting:
            block.render()

        # for piece order
        for i in range(1, 4):
            pygame.draw.circle(self.screen, self.foreground_color, (self.playing_field_rect.x + self.playing_field_rect.width + 100/2,  (self.playing_field_rect.y - 100) +  130*i), 40)

        text = self.font.render('Next', True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (self.playing_field_rect.x + self.playing_field_rect.width + 100/2, self.playing_field_rect.y - 40)
        self.screen.blit(text, textRect)

        # putting pieces in the circles
        if pieces:
            position = 1
            
            for piece in pieces:
                for color, x, y, width, height in pieces_lib.preview_piece(self.playing_field_rect.x + self.playing_field_rect.width + 100/2, (self.playing_field_rect.y - 100) + position*130, piece):
                    pygame.draw.rect(self.screen, color_key[color], (x, y, width, height))
                
                position += 1
    
        # for hold area
        pygame.draw.circle(self.screen, self.foreground_color, (self.playing_field_rect.x - 100/2, self.playing_field_rect.y + 30), 40)
        text = self.font.render('Hold', True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (self.playing_field_rect.x - 100/2, self.playing_field_rect.y - 40)
        self.screen.blit(text, textRect)

        if held:
            for color, x, y, width, height in pieces_lib.preview_piece(self.playing_field_rect.x - 50, self.playing_field_rect.y + 30, held):
                pygame.draw.rect(self.screen, color_key[color], (x, y, width, height))


        text = self.font.render(f"Continuous Movement: {'On' if self.continuous else 'Off'}", True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (self.playing_field_rect.x + self.playing_field_rect.width/2, self.playing_field_rect.y + self.playing_field_rect.height + 80)
        self.screen.blit(text, textRect)

        font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 25)

        text = font.render(f"Level: {self.level}", True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (self.playing_field_rect.x + self.playing_field_rect.width + 20, self.playing_field_rect.y + self.playing_field_rect.height + 25)
        self.screen.blit(text, textRect)

        self.score = int(self.score)
        text = self.font.render(f"Score: {self.score}", True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (self.playing_field_rect.x + self.playing_field_rect.width/2, self.playing_field_rect.y + self.playing_field_rect.height + 25)
        self.screen.blit(text, textRect)

        text = font.render(f"Lines: {self.lines}", True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (self.playing_field_junk_meter_rect.x + textRect.width/3, self.playing_field_rect.y + self.playing_field_rect.height + 25)
        self.screen.blit(text, textRect)

        font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 20)

        time_elapsed = math.floor(time.time() - self.time_started)

        minutes = time_elapsed // 60
        remaining_seconds = time_elapsed % 60

        time_elapsed = f"{minutes}m {remaining_seconds}s"

        text = font.render(f"Time Elapsed: {time_elapsed}", True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (self.playing_field_rect.x + self.playing_field_rect.width/2,  self.playing_field_rect.y - 75)
        self.screen.blit(text, textRect)


        text = font.render(self.name, True, self.text_color)
        textRect = text.get_rect()

        textRect.center = (self.playing_field_rect.x + self.playing_field_rect.width/2, self.playing_field_rect.y - 20)
        self.screen.blit(text, textRect)


        text = font.render(self.opp_name, True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (self.second_screen_rect.x + self.second_screen_rect.width/2, self.second_screen_rect.y - 20)
        self.screen.blit(text, textRect)


        # junk line meter
        pygame.draw.rect(self.screen, self.preview_color, self.playing_field_junk_meter_rect_outline)
        pygame.draw.rect(self.screen, self.foreground_color, self.playing_field_junk_meter_rect)
        

        meter_block = 0

        for index, amount in enumerate(self.meter):

            if not index and self.meter_stage != 4:
                if self.meter_stage == 1:
                    color = color_key["yellow"]
                elif self.meter_stage  == 2:
                    color = color_key["orange"]
                else:
                    color = color_key["red"]
            else:
                color = color_key["gray"]

            darkened = tuple(darken(i) for i in color)


            for block in range(amount):

                if meter_block >= 10:
                    break
                
                block_rect = pygame.Rect(
                        self.playing_field_junk_meter_rect.x, 
                        (self.playing_field_junk_meter_rect.y + 
                        self.playing_field_junk_meter_rect.height - 30) - 
                        (30 * meter_block), 30, 30
                    )

                pygame.draw.rect(
                    self.screen, 
                    color, 
                    block_rect
                )

                self.draw_block_borders(block_rect, darkened)
               
                meter_block += 1

        
        self.render_second_screen()


    def render_second_screen(self):
        pygame.draw.rect(self.screen, self.foreground_color, self.second_screen_rect)
        self.draw_grid(self.second_screen_rect, 15, self.grid_color)

        if self.time_started + 1 > time.time():
            return
        
        for x, y, color in self.opp_resting: # noqa pylint: disable=not-an-iterable
            Block(x, y, color, colorByName = False).render_second()

        
        if self.opp_piece_blocks:
            for x, y, color in self.opp_piece_blocks: # noqa pylint: disable=not-an-iterable
                Block(x, y, color, colorByName = False).render_second()
        
        # junk line meter
        pygame.draw.rect(self.screen, self.preview_color, self.opp_screen_junk_meter_rect_outline)
        pygame.draw.rect(self.screen, self.foreground_color, self.opp_screen_junk_meter_rect)


        meter_block = 0
        for index, amount in enumerate(self.opp_meter):

            if not index:
                if self.opp_meter_stage == 1:
                    color = color_key["yellow"]
                elif self.opp_meter_stage  == 2:
                    color = color_key["orange"]
                else:
                    color = color_key["red"]
            else:
                color = color_key["gray"]

            darkened = tuple(darken(i) for i in color)

            for _ in range(amount):

                if meter_block >= 10:
                    break
                
                block_rect = pygame.Rect(
                        self.opp_screen_junk_meter_rect.x, 
                        (self.opp_screen_junk_meter_rect.y + 
                        self.opp_screen_junk_meter_rect.height - 15) - 
                        (15 * meter_block), 15, 15
                    )
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    block_rect
                )
                game.draw_block_borders(block_rect, darkened, block_size_difference = 2)
                meter_block += 1

    def draw_grid(self, rect, block_size, color):
        #I subtract 3 in both ones because if not it overlaps a tiny bit and triggeres OCD
        for x_pos in range(rect.x, rect.x + rect.width, block_size):
            pygame.draw.line(self.screen,  color, (x_pos, rect.y), (x_pos, rect.y + rect.height - 3), 1)
        
        for y_pos in range(rect.y, rect.y + rect.height, block_size):
            pygame.draw.line(self.screen, color, (rect.x, y_pos), (rect.x + rect.width - 3, y_pos), 1)



    def outdated_version_screen(self, new_version, download_link):

        text_color = game.foreground_color
        rect_color = tuple(darken(color) for color in game.foreground_color)

        
        copy_button_dimensions = (300, 45)
        copy_button_pos = (self.width/2 - copy_button_dimensions[0]/2, self.height/2 - copy_button_dimensions[1]/2)
        copy_button_rect = pygame.Rect(*copy_button_pos, *copy_button_dimensions)

        quit_button_dimensions = (140, 40)
        quit_button_pos = (self.width/2 - quit_button_dimensions[0]/2, 700)
        quit_button_rect = pygame.Rect(*quit_button_pos, *quit_button_dimensions)
    

        def draw_text():
            text1 = self.font.render("You are running an outdated", True, rect_color)
            text2 = self.font.render("version of the game", True, rect_color)

            text3 = self.font.render(f"Your Version: {network.version}", True, rect_color)
            text4 = self.font.render(f"New Version: {new_version}", True, rect_color)

            self.screen.blit(text1, (self.width/2-200, 100))
            self.screen.blit(text2, (self.width/2-130, 150))
            self.screen.blit(text3, (self.width/2-140, 250))
            self.screen.blit(text4, (self.width/2-140, 290))


        def draw_buttons(mouse):
        
            pygame.draw.rect(self.screen, tuple(darken(i, 15) for i in rect_color) if copy_button_rect.collidepoint(mouse) else rect_color, copy_button_rect)
                
            copy_button_text = self.font.render("UPDATE NOW", True, text_color)
            self.screen.blit(copy_button_text, (copy_button_pos[0] + 40, copy_button_pos[1] + 3))
            

            pygame.draw.rect(self.screen, tuple(darken(i, 15) for i in rect_color) if quit_button_rect.collidepoint(mouse) else rect_color, quit_button_rect)

            quit_button_text = self.font.render("Go Back", True, text_color)
            self.screen.blit(quit_button_text, (quit_button_pos[0] + 10, quit_button_pos[1] + 3))

        breakOut = False

        def check_click(pos):

            nonlocal breakOut
            

            if copy_button_rect.collidepoint(pos):
                open_new(download_link)
        

            elif quit_button_rect.collidepoint(pos):
                breakOut = True

        while True:

            game.screen.fill(game.background_color)

            for event in pygame.event.get():

    
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.VIDEORESIZE or self.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()
                    copy_button_pos = (self.width/2 - copy_button_dimensions[0]/2, self.height/2 - copy_button_dimensions[1]/2)
                    copy_button_rect = pygame.Rect(*copy_button_pos, *copy_button_dimensions)
                    quit_button_pos = (self.width/2 - quit_button_dimensions[0]/2, 700)
                    quit_button_rect = pygame.Rect(*quit_button_pos, *quit_button_dimensions)

                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    check_click(event.pos)


            draw_text()
            draw_buttons(pygame.mouse.get_pos())

            if breakOut:
                break

            pygame.display.update()
            self.clock.tick(60)

    
    def disconnected_screen(self, text1, text2):

        def draw_text():
            dc_text_1 = self.font.render(text1, True, game.foreground_color)
            dc_text_2 = self.font.render(text2,  True, game.foreground_color)
            self.screen.blit(dc_text_1, (self.width/2 - dc_text_1.get_rect().width/2, 200))
            self.screen.blit(dc_text_2, (self.width/2 - dc_text_2.get_rect().width/2, 300))

   
        def draw_button():

            pygame.draw.rect(self.screen, tuple(darken(color, 15) for color in game.foreground_color) if button_rect.collidepoint(mouse) else game.foreground_color, button_rect)

                
            button_text = self.font.render("FIND NEW MATCH", True, button_text_color)
            self.screen.blit(button_text, (button_pos[0] + 10, button_pos[1] + 3))

        def check_click(pos):
            nonlocal disconnected
            if button_rect.collidepoint(pos):
                disconnected = False
                game.running = False


        button_text_color = (0,0,0)
        button_dimensions = (300, 40)
        button_pos = (self.width/2 - button_dimensions[0]/2, self.height/2 - button_dimensions[1]/2)
        button_rect = pygame.Rect(*button_pos, *button_dimensions)
        disconnected = True
        while disconnected:

            mouse = pygame.mouse.get_pos() 

            for event in pygame.event.get():


                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE or self.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()
                    button_pos = (self.width/2 - button_dimensions[0]/2, self.height/2 - button_dimensions[1]/2)
                    button_rect = pygame.Rect(*button_pos, *button_dimensions)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    
                    check_click(event.pos)


            self.screen.fill(game.background_color)

            draw_text()
            draw_button()

            pygame.display.update()
            game.clock.tick(60)


    def countdown(self, countdown):

        # countdown is actually 4 seconds long, consisting of 3, 2, 1, and GO
        pygame.mixer.music.pause()
        last_second = 100
        while countdown > time.time():

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return False


                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()

            seconds = int(countdown - time.time())

            if seconds != last_second:

                if seconds:
                    self.play_sound('countdown')
                else:
                    self.play_sound('countdown go')


            last_second = seconds

            if not seconds:
                seconds = "GO"
            

            self.screen.fill(game.background_color)

            above_text = self.medium_font.render("Game starts in...", True, game.foreground_color)
            self.screen.blit(above_text, (game.width/2-above_text.get_rect().width/2, 150))

            countdown_text = self.enormous_font.render(str(seconds), True, game.foreground_color)
            self.screen.blit(countdown_text, (game.width/2-countdown_text.get_rect().width/2, game.height/2))


            pygame.display.update()
            self.clock.tick(60)


        pygame.mixer.music.unpause()

        game.time_started = time.time()

        return True


    async def connect_presence(self):
        try:
            print("Connecting to Discord RPC...")
            self.RPC.connect()
            print("Discord RPC connected")
            self.presence_connected = True
        except Exception as e:
            print(e)
            self.presence_connected = False

    async def start_connect_presence(self):

        self.discord_rpc_loop.create_task(self.connect_presence())


    def start_background_loop(self):
        asyncio.set_event_loop(self.discord_rpc_loop)
        self.discord_rpc_loop.run_forever()
        

    async def async_update_presence(self, details, state, start, large_image):
        try:
            self.RPC.update(
                state=state,
                details=details,
                start=start,
                large_image=large_image,
                large_text=large_image
            )
        except Exception as e:
            print(e)

    def update_presence(self, state, details, start, large_image):
        if not self.dev and self.presence_connected:
            self.discord_rpc_loop.create_task(self.async_update_presence(details, state, start, large_image))

    def check_random_theme(self):
        if self.random_theme:
            random_theme_pick = randint(0, len(self.themes) -1)
            theme = self.themes[randint(0, len(self.themes) -1)]

            while theme[0] == 'Random':
                random_theme_pick = randint(0, len(self.themes) -1)
                theme = self.themes[random_theme_pick]

            self.background_color = theme[1]
            self.foreground_color = theme[2]
            self.set_text_color(self.foreground_color)
            self.set_grid_color(self.foreground_color)
            settings_screen.set_buttons_color(self.foreground_color)


    @staticmethod
    def draw_block_borders(block_rect, color, block_size_difference = 5):

            block_size = block_rect.width
            #draw trapezoid on bottom
            pygame.draw.polygon(game.screen, color, 

                [     
                        #bottom left of trapezoid
                    (block_rect.x, block_rect.y + block_rect.height),
                        #top left of trapezoid
                    (block_rect.x + block_size_difference, block_rect.y + block_size - block_size_difference),
                         #top right of trapezoid
                     (block_rect.x + block_size - block_size_difference, block_rect.y + block_size - block_size_difference),
                        #bottom right of trapezoid
                    (block_rect.x + block_rect.width, block_rect.y + block_rect.height)
                ]
      
            )

            #draw trapezoid on right
            pygame.draw.polygon(game.screen, tuple(lighten(i, 15) for i in color), 

                [     
                        #bottom left of trapezoid
                    (block_rect.x + block_rect.width, block_rect.y + block_rect.height),
                        #top left of trapezoid
                     (block_rect.x + block_size - block_size_difference, block_rect.y + block_size - block_size_difference),
                         #top right of trapezoid
                     (block_rect.x + block_size - block_size_difference, block_rect.y + block_size_difference),
                        #bottom right of trapezoid
                    (block_rect.x + block_rect.width, block_rect.y)
                ]

            )




    def resize_screen_setup(self):
        #BEFORE:
            # self.playing_field_rect = pygame.Rect(100, 100, 300, 600)
            # self.second_screen_rect = pygame.Rect(570, 250, 150, 300)
            # self.playing_field_junk_meter_rect = pygame.Rect(35, 397, 30, 300)
            # self.playing_field_junk_meter_rect_outline = pygame.Rect(32, 394, 36, 306)
            # self.opp_screen_junk_meter = pygame.Rect(540, 399, 15, 150)
            # self.opp_screen_junk_meter_outline = pygame.Rect(539, 398, 17, 152)


        #NOTE y and for this rect has to have 100 margin on both sides
        #NOTE x and for this rect has to have 100 margin left, 350 margin right
        playing_field_rect_height = 600
        playing_field_rect_y = self.height/2 - playing_field_rect_height/2
        playing_field_rect_x = (self.width - 350 - 200)/2
        self.playing_field_rect = pygame.Rect(playing_field_rect_x, playing_field_rect_y, 300, 600)
        self.block_y_offset = playing_field_rect_y
        self.second_block_y_offset = self.block_y_offset + 150
        self.block_x_offset = playing_field_rect_x - 100
        
        playing_field_junk_meter_width = 30
        playing_field_junk_meter_height = self.playing_field_rect.width
        self.playing_field_junk_meter_rect = pygame.Rect(
            self.playing_field_rect.x - 100/2 - playing_field_junk_meter_width/2, 
            self.playing_field_rect.y + self.playing_field_rect.height - playing_field_junk_meter_height,
            playing_field_junk_meter_width,
            playing_field_junk_meter_height
            )

        offset = 6
        self.playing_field_junk_meter_rect_outline = pygame.Rect(
            self.playing_field_junk_meter_rect.x - offset/2,
            self.playing_field_junk_meter_rect.y - offset/2,
            self.playing_field_junk_meter_rect.width + offset,
            self.playing_field_junk_meter_rect.height + offset,
            
            )


        second_screen_rect_height = 150
        self.second_screen_rect = pygame.Rect(
            
            self.playing_field_rect.x + self.playing_field_rect.width + 170, 
            self.playing_field_rect.y + self.playing_field_rect.height/2 - second_screen_rect_height, 
            second_screen_rect_height, 
            300,
            )


        opp_screen_junk_meter_height = self.second_screen_rect.width
        self.opp_screen_junk_meter_rect = pygame.Rect(
            self.second_screen_rect.x - 30,
            self.second_screen_rect.y + self.second_screen_rect.height - opp_screen_junk_meter_height,
            15, 
            opp_screen_junk_meter_height

            )

        offset = 3
        self.opp_screen_junk_meter_rect_outline = pygame.Rect(
            self.opp_screen_junk_meter_rect.x - offset/2,
            self.opp_screen_junk_meter_rect.y - offset/2,
            self.opp_screen_junk_meter_rect.width + offset,
            self.opp_screen_junk_meter_rect.height + offset,
            
            )

    def check_fullscreen(self, event, ingame = False):

        mouse_number_key = {
            1: 'left click',
            2: 'middle click',
            3: 'right click'
        }

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):

            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)

            else:
                if 1 <= event.button <= 3:
                    key_name = mouse_number_key[event.button]
                else:
                    key_name = None

            
            if key_name == self.fullscreen_key:
                self.toggle_fullscreen()
                if ingame:
                    pygame.mouse.set_visible(False)

                return True
        
        return False


    def toggle_fullscreen(self):

        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            
            self.width, self.height = screen_size()

            pygame.display.quit()
            self.screen = pygame.display.set_mode((self.width, self.height), flags = pygame.FULLSCREEN)
            pygame.display.init()

        else:

            self.width, self.height = 750, 800

            pygame.display.quit()
            self.screen = pygame.display.set_mode((750, 800), flags = pygame.RESIZABLE)
            pygame.display.init()

            pygame.display.set_icon(self.icon)
            pygame.display.set_caption(self.caption)

        self.resize_all_screens()



    def resize_all_screens(self):
        self.resize_screen_setup()
        start_screen.resize_screen()
        settings_screen.resize_screen()
        pygame.display.flip()
            
game = Game()


class StartScreen(Game):

    def __init__(self):

        self.ready = False

        self.rgb_stage = 0

        self.version_text = game.small_font.render(f"v {network.version}", True, (255, 255, 255))
        self.input_box_width = 300
        self.input_box_height = 50
        self.mute_button_radius = 35
        self.start_button_text_color = (255, 255, 255)
        self.credits_button_height = 30
        self.input_text_width = 0
        self.back_button = pygame.Rect(10, 10, 75, 65)
        self.piece_types = ['I', 'O', 'T', 'L', 'J', 'Z', 'S']
        self.resize_screen()
    
        self.r, self.g, self.b = 255, 0, 0
        self.last_falls = [time.time() for _ in self.pieces]

        self.input_box_placeholder = game.medium_font.render("Enter a name...", True, (96, 93, 93))
        self.input_active = False
        self.input_text = game.initial_nickname
        self.settings_button_text = game.medium_font.render('SETTINGS', True, (0, 0, 0))
        self.credits_button_text = game.small_font.render('CREDITS', True, (0, 0, 0))
        self.connected = False
        self.started = False
        self.back_icon = pygame.image.load(get_path('assets/images/arrow-back.png'))
        self.disconnect_button_text = game.font.render('Disconnect', True, (self.r, self.g, self.b))

    def resize_screen(self):
        self.max_x = int((game.width/30)-4) 
        self.max_y = int((game.height/30))
        step_y = 5
        step_x = 1
        #It might seem confusing whats happeneing here but dw about it, just making sure blocks are spaced out
        self.x_pos = list(range(-3, self.max_x, step_x)) + [randint(0, self.max_x) for _ in range(3)]
        self.y_pos = list(range(-3, self.max_y, step_y)) + [randint(0, self.max_y) for _ in range(3)]

        shuffle(self.x_pos)
        shuffle(self.y_pos)


        self.pieces = [
            Piece(x_pos, y_pos, choice(self.piece_types)) for x_pos, y_pos in zip(self.x_pos, self.y_pos)
        ]

        rect = self.version_text.get_rect()
        self.version_text_rect = self.version_text.get_rect(center=(game.width-(rect.width/2)-10, rect.height+10))
    
        self.r, self.g, self.b = 255, 0, 0
        self.last_falls = [time.time() for _ in self.pieces]
        self.start_button_text_color = (255, 255, 255)
        self.start_button_rect = pygame.Rect(game.width/2-60, game.height/2, 120, 40)
        self.disconnect_button_rect = pygame.Rect(game.width/2-90, game.height/2+200, 175, 40)

        self.s = pygame.Surface((game.width, game.height), pygame.SRCALPHA) # noqa pylint: disable=too-many-function-args
        self.input_box_y =  game.height/2 - 85
        
        self.input_box_x = (game.width - self.input_box_width)/2
        
        self.input_box = pygame.Rect(self.input_box_x, self.input_box_y, self.input_box_width, self.input_box_height)
        self.input_box_bkg = pygame.Rect((game.width - self.input_box_width)/2 , game.height/2 - 85, self.input_box_width, self.input_box_height)
        self.settings_button_pos = (0 , game.height - 30)
        self.settings_button = pygame.Rect(0, game.height - self.credits_button_height, 125, self.credits_button_height)
        self.credits_button_pos = (game.width - 70, game.height - self.credits_button_height)
        self.credits_button = pygame.Rect(self.credits_button_pos[0], self.credits_button_pos[1], 70, self.credits_button_height)
        self.back_icon = pygame.image.load(get_path('assets/images/arrow-back.png'))
        self.back_button = pygame.Rect(10, 10, 75, 65)
        self.disconnect_button_rect = pygame.Rect(game.width/2-90, game.height/2+70, 175, 40)
        self.disconnect_button_text = game.font.render('Disconnect', True, (self.r, self.g, self.b))


    def check_started(self):
        return not self.started

    def draw_back_button(self, pos = (-10, -10)):
        white = (255, 255, 255)
        color = tuple(darken(i) for i in white) if start_screen.back_button.collidepoint(pos) else white
        pygame.draw.rect(game.screen, color, start_screen.back_button)
        game.screen.blit(start_screen.back_icon, (-3, -7))

    
    def draw_start_button(self):
       
        #if mouse hovering make it lighter
        if self.start_button_rect.collidepoint(self.mouse): 
            colooooooooor = (255,255,255)
            self.start_button_text_color = (self.r, self.g, self.b)
        
        else: 
            colooooooooor = (0, 0, 0)
            self.start_button_text_color = (255, 255, 255)

        pygame.draw.rect(game.screen, colooooooooor, self.start_button_rect)

    
    def credits_screen(self):

        
        credits_list = ['Made by', 'okay#2996', 'and', 'AliMan21#6527']
        text_y = 0
        text_offset = 80    
        text_scroll_dist_multiplier = 4000

        def draw_text(tup):
            index, text = tup
            rendered_text = game.font.render(text, True, (255,255,255))
            game.screen.blit(rendered_text, (rendered_text.get_rect(center = (game.width/2, game.height/2))[0], text_y + (index * text_offset)))
        
       

        running = True
        while running:
            mouse = pygame.mouse.get_pos()
            #Makes sure that if game starts while were in this screen it goes back to game
            running = start_screen.check_started()

            #Game over loop
            for event in pygame.event.get():

               

                if event.type == pygame.QUIT:

                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button.collidepoint(event.pos):
                        running = False
                        break

            text_scroll_dist = game.width / text_scroll_dist_multiplier
            game.screen.fill((0, 0, 0))
            self.draw_tetris_pieces(self.pieces)
            self.draw_back_button(mouse)
            text_y = text_y + text_scroll_dist if text_y <= (game.height + 100) else -1 * (len(credits_list) * text_offset)
            list(map(draw_text, enumerate(credits_list)))
            pygame.display.update()
    
    
    def draw_text(self, mouse):


        if not self.connected:
            self.start_button_text = game.font.render('START', True, self.start_button_text_color)
        
        else:
            self.start_button_text = game.font.render('Waiting for opponent...', True, (self.r, self.g, self.b))
            self.start_button_rect.x = game.width/2-60 - 100
            if self.disconnect_button_rect.collidepoint(mouse):
                color = tuple(darken(i) for i in (255, 255, 255))
            else:
                color = (255, 255, 255)
                
            pygame.draw.rect(game.screen, color, self.disconnect_button_rect)
            game.screen.blit(self.disconnect_button_text, (self.disconnect_button_rect.x + 7, self.disconnect_button_rect.y + 1))
            

        title_text = game.very_big_font.render('TETRIUM', True, (self.r, self.g, self.b)) 
        game.screen.blit(self.start_button_text, (self.start_button_rect.x + 7, self.start_button_rect.y + 3))
        game.screen.blit(title_text, (game.width/2 - 165, game.height/2 - 200)) 


        game.screen.blit(self.version_text, self.version_text_rect)

    
    def draw_input_text(self):
       
        if not self.input_text:
            game.screen.blit(self.input_box_placeholder, (self.input_box_x + 25, self.input_box_y + 12))


        input_text_render = game.big_font.render(self.input_text, True, (0, 0, 0))
        self.input_text_width = input_text_render.get_rect().width
        game.screen.blit(input_text_render, (self.input_box_x + 5, self.input_box_y + 6))


    def draw_input_box(self):
        if self.input_active:
            input_bkg_color = (0, 0, 255)

        else:
            input_bkg_color = (0, 0, 0)

        pygame.draw.rect(game.screen, input_bkg_color, self.input_box, 10)
        pygame.draw.rect(game.screen, (255,255,255), self.input_box_bkg)

        self.draw_input_text()
        
        

    def get_input(self, key):
       
        if self.input_text_width < self.input_box_width - 15:
            self.input_text += key

    def start(self):
        
        self.input_active = False

        # saving nickname
        with open(get_path('settings.json')) as f:
            settings = json.load(f)

        settings['name'] = self.input_text

        with open(get_path('settings.json'), 'w') as f:
            json.dump(settings, f, indent=2)

        game.n = network.Network()
        if game.n.p == "no connection":
            self.no_connection_screen()
            return            



        self.input_text = self.input_text.strip()
        if not self.input_text:
            self.input_text = "Player"

        if isinstance(game.n.p, str):
            outdated_info = game.n.p.split()
                                        # new version number # download link
            game.outdated_version_screen(outdated_info[2], outdated_info[3])
            return

        game.update_presence(
            details="In Start Menu",
            state="Waiting for match",
            start=game.time_opened,
            large_image="tetrium"
        )

        self.start_button_rect.x -=  100
        self.connected = True
        game.name = self.input_text
        game.n.send("name " + self.input_text)
        _thread.start_new_thread(self.wait_for_game, ())

    def cycle_colors(self, rgb):
        r, g, b = rgb
    

        if self.rgb_stage == 0:
            if g < 255 and r > 0:
                g += 1
                r -= 1
            else:
                self.rgb_stage = 1


        elif self.rgb_stage == 1:
            if b < 255 and g > 0:
                b += 1
                g -= 1
                
            else:
                self.rgb_stage = 2

        elif self.rgb_stage == 2:
            if r < 255 and b > 0:
                r += 1
                b -= 1
            else:
                self.rgb_stage = 0
        
        return (r, g, b)
        
    def draw_tetris_pieces(self, pieces, rotate = True):
        for i, piece in enumerate(pieces):
            #means piece is off the screen
            if piece.y >= 28:
                #Moves it back up
                piece.move(0, -30)


            piece.render(False)

            try:
                if time.time() > self.last_falls[i]:
                    piece.move(0, 1)
                    self.last_falls[i] = time.time() + 0.75
                    #this is just an algorithm for occasionally turning the pieces
                    if rotate and randint(0, 7) == 3:
                        piece.rotate(randint(0, 1), False)


            except:
                break



    def draw_credits_button(self, pos):
        color = tuple(map(lighten, (self.r,self.g, self.b))) if self.credits_button.collidepoint(pos) else (self.r, self.g, self.b)
        pygame.draw.rect(game.screen, color, self.credits_button)
        game.screen.blit(self.credits_button_text, (self.credits_button_pos[0] + 3, self.credits_button_pos[1] + 5))   


    def draw_settings_button(self, pos):
        color = tuple(map(lighten, (self.r,self.g, self.b))) if self.settings_button.collidepoint(pos) else (self.r, self.g, self.b)
        pygame.draw.rect(game.screen, color, self.settings_button)
        game.screen.blit(self.settings_button_text, (self.settings_button_pos[0] + 10, self.settings_button_pos[1] + 3))

    def wait_for_game(self):

        self.status = 'get'
        while True:

            if self.status == 'get':
                data = game.n.send('get')

            elif self.status == 'disconnect':
                game.n.disconnect()
                break
            
            try:
                if data.ready: #type: ignore

                    time.sleep(1)
                    data = game.n.send('get')
                    game.opp_name = data.opp_name(game.n.p)
                    self.ready = True
                    self.started = True
                    break
            
            except Exception as e:
                if not isinstance(e, AttributeError):
                    raise e
                break


        
    def no_connection_screen(self):

        display_time = time.time() + 3

        game.screen.fill(game.background_color)

        text = game.very_big_font.render("No connection", True, game.foreground_color)
        game.screen.blit(text, (game.width/2-text.get_rect().width/2, 300))
        pygame.display.update()

        while display_time > time.time():

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()

            game.clock.tick(60)


    
    def main(self):

        running = True
        initial_presence = False
        while running:

            #NOTE make sure this is at the top
            self.s.fill((0,0,0, 2))
            #Makes sure that if game starts while were in this screen it goes back to game
            running = start_screen.check_started()

            # print(initial_presence, game.presence_connected)
            if not initial_presence and game.presence_connected:

                game.update_presence(
                    details = "In Start Menu",
                    state = "Idling",
                    start = game.time_opened,
                    large_image = "tetrium"
                )

                initial_presence = True


            self.mouse = pygame.mouse.get_pos() 
            
            #Game over loop
            for event in pygame.event.get():


                if event.type == pygame.QUIT:

                    if self.connected:
                        game.n.disconnect()

                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()

                 
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    
                    if self.start_button_rect.collidepoint(event.pos) and not self.connected:  

                        self.start()
                        game.screen.fill((0, 0, 0))
                      
                    
                    elif self.disconnect_button_rect.collidepoint(event.pos) and self.connected:
                        self.status = 'disconnect'
                        self.start_button_rect.x = game.width/2-60
                        game.screen.fill((0, 0, 0))
                        self.connected = False
                        game.update_presence(
                            details="In Start Menu",
                            state="Idling",
                            start=game.time_opened,
                            large_image="tetrium"
                        )
                    
                    elif self.credits_button.collidepoint(event.pos):
                        self.credits_screen()
                        #NOTE after we go back from the credits screen, we have to refresh the screen with black so the text doesnt linger over, because our background is opaque
                        self.s.fill((0, 0, 0))

                    elif self.settings_button.collidepoint(event.pos):
                        settings_screen.main()
                        #NOTE after we go back from the credits screen, we have to refresh the screen with black so the text doesnt linger over, because our background is opaque
                        self.s.fill((0, 0, 0))


                    elif self.input_box.collidepoint(event.pos) and not self.connected:
                        self.input_active = True
                    
                    else: 
                        self.input_active = False

                elif event.type == pygame.KEYDOWN:
                    
                    if self.input_active:
                        
                        if event.key == pygame.K_RETURN:
                            self.start()
                            game.screen.fill((0, 0, 0))
                                

                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]

                        else:
                            self.get_input(event.unicode)

                        
            game.screen.blit(self.s, (0, 0))
            self.r, self.g, self.b = self.cycle_colors((self.r, self.g, self.b))
            self.draw_tetris_pieces(self.pieces)
            self.draw_credits_button(self.mouse)
            self.draw_settings_button(self.mouse)

            if not self.connected:
                self.draw_start_button()
                
            self.draw_text(self.mouse)
            self.draw_input_box()

            # checking if game started
            if self.connected and self.ready:
                self.connected = False
                self.start_button_rect = pygame.Rect(game.width/2-60, game.height/2, 120, 40)
                self.started = True
                running = False
                break
            
                
            pygame.display.update()

            game.clock.tick(60)

        game.time_started = time.time()
        game.running = True



class SettingsScreen(StartScreen):


    def __init__(self):
        self.buttons_color = game.foreground_color
        self.background_color = game.background_color
        self.resize_screen()
    
        

    def set_buttons_color(self, color):
        self.buttons_color = color
        for i in range(len(self.buttons)):
            self.buttons[i][2] = color


    def resize_screen(self):
        self.buttons = [
            [
                pygame.Rect(game.width/2 - 200/2, game.height/2 - 200, 200, 50), 
                game.big_font.render('CONTROLS', True,  (0, 0, 0)),
                self.buttons_color,
                self.pick_controls_screen
            ], 
            [
                pygame.Rect(game.width/2 - 200/2, game.height/2 - 100, 200, 50), 
                game.big_font.render('THEMES', True, (0, 0, 0)), 
                self.buttons_color,
                self.pick_themes_screen
            ],
            [
                pygame.Rect(game.width/2 - 200/2, game.height/2, 200, 50), 
                game.big_font.render('GAMEPLAY', True, (0, 0, 0)), 
                self.buttons_color,
                self.gameplay_screen
            ],
            [
                pygame.Rect(game.width/2 - 200/2, game.height/2 + 100, 200, 50), 
                game.big_font.render('AUDIO', True, (0, 0, 0)), 
                self.buttons_color,
                self.audio_screen
            ]
        ]


    def audio_screen(self):

        with open(get_path('settings.json')) as f:
            settings = json.load(f)

        audio_settings = settings['audio']
        
        slider_width = game.width/1.5
        slider_radius = game.height/80

        sliders = [
            {
                "json name": "main",
                "name": "Main Volume",
                "pos": (0, 0),
                "default": 1.0
            },
            {
                "json name": "music",
                "name": "Music",
                "pos": (0, 0),
                "default": 0.5
            },
            {
                "json name": "sfx",
                "name": "Sound Effects",
                "pos": (0, 0),
                "default": 1.0
            },
        ]

        def set_slider_pos():
            for i in range(len(sliders)):
                y_pos = (game.height/8 + game.height/16) * (i + 0.5)
                sliders[i]['pos'] = (game.width/2, y_pos)

        set_slider_pos()

        def screen_size_change():
            set_slider_pos()
            reset_button_rect.x = game.width/2-40
            reset_button_rect.y = game.height - 35



        for x in range(len(sliders)):
            sliders[x]["value"] = audio_settings[sliders[x]["json name"]]

        def draw_sliders():

            for slider in sliders:
                name, pos, value = slider["name"], slider["pos"], slider["value"]

                text_element = game.big_font.render(name, True, game.foreground_color)
                game.screen.blit(text_element, (pos[0] - text_element.get_rect().width/2, pos[1]))

                pygame.draw.rect(game.screen, game.foreground_color, (pos[0] - slider_width/2, pos[1] + 70, slider_width, 4))
                pygame.draw.circle(game.screen, game.foreground_color, center= ((pos[0]-slider_width/2) + int(value * slider_width), pos[1]+72), radius=slider_radius)

                
                measurement = f'{int(value*100)}%'
                value_element = game.medium_font.render(measurement, True, game.foreground_color)
                game.screen.blit(value_element, (pos[0] - value_element.get_rect().width/2, pos[1]+90))
        

        reset_button_rect = pygame.Rect(game.width/2-40, game.height - 35, 80, 25)

        def path_leaf(path):
            head, tail = ntpath.split(path)
            return tail or ntpath.basename(head)

        track_names = [path_leaf(path).replace('.wav', '') for path in game.tracks]

        def draw_reset_button():

            if reset_button_rect.collidepoint(mouse):
                reset_button_color = tuple(darken(color, 15) for color in game.foreground_color)
            else:
                reset_button_color = game.foreground_color
           
            pygame.draw.rect(game.screen, reset_button_color, reset_button_rect)

            reset_button_text = game.medium_font.render("RESET", True, game.background_color)
            game.screen.blit(reset_button_text, (game.width/2-reset_button_text.get_rect().width/2, reset_button_rect.y))

        
        left_arrow = pygame.image.load(get_path('assets/images/left_arrow.png'))
        left_arrow = pygame.transform.scale(left_arrow, (30, 30))
        dimensions = left_arrow.get_height()
        left_arrow_pos = (game.width/4 - left_arrow.get_width()/2, game.height - dimensions/2 - 140)
        right_arrow = pygame.image.load(get_path('assets/images/right_arrow.png'))
        right_arrow = pygame.transform.scale(right_arrow, (30, 30))
        right_arrow_pos =  (((game.width/4)*3) - right_arrow.get_width()/2, game.height - dimensions/2 - 140)
        left_arrow_rect = left_arrow.get_rect(center = (left_arrow_pos[0] + dimensions/2, left_arrow_pos[1] + dimensions/2))
        right_arrow_rect = right_arrow.get_rect(center = (right_arrow_pos[0] + dimensions/2, right_arrow_pos[1] + dimensions/2))
        hover_scale_factor = 1.1


        def is_dark(rgb):
            
            r, g, b = rgb
            cutoff = 30
            if r < cutoff and g < cutoff and b < cutoff:
                return True
            return False


        def draw_arrows(mouse):
            dark = is_dark(game.background_color)

            #hover effect
            if left_arrow_rect.collidepoint(mouse):
                
                if dark:
                    new_left_arrow = left_arrow
                    new_left_arrow_rect = new_left_arrow.get_rect(center = (left_arrow_pos[0] + dimensions/2, left_arrow_pos[1] + dimensions/2))
                    new_left_arrow_rect_color = tuple(darken(i) for i in game.foreground_color)
               
            
                else:
                    new_left_arrow = pygame.transform.scale(left_arrow, (int(dimensions * hover_scale_factor), int(dimensions * hover_scale_factor)))
                    new_left_arrow_rect = new_left_arrow.get_rect(center = (left_arrow_pos[0] + dimensions/2, left_arrow_pos[1] + dimensions/2))
                    new_left_arrow_rect_color = game.foreground_color

            else:
                new_left_arrow = left_arrow
                new_left_arrow_rect = left_arrow_rect
                new_left_arrow_rect_color = game.foreground_color


            if right_arrow_rect.collidepoint(mouse):

                if dark:
                    new_right_arrow = right_arrow
                    new_right_arrow_rect = new_right_arrow.get_rect(center = (right_arrow_pos[0] + dimensions/2, right_arrow_pos[1] + dimensions/2))
                    new_right_arrow_rect_color = tuple(darken(i) for i in game.foreground_color)
                
                
                
                else:
                    new_right_arrow = pygame.transform.scale(right_arrow, (int(dimensions * hover_scale_factor), int(dimensions * hover_scale_factor)))
                    new_right_arrow_rect = new_right_arrow.get_rect(center = (right_arrow_pos[0] + dimensions/2, right_arrow_pos[1] + dimensions/2))
                    new_right_arrow_rect_color = game.foreground_color

            else:
                new_right_arrow = right_arrow
                new_right_arrow_rect = right_arrow_rect
                new_right_arrow_rect_color = game.foreground_color
                


            if dark:
                pygame.draw.rect(game.screen, new_left_arrow_rect_color, new_left_arrow_rect)
                pygame.draw.rect(game.screen, new_right_arrow_rect_color, new_right_arrow_rect)

            game.screen.blit(new_left_arrow, left_arrow_pos)
            game.screen.blit(new_right_arrow, right_arrow_pos)



        if not game.random_track:
            music_name = track_names[game.current_track]
        else:
            music_name = "Auto Cycle"

        
        def draw_music_switcher():

            soundtrack_text = game.medium_font.render("Soundtrack", True, game.foreground_color)
            game.screen.blit(soundtrack_text, (game.width/2-soundtrack_text.get_rect().width/2, game.height-210))

            music_name_text = game.big_font.render(music_name, True, game.foreground_color)
            game.screen.blit(music_name_text, (game.width/2-music_name_text.get_rect().width/2, game.height-160))

            draw_arrows(mouse)

        if not game.random_track:
            track_number = game.current_track + 1
        else:
            track_number = 0

        def next_music(direction):
            nonlocal music_name, track_number

            options = track_names.copy()
            options.insert(0, "Auto Cycle")


            # right
            if direction == 1:
                track_number += 1

                if track_number >= len(options):
                    track_number = 0
            # left
            elif direction == 0:
                track_number -= 1

                if track_number < 0:
                    track_number = len(options) - 1


            music_name = options[track_number]

            pygame.mixer.music.stop()

            if track_number == 0:
                game.current_track = randint(0, len(game.tracks)-1)

                if not game.random_track:
                    pygame.mixer.music.stop()
                    game.random_track = True
                    _thread.start_new_thread(game.cycle_music, ())

                settings['track'] = 'random'
            
            else:
                game.random_track = False
                game.current_track = track_number - 1

                pygame.mixer.music.load(game.tracks[game.current_track])
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(game.music)

                settings['track'] = game.current_track

            
    
        running = True
        dragging = None
        while running:

            running = start_screen.check_started()

            for slider in sliders:
                audio_settings[slider["json name"]] = slider["value"]


            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()
                    screen_size_change()
                    left_arrow_pos = (game.width/4 - left_arrow.get_width()/2, game.height - dimensions/2 - 140)
                    right_arrow_pos =  (((game.width/4)*3) - right_arrow.get_width()/2, game.height - dimensions/2 - 140)
                    left_arrow_rect = left_arrow.get_rect(center = (left_arrow_pos[0] + dimensions/2, left_arrow_pos[1] + dimensions/2))
                    right_arrow_rect = right_arrow.get_rect(center = (right_arrow_pos[0] + dimensions/2, right_arrow_pos[1] + dimensions/2))
                    slider_width = game.width/1.5
                    slider_radius = game.height/80




                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # back button
                    if start_screen.back_button.collidepoint(event.pos):
                        running = False

                        with open(get_path('settings.json'), 'w') as f:
                            json.dump(settings, f, indent=2)

                        
                    elif reset_button_rect.collidepoint(mouse):

                        for slider in sliders:
                            slider['value'] = slider['default']

                        track_number = 0
                        next_music(-1)



                    elif left_arrow_rect.collidepoint(event.pos):
                        next_music(0)

                    elif right_arrow_rect.collidepoint(event.pos):
                        next_music(1)



                    elif not dragging:
                        for slider in sliders:
                            x, y = slider["pos"]
                            value = slider["value"]

                            if x - slider_width/2 + int(value * slider_width) - slider_radius < mouse[0] < x - slider_width/2 + int(value * slider_width) + slider_radius and y + 72 - slider_radius < mouse[1] < y + 72 + slider_radius:
                                dragging = slider["name"]
                                break

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

                    if dragging: dragging = None

            if dragging:
                for slider in sliders:
                    if slider["name"] == dragging:

                        value = mouse[0] - (slider["pos"][0] - slider_width / 2)

                        if value < 0: value = 0
                        elif value > slider_width: value = slider_width

                        value /= slider_width
                        slider["value"] = value


            game.screen.fill(game.background_color)

            draw_sliders()
            draw_reset_button()
            draw_music_switcher()
            self.draw_back_button(mouse)

            game.music = audio_settings['main'] * audio_settings['music']
            game.sfx = audio_settings['main'] * audio_settings['sfx']

            pygame.mixer.music.set_volume(game.music)
            game.sfx_channel.set_volume(game.sfx)

            pygame.display.update()


            if not running:
                with open(get_path('settings.json'), 'w') as f:
                    json.dump(settings, f, indent=2)


        


    def gameplay_screen(self):

        with open(get_path('settings.json')) as f:
            settings = json.load(f)

        gameplay_settings = settings["gameplay"]
        controls = settings["controls"]

        slider_width = game.width/1.5
        slider_radius = game.height/80

        sliders = [
            {
                "json name": "das",
                "name": "Delayed Auto Shift",
                "pos": (0, 0),
                "default": 0.8
            },
            {
                "json name": "arr",
                "name": "Auto Repeat Rate",
                "pos": (0, 0),
                "default": 0.85
            },
            {
                "json name": "sds",
                "name": "Soft Drop Speed",
                "pos": (0, 0),
                "default": 0.17
            }
        ]

        def set_slider_pos():
            for i in range(len(sliders)):
                y_pos = (game.height/8 + game.height/16) * (i + 0.5)
                sliders[i]['pos'] = (game.width/2, y_pos)

        set_slider_pos()

        def screen_size_change():
            set_slider_pos()
            reset_button_rect.x = game.width/2-40
            reset_button_rect.y = game.height - 35



        for x in range(len(sliders)):
            sliders[x]["value"] = gameplay_settings[sliders[x]["json name"]]

        def draw_sliders():

            for slider in sliders:
                name, pos, value = slider["name"], slider["pos"], slider["value"]

                text_element = game.big_font.render(name, True, game.foreground_color)
                game.screen.blit(text_element, (pos[0] - text_element.get_rect().width/2, pos[1]))

                pygame.draw.rect(game.screen, game.foreground_color, (pos[0] - slider_width/2, pos[1] + 70, slider_width, 4))
                pygame.draw.circle(game.screen, game.foreground_color, center= ((pos[0]-slider_width/2) + int(value * slider_width), pos[1]+72), radius=slider_radius)

                
                if name == "Delayed Auto Shift":
                    measurement = int(value * 500)
                    measurement = f"{measurement}ms"

                elif name == "Auto Repeat Rate":
                    measurement = 205 - (int(value * 195) + 5)
                    measurement = f"{measurement}ms"

                else:
                    #name == "Soft Drop Speed"
                    measurement = int(value*78) + 2
                    measurement = f"x{measurement}"
                
                
                value_element = game.medium_font.render(measurement, True, game.foreground_color)
                game.screen.blit(value_element, (pos[0] - value_element.get_rect().width/2, pos[1]+90))

        
        piece = Piece((game.width/2)/30 - 3.3, 20, "O")
        def draw_preview():
            text_element = game.big_font.render("Preview", True, game.foreground_color)
            game.screen.blit(text_element, (game.width/2 - text_element.get_rect().width/2, game.height/2+140))

            text_element2 = game.medium_font.render("Move left and right to try it out", True, game.foreground_color)
            game.screen.blit(text_element2, (game.width/2 - text_element2.get_rect().width/2, game.height/2+190))

            piece.render(preview=False)
            

        def can_move(moving):

            if moving == 1 and piece.x < game.width//30 - 5: return True
            elif moving == -1 and piece.x > -1.3: return True
            return False


        reset_button_rect = pygame.Rect(game.width/2-40, game.height - 35, 80, 25)

        def draw_reset_button():

            if reset_button_rect.collidepoint(mouse):
                reset_button_color = tuple(darken(color, 15) for color in game.foreground_color)
            else:
                reset_button_color = game.foreground_color
           
            pygame.draw.rect(game.screen, reset_button_color, reset_button_rect)

            reset_button_text = game.medium_font.render("RESET", True, game.background_color)
            game.screen.blit(reset_button_text, (game.width/2-reset_button_text.get_rect().width/2, reset_button_rect.y))

        running = True
        dragging = None
        moving = 0
        last_move = 0
        das_start = 0
        while running:

            running = start_screen.check_started()

            for slider in sliders:
                gameplay_settings[slider["json name"]] = slider["value"]

            if moving:
                if can_move(moving) and time.time() > das_start:
                    if time.time() > last_move:
                        piece.move(moving, 0)
                        last_move = time.time() + (0.205 - ((gameplay_settings['arr'] * 0.195) + 0.005))

            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()
                    screen_size_change()
                    piece = Piece((game.width/2)/30 - 3.3, 20, "O")
                    slider_width = game.width/1.5
                    slider_radius = game.height/80

                elif event.type == pygame.KEYDOWN:

                    key_name = pygame.key.name(event.key)

                    if key_name == controls['Move Left']:

                        if can_move(-1):
                            moving = -1
                            das_start = max(time.time() + (gameplay_settings['das'] * 0.5), time.time() + 0.205 - ((gameplay_settings['arr'] * 0.195) + 0.005))
                            piece.move(-1, 0)
                    
                    elif key_name == controls['Move Right']:

                        if can_move(1):
                            moving = 1
                            das_start = max(time.time() + (gameplay_settings['das'] * 0.5), time.time() + 0.205 - ((gameplay_settings['arr'] * 0.195) + 0.005))
                            piece.move(1, 0)

                elif event.type == pygame.KEYUP:

                    key_name = pygame.key.name(event.key)

                    if key_name == controls['Move Left']:
                        if moving == -1:
                            moving = 0

                    elif key_name == controls['Move Right']:
                        if moving == 1:
                            moving = 0


                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # back button
                    if start_screen.back_button.collidepoint(event.pos):
                        running = False

                        with open(get_path('settings.json'), 'w') as f:
                            json.dump(settings, f, indent = 2)
                        
                    elif reset_button_rect.collidepoint(mouse):

                        for slider in sliders:

                            slider['value'] = slider['default']

                        with open(get_path('settings.json'), 'w') as f:
                            json.dump(settings, f, indent = 2)

                    elif not dragging:
                        for slider in sliders:
                            x, y = slider["pos"]
                            value = slider["value"]

                            if x - slider_width/2 + int(value * slider_width) - slider_radius < mouse[0] < x - slider_width/2 + int(value * slider_width) + slider_radius and y + 72 - slider_radius < mouse[1] < y + 72 + slider_radius:
                                dragging = slider["name"]
                                break

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

                    if dragging: dragging = None

            if dragging:
                for slider in sliders:
                    if slider["name"] == dragging:

                        value = mouse[0] - (slider["pos"][0] - slider_width / 2)

                        if value < 0: value = 0
                        elif value > slider_width: value = slider_width

                        value /= slider_width
                        slider["value"] = value

            game.screen.fill(game.background_color)

            draw_sliders()
            draw_preview()
            draw_reset_button()
            self.draw_back_button(mouse)
            pygame.display.update()

        #Write to json if loop stopped, meaning they pressed back or game started            
        with open(get_path('settings.json'), 'w') as f:
            json.dump(settings, f, indent = 2)


    
    def pick_themes_screen(self):

        #issue: we need to call setup function for this outside of this function but we cant cause its not a class


        def render_game_preview(bkg_color, fgd_color):
            
            pygame.draw.rect(game.screen, bkg_color, pygame.Rect(0, 0, game.width, game.height))
            pygame.draw.rect(game.screen, fgd_color, new_playing_field_rect)
            self.draw_tetris_pieces(self.pieces)
           
        
            #It was a lot of work to change the start and end position of the blocks, so i just cover them with a rect so look like theyre not going off screen
            pygame.draw.rect(game.screen, bkg_color, pygame.Rect(0, 0, game.width, (game.height - new_playing_field_rect.height)/2))
            pygame.draw.rect(game.screen, bkg_color, pygame.Rect(0, new_playing_field_rect.y + new_playing_field_rect.height, game.width, (game.height - new_playing_field_rect.height)))



        def is_dark(rgb):
            
            r, g, b = rgb
            cutoff = 30
            if r < cutoff and g < cutoff and b < cutoff:
                return True


        def draw_arrows(mouse):
            dark = False
            if is_dark(game.background_color):
                dark = True

            #hover effect
            if left_arrow_rect.collidepoint(mouse):
                
                if dark:
                    new_left_arrow = left_arrow
                    new_left_arrow_rect = new_left_arrow.get_rect(center = (left_arrow_pos[0] + dimensions/2, left_arrow_pos[1] + dimensions/2))
                    new_left_arrow_rect_color = tuple(darken(i, 15) for i in game.foreground_color)
               
            
                else:
                    new_left_arrow = pygame.transform.scale(left_arrow, (int(dimensions * hover_scale_factor), int(dimensions * hover_scale_factor)))
                    new_left_arrow_rect = new_left_arrow.get_rect(center = (left_arrow_pos[0] + dimensions/2, left_arrow_pos[1] + dimensions/2))
                    new_left_arrow_rect_color = game.foreground_color

            else:
                new_left_arrow = left_arrow
                new_left_arrow_rect = left_arrow_rect
                new_left_arrow_rect_color = game.foreground_color


            if right_arrow_rect.collidepoint(mouse):

                if dark:
                    new_right_arrow = right_arrow
                    new_right_arrow_rect = new_right_arrow.get_rect(center = (right_arrow_pos[0] + dimensions/2, right_arrow_pos[1] + dimensions/2))
                    new_right_arrow_rect_color = tuple(darken(i, 15) for i in game.foreground_color)
                
                
                
                else:
                    new_right_arrow = pygame.transform.scale(right_arrow, (int(dimensions * hover_scale_factor), int(dimensions * hover_scale_factor)))
                    new_right_arrow_rect = new_right_arrow.get_rect(center = (right_arrow_pos[0] + dimensions/2, right_arrow_pos[1] + dimensions/2))
                    new_right_arrow_rect_color = game.foreground_color

            else:
                new_right_arrow = right_arrow
                new_right_arrow_rect = right_arrow_rect
                new_right_arrow_rect_color = game.foreground_color
            

            if dark:
                pygame.draw.rect(game.screen, new_left_arrow_rect_color, new_left_arrow_rect)
                pygame.draw.rect(game.screen, new_right_arrow_rect_color, new_right_arrow_rect)

            game.screen.blit(new_left_arrow, left_arrow_pos)
            game.screen.blit(new_right_arrow, right_arrow_pos)

        def change_theme():
            theme = game.themes[game.theme_index]
            game.theme_text = theme[0]
            background_color = theme[1]
            foreground_color = theme[2]
            game.foreground_color = foreground_color
            game.background_color = background_color
            game.set_grid_color(foreground_color)
            game.set_text_color(foreground_color)
            self.set_buttons_color(foreground_color)
            self.background_color = background_color

            #we need a seperate var because if we rely on theme text, then once we change the theme (since its random), it will no longer think its random
            if game.theme_text == 'Random':
                game.random_theme = True
            
            else:
                game.random_theme = False

        
        def next_theme(direction):
            #direction 0 = left, 1 = right
            themes_len = len(game.themes)

            if direction and game.theme_index >= themes_len - 1:
                val = 0
                game.theme_index = 0

            elif direction:
                val = 1
            
            elif game.theme_index <= 0:
                val = 0
                game.theme_index = themes_len - 1
            
            else:
                val = -1

            game.theme_index += val

            change_theme()


        rgb_stage = 0

        r, g, b = 255, 0, 0

        def cycle_colors():
            
            nonlocal r, g, b, rgb_stage

            if rgb_stage == 0:
                if g < 255 and r > 0:
                    g += 1
                    r -= 1
                else:
                    rgb_stage = 1


            elif rgb_stage == 1:
                if b < 255 and g > 0:
                    b += 1
                    g -= 1
                    
                else:
                    rgb_stage = 2

            elif rgb_stage == 2:
                if r < 255 and b > 0:
                    r += 1
                    b -= 1
                else:
                    rgb_stage = 0


    
        def draw_title():

            title = game.very_big_medium_font.render(game.theme_text, True, game.foreground_color)
            title_rect = title.get_rect()
            game.screen.blit(title, (game.width/2 - title_rect.width/2, 10))
            
        def store_theme():
            with open(get_path('settings.json')) as f:
                full_dict = json.load(f)

            full_dict['theme'] = game.theme_index

            with open(get_path('settings.json'), 'w') as f:
                json.dump(full_dict, f, indent = 2)
            
        def random_theme():
        
            if game.random_theme:
                if not randint(0, 2):
                    cycle_colors()

                text = game.enormous_font.render('?', True, (game.background_color))
                text_rect = text.get_rect(center = (new_playing_field_rect.x + new_playing_field_rect.width/2, new_playing_field_rect.y + new_playing_field_rect.height/2))
                game.screen.blit(text, text_rect)

        
        offset = 10
        left_arrow = pygame.image.load(get_path('assets/images/left_arrow.png'))
        dimensions = left_arrow.get_height()
        left_arrow_pos = (offset, game.height/2 - dimensions/2)
        right_arrow_pos =  (game.width - dimensions - offset, game.height/2 - dimensions/2)
        right_arrow = pygame.image.load(get_path('assets/images/right_arrow.png'))
        left_arrow_rect = left_arrow.get_rect(center = (left_arrow_pos[0] + dimensions/2, left_arrow_pos[1] + dimensions/2))
        right_arrow_rect = right_arrow.get_rect(center = (right_arrow_pos[0] + dimensions/2, right_arrow_pos[1] + dimensions/2))
        hover_scale_factor = 1.1
        new_playing_field_rect =  pygame.Rect(game.width/2 - game.playing_field_rect.width/2, game.playing_field_rect.y, game.playing_field_rect.width, game.playing_field_rect.height)
        min_x = int(new_playing_field_rect.x/30)
        max_x = min_x + int(new_playing_field_rect.width/30) - 5 
        max_y = int(new_playing_field_rect.height/30)
        step_y = int(max_y/5) or 1
        step_x = 1
        #It might seem confusing whats happeneing here but dw about it, just making sure blocks are spaced out
        x_pos = list(range(min_x, max_x, step_x))
        y_pos = list(range(0, max_y, step_y)) 

        shuffle(x_pos)


        self.pieces = [

            Piece(x_pos, y_pos, choice(start_screen.piece_types)) for x_pos, y_pos in zip(x_pos, y_pos)
           
        ]

        self.last_falls = [time.time() for _ in self.pieces]


        running = True
        while running:
            #bkg color

            mouse = pygame.mouse.get_pos()
    
            #Makes sure that if game starts while were in this screen it goes back to game
            running = start_screen.check_started()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()
                    left_arrow_pos = (offset, game.height/2 - dimensions/2)
                    right_arrow_pos =  (game.width - dimensions - offset, game.height/2 - dimensions/2)
                    left_arrow_rect = left_arrow.get_rect(center = (left_arrow_pos[0] + dimensions/2, left_arrow_pos[1] + dimensions/2))
                    right_arrow_rect = right_arrow.get_rect(center = (right_arrow_pos[0] + dimensions/2, right_arrow_pos[1] + dimensions/2))
                    new_playing_field_rect =  pygame.Rect(game.width/2 - game.playing_field_rect.width/2, game.playing_field_rect.y, game.playing_field_rect.width, game.playing_field_rect.height)
                    min_x = int(new_playing_field_rect.x/30)
                    max_x = min_x + int(new_playing_field_rect.width/30) - 5
                    max_y = int(new_playing_field_rect.height/30)
                    step_y = int(max_y/5) or 1
                    step_x = 1

                    x_pos = list(range(min_x, max_x, step_x))

                    y_pos = list(range(0, max_y, step_y))
                    shuffle(x_pos)


                    self.pieces = [

                        Piece(x_pos, y_pos, choice(start_screen.piece_types)) for x_pos, y_pos in zip(x_pos, y_pos)
                    
                    ]

                    self.last_falls = [time.time() for _ in self.pieces]

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_screen.back_button.collidepoint(event.pos):
                        store_theme()
                        running = False

                    elif left_arrow_rect.collidepoint(event.pos):
                        next_theme(0)


                    elif right_arrow_rect.collidepoint(event.pos):
                        next_theme(1)

            render_game_preview(game.background_color, (r, g, b) if game.random_theme else game.foreground_color)
            random_theme()
            draw_title()
            self.draw_back_button(mouse)
            draw_arrows(mouse)
            pygame.display.update()
        
        game.check_random_theme()


    
    def pick_controls_screen(self):


        def draw_controls(controls, pos, color, keys_bkg_color = (0, 0, 0), value_bkg_color = self.background_color, underline = False, clicked_index = -1):
        
            replace_keys = {
                'left click': 'lmb',
                'middle click': 'mmb',
                'right click': 'rmb',
                'up': '↑',
                'down': '↓',
                'right': '→',
                'left': '←',
                'left shift': 'lshft',
                'right shift': 'rshft',
                'caps lock': 'caps',
                'return': 'entr',
                'left ctrl': 'lctrl',
                'right ctrl': 'rctrl',
                'left meta': 'wn',
                'right meta': 'wn',
                'left alt': 'lalt',
                'right alt': 'ralt',
                'compose': 'cmp',
                'space': 'spc',
                'escape': 'esc',
                'print screen': 'prnt',
                'scroll lock': 'scrl',
                'break': 'brk',
                'insert': 'insrt',
                'page up': 'pup',
                'page down': 'pdwn',
                'backspace': 'bksp',

            }

            
            text_rects = []
        
        
            #pos 0 = left side, 1 = right side
            for index, values in enumerate(controls):
                description, key = values
                modified_key = replace_keys[key].upper() if key in replace_keys.keys() else key.upper()
                text_1 = game.big_font.render(modified_key, True, (0, 0, 0))
                text_2 = game.medium_font.render(f" = {description}", True, color)
                text_2_rect = text_2.get_rect()
                text_2_rect.center = ((200 if pos == 0 else game.width - 150), (index * 50) + 450)
                text_1_rect = text_1.get_rect()
                text_1_rect.center = (text_2_rect.x - text_1_rect.width/2, text_2_rect.y + 10)
    
                                                #Dw about mechanics of this, just know that This just toggles True/False every half a second
                if underline and index == clicked_index and int(str(round(time.time(), 1))[-1:]) < 5:
                        pygame.draw.rect(game.screen, (255, 255, 255), pygame.Rect(text_1_rect.x, text_1_rect.y + 2, text_1_rect.width, text_1_rect.height + 2))
            

                pygame.draw.rect(game.screen, value_bkg_color, text_1_rect)
                pygame.draw.rect(game.screen, keys_bkg_color, text_2_rect)
                game.screen.blit(text_1, (text_1_rect.x, text_1_rect.y))
                game.screen.blit(text_2, (text_2_rect.x, text_2_rect.y))

                text_rects.append(text_1_rect)


            return text_rects


        def get_keys_bkg_color(color: tuple):
            
            darkened = tuple(darken(i, 30) for i in color)
            
            r, g, b  = darkened

            if r <= 10 and g <= 10 and b <= 10:
                return tuple(lighten(i, 30) for i in color)
            
            return darkened
    
            

        def key_exists_err():
            text = game.big_font.render('KEY ALREADY IN USE', True, (255, 0, 0))
            text_rect = text.get_rect(center = (game.width/2, game.height/2 - 100))
            start_time = time.time()
            while time.time() - start_time <= 0.5:

                for event in pygame.event.get():

                    if event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                        try: 
                            game.width, game.height = event.w, event.h
                        except:
                            pass
                        game.resize_all_screens()

                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                        
                game.screen.blit(text, (text_rect.x, text_rect.y))
                pygame.display.update()

        def draw_reset_button(mouse):
            inital_color = self.buttons_color
            color = tuple(darken(i, 15) for i in inital_color) if reset_button.collidepoint(mouse) else inital_color
            pygame.draw.rect(game.screen, color, reset_button)
            game.screen.blit(reset_text, (game.width/2 - 50 + 20,  game.height - 45 + 12))
        
        
        
        def reset_controls():
            with open(get_path('settings.json')) as f:
                full_dict = json.load(f)

            full_dict['controls'] = game.default_controls

            with open(get_path('settings.json'), 'w') as f:
                json.dump(full_dict, f, indent=2)


            game.left_controls = {
                    
                "Move Left": game.default_controls["Move Left"],
                "Move Right": game.default_controls["Move Right"],
                "Soft Drop": game.default_controls["Soft Drop"],
                "Toggle Movement": game.default_controls["Toggle Movement"],
                "Toggle Music": game.default_controls["Toggle Music"]

            }
           
            game.right_controls = {
                    "Rotate Clockwise": game.default_controls["Rotate Clockwise"],
                    "Rotate Counter-Clockwise": game.default_controls["Rotate Counter-Clockwise"],
                    "Hold Piece": game.default_controls["Hold Piece"],
                    "Hard Drop": game.default_controls["Hard Drop"],
                    "Toggle Fullscreen": game.default_controls["Toggle Fullscreen"]
            }

            game.fullscreen_key = full_dict["controls"]["Toggle Fullscreen"]


        def draw_title():
            game.screen.blit(title_text_1, (game.width/2 - 140, 100))
            game.screen.blit(title_text_2, (game.width/2 - 200, 160))
        
        def draw_prompt():
            if clicked:
                color = self.buttons_color if int(str(round(time.time(), 1))[-1:]) < 5 else game.background_color
                prompt_text = game.big_font.render('PRESS A KEY', True, color)
                game.screen.blit(prompt_text, (game.width/2 - 100, 300))

        mouse_number_key = {
            1: 'left click',
            2: 'middle click',
            3: 'right click'
        }

        def get_key_input(key, mouse_clicked = False):

            if not mouse_clicked:
                key = pygame.key.name(key)

            else:
                key = mouse_number_key[key]


            keys = list(list(game.left_controls.values()) + list(game.right_controls.values()))

            if clicked_index_1 >= 0:
                
                if key not in keys:
                    game.left_controls[list(game.left_controls.keys())[clicked_index_1]] = key

                else:
                    key_exists_err()

            elif clicked_index_2 >= 0:
                if key not in keys:
                    game.right_controls[list(game.right_controls.keys())[clicked_index_2]] = key
                
                else:
                    key_exists_err()

            with open(get_path('settings.json')) as f:
                full_dict = json.load(f)

            full_controls = dict(game.left_controls, **game.right_controls)
            full_dict['controls'] = full_controls
            
            with open(get_path('settings.json'), 'w') as f:
                json.dump(full_dict, f, indent=2)

            game.fullscreen_key = full_dict["controls"]["Toggle Fullscreen"]
        

        title_text_1 = game.big_font.render('CLICK ON A BOX TO', True, (255, 255, 255))
        title_text_2 = game.big_font.render('CHANGE YOUR CONTROLS', True, (255, 255, 255))
        reset_text = game.medium_font.render('RESET', True, (0, 0, 0))
        text_boxes_1 = []
        text_boxes_2 = []
        clicked = False
        clicked_index_1 = -1
        clicked_index_2 = -1
        reset_button = pygame.Rect(game.width/2 - 50, game.height - 35, 100, 27)
    
        running = True
        while running:
            #bkg color
            game.screen.fill(game.background_color)

            mouse = pygame.mouse.get_pos()
            
            #Makes sure that if game starts while were in this screen it goes back to game
            running = start_screen.check_started()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()
                    

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if clicked:
                        if 1 <= event.button <= 3:
                            get_key_input(event.button, mouse_clicked=True)
                            clicked = False
                            
                    elif event.button == 1:
 
                        if start_screen.back_button.collidepoint(event.pos):
                            running = False

                        elif reset_button.collidepoint(event.pos):
                            reset_controls()

                        else:
                            for index, text_box in enumerate(text_boxes_1):
                                if text_box.collidepoint(event.pos):
                                    clicked = True
                                    clicked_index_2 = -1
                                    clicked_index_1 = index
                                


                            for index, text_box in enumerate(text_boxes_2):
                                if text_box.collidepoint(event.pos):
                                    clicked = True
                                    clicked_index_1 = -1
                                    clicked_index_2 = index
                        

                elif event.type == pygame.KEYDOWN:
                    if clicked:
                        get_key_input(event.key)
                    
                    clicked = False


            reset_button = pygame.Rect(game.width/2 - 50, game.height - 35, 100, 27)
            self.draw_back_button(mouse)
            draw_reset_button(mouse)

            draw_title()
            draw_prompt()

            keys_bkg_color = get_keys_bkg_color(game.background_color)
            text_boxes_1 = draw_controls(game.left_controls.items(), 0, (255, 255, 255), keys_bkg_color = keys_bkg_color, value_bkg_color = self.buttons_color, underline = clicked, clicked_index = clicked_index_1)
            text_boxes_2 = draw_controls(game.right_controls.items(), 1,  (255, 255, 255),  keys_bkg_color = keys_bkg_color, value_bkg_color = self.buttons_color, underline = clicked, clicked_index = clicked_index_2)
            pygame.display.update()
    

    def draw_buttons(self):

        for button, text, color, _ in self.buttons:
            pygame.draw.rect(game.screen, color, button)
            text_rect = text.get_rect(center = (button.x + button.width/2, button.y +button.height/2))
            game.screen.blit(text, text_rect)
        

       

    def buttons_hover(self, mouse):
        for index, button in enumerate(self.buttons):
              
            if button[0].collidepoint(mouse):
                                                                #2 is the color index
                self.buttons[index][2] = tuple(darken(i, 20) for i in self.buttons_color)
            
            else:
                self.buttons[index][2] = self.buttons_color


    def main(self):
        running = True
        while running:
            #bkg color
            game.screen.fill(game.background_color)
            mouse = pygame.mouse.get_pos()
            #Makes sure that if game starts while were in this screen it goes back to game
            running = start_screen.check_started()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                    try: 
                        game.width, game.height = event.w, event.h
                    except:
                        pass
                    game.resize_all_screens()


                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    
                    for button, _, _, func in self.buttons:
                        if button.collidepoint(event.pos):
                            func()

                    if start_screen.back_button.collidepoint(event.pos):
                        running = False


            self.buttons_hover(mouse)
            self.draw_back_button(mouse)
            self.draw_buttons()
            pygame.display.update()
            game.clock.tick(60)


class Block(Game):

    def __init__(self, x, y, color, colorByName = True):

        self.x, self.y = x, y

        if colorByName:
            self.color = color_key[color]
        else:
            self.color = color

        self.size = 30


        self.flash_start = 0
        self.direction = 0
        self.fade_start = 0


        
    
    def render(self, offset = True):
        
        
        x_offset_val = game.playing_field_rect.x if offset else 100
        
        # normal
        if time.time() > self.flash_start + 0.2 and not self.fade_start:

            darker = tuple(darken(i) for i in self.color)
            block_rect = pygame.Rect((self.x-1) * self.size + x_offset_val, (self.y-1)* self.size + game.block_y_offset, 30, 30)
            pygame.draw.rect(game.screen, self.color, block_rect)
            game.draw_block_borders(block_rect, darker)

        
        # flashing
        elif time.time() <= self.flash_start + 0.2:

            flash_time = self.flash_start + 0.2 - time.time()

            flash_color = []

            # whether it flashes dark or light
            direction = self.direction

            # orange, blue, purple flashes light
            if flash_time >= 0.1:
                direction *= -1

            for color in self.color:

                color = color + (flash_time * 270 * direction)
                
                if color > 255: color = 255
                elif color < 0: color = 0

                flash_color.append(color)

            flash_color = tuple(flash_color)

            darker = tuple(darken(i) for i in flash_color)
            block_rect = pygame.Rect((self.x-1) * self.size + game.playing_field_rect.x, (self.y-1)* self.size + game.block_y_offset, 30, 30)
            game.draw_block_borders(block_rect, darker)
            pygame.draw.rect(game.screen, flash_color, block_rect)
            pygame.draw.rect(game.screen, flash_color, ((self.x-1) * self.size + game.playing_field_rect.x + 5, (self.y-1)* self.size + game.block_y_offset + 5, 20, 20))


        # fading
        else:
            fade_time = self.fade_start + 0.5 - time.time()

            if fade_time > 0:
                color_difference = [255 - color for color in self.color]

                fade_color = []
                for x in range(3):
                    fade_color.append((color_difference[x] / 0.5 * (0.5 - fade_time)) + self.color[x])
                fade_color = tuple(fade_color)
           
            else:
                fade_color = (255, 255, 255)

            
            darker = tuple(darken(i) for i in fade_color)
            block_rect = pygame.Rect((self.x-1) * self.size + game.playing_field_rect.x, (self.y-1)* self.size + game.block_y_offset, 30, 30)
            game.draw_block_borders(block_rect, darker)
            pygame.draw.rect(game.screen, fade_color, ((self.x-1) * self.size + game.playing_field_rect.x + 5, (self.y-1)* self.size + game.block_y_offset + 5, 20, 20))


    # for putting blocks on second screen
    def render_second(self):
        darker = tuple(darken(i) for i in self.color)
        block_rect = pygame.Rect((self.x-1) * self.size/2 + 570 + game.block_x_offset, (self.y-1)* self.size/2 + game.second_block_y_offset, 15, 15)
        pygame.draw.rect(game.screen, self.color, block_rect)
        game.draw_block_borders(block_rect, darker, block_size_difference = 2)


    def render_preview(self):
        pygame.draw.rect(game.screen, game.preview_color, ((self.x-1) * self.size + game.playing_field_rect.x, (self.y-1)* self.size + game.block_y_offset, 30, 30))
        pygame.draw.rect(game.screen, game.foreground_color, ((self.x-1) * self.size + game.playing_field_rect.x + 3, (self.y-1)* self.size + game.block_y_offset + 3, 24, 24))


        
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

    def flash(self):

        if self.piece_type in ("L", "J", "T"):
            direction = -1
        else:
            direction = 1

        for block in self.blocks:
            block.direction = direction
            block.flash_start = time.time()


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


    def _path_check(self, direct, x, y, play_sound = True):

        # invert y direction
        y *= -1

        self.move(x, y)

        if not self.check_overlap():
            if play_sound:
                game.play_sound('correct rotate')
            return True

        # reset
        self.move(-1*x, -1*y)
        
        return False

        



    #0 means clockwise, 1 means counterclockwise
    def rotate(self, direct: int, play_sound = True):
       

        if self.piece_type == "O": return game.play_sound('correct rotate') if play_sound else None

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
                        if self._path_check(direct, -2, 0, play_sound): return
                        if self._path_check(direct, 1, 0, play_sound): return
                        if self._path_check(direct, -2, -1, play_sound): return
                        if self._path_check(direct, 1, 2, play_sound): return


                    # R -> 2
                    elif old_rotation == 'R':
                        if self._path_check(direct, -1, 0, play_sound): return
                        if self._path_check(direct, 2, 0, play_sound): return
                        if self._path_check(direct, -1, 2, play_sound): return
                        if self._path_check(direct, 2, -1, play_sound): return
                    
                    # 2 -> L
                    elif old_rotation == '2':
                        if self._path_check(direct, 2, 0, play_sound): return
                        if self._path_check(direct, -1, 0, play_sound): return
                        if self._path_check(direct, 2, 1, play_sound): return
                        if self._path_check(direct, -1, -2, play_sound): return

                    # L -> 0
                    elif old_rotation == "L":
                        if self._path_check(direct, 1, 0, play_sound): return
                        if self._path_check(direct, -2, 0, play_sound): return
                        if self._path_check(direct, 1, -2, play_sound): return
                        if self._path_check(direct, -2, 1, play_sound): return


                # counterclockwise
                else:

                    # R -> 0
                    if old_rotation == "R":
                        if self._path_check(direct, 2, 0, play_sound): return
                        if self._path_check(direct, -1, 0, play_sound): return
                        if self._path_check(direct, 2, 1, play_sound): return
                        if self._path_check(direct, -1, -2, play_sound): return

                    # 2 -> R
                    elif old_rotation == "2":
                        if self._path_check(direct, 1, 0, play_sound): return
                        if self._path_check(direct, -2, 0, play_sound): return
                        if self._path_check(direct, 1, -2, play_sound): return
                        if self._path_check(direct, -2, 1, play_sound): return

                    # L -> 2
                    elif old_rotation == "L":
                        if self._path_check(direct, -2, 0, play_sound): return
                        if self._path_check(direct, 1, 0, play_sound): return
                        if self._path_check(direct, -2, -1, play_sound): return
                        if self._path_check(direct, 1, 2, play_sound): return
                    
                    # 0 -> L
                    elif old_rotation == "0":
                        if self._path_check(direct, -1, 0, play_sound): return
                        if self._path_check(direct, 2, 0, play_sound): return
                        if self._path_check(direct, -1, 2, play_sound): return
                        if self._path_check(direct, 2, -1, play_sound): return



            else:

                # clockwise
                if direct == 0:

                    
                    # 0 -> R
                    if old_rotation == "0":
                        if self._path_check(direct, -1, 0, play_sound): return
                        if self._path_check(direct, -1, 1, play_sound): return
                        if self._path_check(direct, 0, -2, play_sound): return
                        if self._path_check(direct, -1, -2, play_sound): return


                    # R -> 2
                    elif old_rotation == 'R':
                        if self._path_check(direct, 1, 0, play_sound): return
                        if self._path_check(direct, 1, -1, play_sound): return
                        if self._path_check(direct, 0, 2, play_sound): return
                        if self._path_check(direct, 1, 2, play_sound): return
                    
                    # 2 -> L
                    elif old_rotation == '2':
                        if self._path_check(direct, 1, 0, play_sound): return
                        if self._path_check(direct, 1, 1, play_sound): return
                        if self._path_check(direct, 0, -2, play_sound): return
                        if self._path_check(direct, 1, -2, play_sound): return

                    # L -> 0
                    elif old_rotation == "L":
                        if self._path_check(direct, -1, 0, play_sound): return
                        if self._path_check(direct, -1, -1, play_sound): return
                        if self._path_check(direct, 0, 2, play_sound): return
                        if self._path_check(direct, -1, 2, play_sound): return


                # counterclockwise
                else:

                    # R -> 0
                    if old_rotation == "R":
                        if self._path_check(direct, 1, 0, play_sound): return
                        if self._path_check(direct, 1, -1, play_sound): return
                        if self._path_check(direct, 0, 2, play_sound): return
                        if self._path_check(direct, 1, 2, play_sound): return

                    # 2 -> R
                    elif old_rotation == "2":
                        if self._path_check(direct, -1, 0, play_sound): return
                        if self._path_check(direct, -1, 1, play_sound): return
                        if self._path_check(direct, 0, -2, play_sound): return
                        if self._path_check(direct, -1, -2, play_sound): return

                    # L -> 2
                    elif old_rotation == "L":
                        if self._path_check(direct, -1, 0, play_sound): return
                        if self._path_check(direct, -1, -1, play_sound): return
                        if self._path_check(direct, 0, 2, play_sound): return
                        if self._path_check(direct, -1, 2, play_sound): return
                    
                    # 0 -> L
                    elif old_rotation == "0":
                        if self._path_check(direct, 1, 0, play_sound): return
                        if self._path_check(direct, 1, 1, play_sound): return
                        if self._path_check(direct, 0, -2, play_sound): return
                        if self._path_check(direct, 1, -2, play_sound): return
            

            # if all tests fail
            self.rotation = old_rotation
            
            # reset
            for index, block in enumerate(self.blocks):
                block.x, block.y = org_block_coords[index]

            if self.piece_type == "T":
                for index, coords in enumerate(self.corners.values()):
                    coords = org_corner_coords[index] #type: ignore
  

        elif play_sound:
            game.play_sound('correct rotate')
            
            
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
        if preview:
            downCount = 0

            while not self.check_floor():
                self.move(0, 1)
                downCount += 1
            self.move(0, -1)
            
            for block in self.blocks:
                block.render_preview()
            
            for _ in range(downCount):
                self.move(0, -1)

            self.move(0, 1)
            
        # for actual piece
        for block in self.blocks:
            block.render(preview)


start_screen = StartScreen()
settings_screen = SettingsScreen()