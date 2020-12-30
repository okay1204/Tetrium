import sys
import traceback

from pygame.display import toggle_fullscreen
from oooooooooooooooooooooooooooooooooooooooooooootils import get_path

def error_handler(e_type, value, tb):

    error = traceback.format_exception(e_type, value, tb)
    text = "".join(error)

    print(text)

    with open(get_path('logs.txt'), 'a') as f:
        f.write(f"{text}\n\n\n")


sys.excepthook = error_handler



# pylint: disable=no-member, unused-wildcard-import
import pygame
from game import *
import time
import random
import json
import _thread
import socket
import onlineGame




pieces = ["T", "L", "J", "S", "Z", "I", "O"]

bag = pieces.copy()
random.shuffle(bag)
next_bag = pieces.copy()
random.shuffle(next_bag)

def stop():

    game.running = False

    if game.multiplayer:
        
        while True:
            if can_disconnect:
                game.n.disconnect()
                break

    pygame.quit()
    sys.exit()


def render_texts():

    # queing up special texts
    removed_texts = []
    for text, display_time, size in texts:

        if display_time > time.time():

            font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), size)

            original = text

            if isinstance(text, str):
                text = text,

            textElements = []
            for line in text:
                textElement = font.render(line, True, game.foreground_color)
                textRect = textElement.get_rect()

                textElements.append((textElement, textRect))

            for index, element in enumerate(textElements):
                textElement, textRect = element

                textRect.center = (
                    game.playing_field_rect.x + 350, game.playing_field_rect.y + 400 + (texts.index((original, display_time, size)) * 50) + (index * 25))

                game.screen.blit(textElement, textRect)

        else:
            removed_texts.append((text, display_time, size))

    for item in removed_texts:
        texts.remove(item)
    
    removed_texts.clear()


def pick_bag():
    global bag, next_bag

    value = bag.pop(0)

    if not next_bag:
        next_bag = pieces.copy()
        random.shuffle(next_bag)

    bag.append(next_bag.pop(0)) 

    return value


fall_speed = 1
last_fall = time.time() + fall_speed
fall = 0

current = None

speedUp = False

avoids = 0

held = ''


display_until = 0

canSwitch = True

gameOver = False

chat = []


def reset():
    global bag, next_bag, avoids, current, held, canSwitch, moving, fall_speed, speedUp, difficult_before

    game.resting.clear()
    game.rows_cleared.clear()
    game.level = 1
    game.score = 0
    game.lines = 0
    bag = pieces.copy()
    random.shuffle(bag)
    next_bag = pieces.copy()
    random.shuffle(next_bag)
    avoids = 0
    current = None
    held = None
    canSwitch = True
    moving = 0
    game.meter.clear()
    fall_speed = 1
    speedUp = False
    difficult_before = False


opp_disconnected_after = False
opp_rematched = False

def game_over(win: bool):

    global gameOver, opp_disconnected_after

    game_over_start = time.time()

    gameOver = True

    button_dimensions = (250, 40)
    button_pos = (
        int(game.width/2 - button_dimensions[0]/2), int(game.height/2))

    menu_button_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 32)
    menu_button_rect = pygame.Rect(button_pos, button_dimensions)
    menu_button_color = game.foreground_color
    menu_button_text = menu_button_font.render(
        'Return to menu', True, game.background_color)
    game_over_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 50)

    rematch_text_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 40)
    self_rematch_text = opp_rematch_text = "Deciding..."
    
    rematch_active = True

    rematch_button_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 26)

    if game.multiplayer:
        rematch_button_text = rematch_button_font.render('Rematch', True, game.background_color)
        rematch_button_dimensions = (120, 40)
    else:
        rematch_button_text = rematch_button_font.render('Retry', True, game.background_color)
        rematch_button_dimensions = (80, 40)


    rematch_button_pos = (int(game.width/2 - rematch_button_dimensions[0]/2), int(game.height/2)+150)
    rematch_button_rect = pygame.Rect(rematch_button_pos, rematch_button_dimensions)
    rematch_button_color = game.foreground_color


    text_font = pygame.font.Font(get_path('assets/fonts/arial.ttf'), 25)
    you_text = text_font.render("You", True, game.foreground_color)
    opponent_text = text_font.render(game.opp_name, True, game.foreground_color)
    opponent_rect = opponent_text.get_rect(center=((game.width/4)*3, int(game.height/2)+100+opponent_text.get_rect().height/2))
    
    input_box_width = 300
    input_box_height = 50
    input_box_x = (game.width - input_box_width)/2
    input_box_y =  game.height/2 - 85
    input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
    input_box_bkg = pygame.Rect((game.width - input_box_width)/2 , game.height/2 - 85, input_box_width, input_box_height)

    if game.multiplayer:
        if not win:
            send('game over')
            game_over_text = game_over_font.render('You lost...', True, game.foreground_color)

            game.update_presence(
                details=f"In End Screen",
                state=f"Lost to {game.opp_name}",
                start=game.time_started,
                large_image="tetrium"
            )

        else:
            game_over_text = game_over_font.render('You win!', True, game.foreground_color)

            game.update_presence(
                details=f"In End Screen",
                state=f"Won against {game.opp_name}",
                start=game.time_started,
                large_image="tetrium"
            )

    else:
        game_over_text = game_over_font.render('Game over', True, game.foreground_color)

        score_text = game.big_font.render(f'Score: {game.score}', True, game.foreground_color)
        lines_text = game.big_font.render(f'Lines Cleared: {game.lines}', True, game.foreground_color)
        level_text = game.big_font.render(f'Level: {game.level}', True, game.foreground_color)

        game.update_presence(
            details=f"In End Screen",
            state=f"Singleplayer; Score: {game.score}",
            start=game.time_started,
            large_image="tetrium"
        )


    textRect = game_over_text.get_rect()
    textRect.center = (game.width // 2, 200)

    def draw_menu_button():

        pygame.draw.rect(game.screen, menu_button_color,
                         menu_button_rect)
        game.screen.blit(menu_button_text,
                         (button_pos[0] + 10, button_pos[1] + 3))


    def draw_rematch_button():
        pygame.draw.rect(game.screen, rematch_button_color, rematch_button_rect)
        game.screen.blit(rematch_button_text, (rematch_button_pos[0]+10, rematch_button_pos[1]+4))

    def draw_self_rematch_text():
        
        self_rendered_text = rematch_text_font.render(self_rematch_text, True, game.foreground_color)
        game.screen.blit(self_rendered_text, (int(game.width/4)-100, int(game.height/2)+250))


        opp_rendered_text = rematch_text_font.render(opp_rematch_text, True, game.foreground_color)
        game.screen.blit(opp_rendered_text, (opponent_rect.x -  0.75 * opponent_rect.width, int(game.height/2)+250))

    def draw_texts():
        game.screen.blit(you_text, (int(game.width/4)-30, int(game.height/2)+100))

        game.screen.blit(opponent_text, opponent_rect)

    def draw_stats():

        game.screen.blit(score_text, (game.width // 2 - score_text.get_rect().width//2, 240))
        game.screen.blit(lines_text, (game.width // 2 - lines_text.get_rect().width//2, 290))
        game.screen.blit(level_text, (game.width // 2 - level_text.get_rect().width//2, 340))


    def draw_chat():
        for idx, msg in enumerate(chat):
            text_render = game.small_font.render(msg, True, game.foreground_color)
            game.screen.blit(text_render, (game.width/2 - 100, 100 + 50 * (idx + 1)))

    def send_text(text):
        send(f"chat {text}")
        chat.append(f"me {text}")
        return ''

    def draw_chat_box(message, active):
        if active:
            input_bkg_color = (0, 0, 255)

        else:
            input_bkg_color = (0, 0, 0)

        pygame.draw.rect(game.screen, input_bkg_color, input_box, 10)
        pygame.draw.rect(game.screen, (255,255,255), input_box_bkg)

        message_render = game.medium_font.render(message, True, game.background_color) if message else game.small_font.render("send a message", True, game.foreground_color)
        game.screen.blit(message_render, (input_box.x + 5, input_box.y + 6))
        return message_render.get_rect().width

    def get_input(text, text_width):
        return text

    message_text = ''
    mressage_text_width = 0
    input_active = False

    while gameOver:

        game.screen.fill(game.background_color)


        if opp_disconnected_after:
            opp_rematch_text = "Disconnected"

        elif opp_rematched:
            opp_rematch_text = "Rematching..."


        mouse = pygame.mouse.get_pos()
        held_key = ""
        held_unicode = ""
        held_time = 0


        # Game over loop

        for event in pygame.event.get():


            # NOTE this if statement is temporary, in order to send a chat message
            # used the send() and chat.append() functions where text is the message to send
            # the list, chat, is a list of messages that start with "me" or "opp"
            # if it starts with "me", then it is by this client, if its "opp" the message is by the opponent
            if event.type == pygame.KEYDOWN:
   
                #sending message
                if message_text and event.key == pygame.K_RETURN:
                    message_text = send_text(message_text)
                    
                if input_active:
                    if event.key == pygame.K_BACKSPACE:
                        message_text = message_text[:-1]

                    else:
                        message_text += get_input(event.unicode, mressage_text_width)
                    
                    if held_key != pygame.key:
                        held_time = time.time() + 0.5
                    
                        held_key = event.key
                        
                        if event.key == pygame.K_BACKSPACE:
                            held_unicode = "backspace"

                        else:
                            held_unicode = event.unicode

            elif event.type == pygame.KEYUP:

                held_time = time.time() + 0.5

                if event.key == held_key:
                    held_key = ""
                    held_unicode = ""
                

            elif event.type == pygame.QUIT:
                stop()

            elif event.type == pygame.VIDEORESIZE or game.check_fullscreen(event):
                try:
                    game.width, game.height = event.w, event.h
                except: pass
                game.resize_all_screens()
                button_pos = (
                    int(game.width/2 - button_dimensions[0]/2), int(game.height/2))
                menu_button_rect = pygame.Rect(button_pos, button_dimensions)
                menu_button_color = game.foreground_color
                menu_button_text = menu_button_font.render(
                    'Return to menu', True, game.background_color)
                rematch_button_pos = (int(game.width/2 - rematch_button_dimensions[0]/2), int(game.height/2)+150)
                rematch_button_rect = pygame.Rect(rematch_button_pos, rematch_button_dimensions)
                opponent_rect = opponent_text.get_rect(center=((game.width/4)*3, int(game.height/2)+100+opponent_text.get_rect().height/2))
                textRect.center = (game.width // 2, 200)
                input_box_x = (game.width - input_box_width)/2
                input_box_y =  game.height/2 - 85
                input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
                input_box_bkg = pygame.Rect((game.width - input_box_width)/2 , game.height/2 - 85, input_box_width, input_box_height)
                        

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if input_box.collidepoint(event.pos):
                    input_active = True
                    
                else: 
                    input_active = False

                # find new match
                if menu_button_rect.collidepoint(event.pos):
                    game.running = False

                    if game.multiplayer and not opp_disconnected_after:

                        # while loop to wait until it can disonnect safely
                        while True:
                            if can_disconnect:
                                game.n.disconnect()
                                break

                    gameOver = False
                    return False

                
                if rematch_button_rect.collidepoint(event.pos) and rematch_active and not opp_disconnected_after:

                    if game.multiplayer:
                        rematch_active = False
                        self_rematch_text = "Rematching..."
                        send("rematch")
                        
                    else:
                        gameOver = False
                        return True

        if held_key and time.time() >= held_time:

            held_time = time.time() + 0.05

            if held_unicode == "backspace":
                message_text = message_text[:-1]

            else:
                message_text += get_input(held_unicode)
            

        menu_button_color = tuple(darken(i, 15) for i in game.foreground_color) if menu_button_rect.collidepoint(mouse) else game.foreground_color

        rematch_button_color = tuple(darken(i, 15) for i in game.foreground_color) if rematch_button_rect.collidepoint(mouse) else game.foreground_color

        if game.multiplayer:
            draw_self_rematch_text()
            draw_texts()

        else:
            draw_stats()

        if won == None:
            gameOver = False
            return True

        game.screen.blit(game_over_text, textRect)
        mressage_text_width = draw_chat_box(message_text, input_active)
        draw_menu_button()
        draw_chat()

        if not opp_disconnected_after:
            draw_rematch_button()

        if (time.time() > game_over_start + 1 and not won == False) or won == True:
            pygame.display.update()

        game.clock.tick(60)


moving = 0


combo = -1
score_key = [100, 300, 500, 800]
tspin_key = [{"mini": 200, "normal": 800}, {
    "mini": 400, "normal": 1200}, {"normal": 1600}]
difficult_before = False


last_touched = 0
touched_floor = False

texts = []

# for sending junk lines
line_key = [0, 1, 2, 4]
t_spin_line_key = [2, 4, 6]
combo_line_key = [(1, 3), (4, 5), (6, 7), (8, 10), (11, 10000000)]

won = None

specials = []


def send(string):
    if game.multiplayer:
        specials.append(string)


# for getting information about opponent
disconnected = None
attacked = True


can_disconnect = False
countdown = 0

first_bag = False
def server_connection():
    
    global disconnected, current, specials, display_until, fall_speed, won, opp_disconnected_after, attacked, can_disconnect, opp_rematched, countdown, first_bag, bag

    specials.clear()

    while game.running:

        can_disconnect = False

        # for any events

        resting_coords = list(map(lambda block: (block.x, block.y, block.color), game.resting))

        if current:
            piece_block_coords = list(map(lambda block: (block.x, block.y, block.color), current.blocks))
        else:
            piece_block_coords = None
        
        sent_specials = specials.copy()

        try:
            data = game.n.send([resting_coords, piece_block_coords, game.meter, game.meter_stage, sent_specials])
        except:
            # lost connection unexpectedly
            disconnected = ("You disconnected", "Try again?")
            break

        can_disconnect = True

        if first_bag:
            first_bag = False

            bag = data.starting_bag

        # lost connection unexpectedly
        if not data:
            disconnected = ("You disconnected", "Try again?")
            break

        if data == "disconnect":
            
            # disconnected after game
            if won == None:
                disconnected = ("Opponent disconnected", "You win!")
            # disconnected in game
            else:
                opp_disconnected_after = True

            break

        for special in sent_specials:
            specials.remove(special)
        
        # if winner info hasn't updated yet
        if won == False and data.winner == None and game.round == data.round:
            continue


        # if the player won
        if data.winner == game.n.p:
            won = True

        # telling game over function that rematch has started
        elif data.winner == None and gameOver:
            won = None

        
        opp_rematched = data.opp_has_rematched(game.n.p)

        game.round = data.round
        
        game.opp_resting = data.opp_resting(game.n.p)
        game.opp_piece_blocks = data.opp_piece_blocks(game.n.p)
        game.opp_meter = data.opp_meter(game.n.p)
        game.opp_meter_stage = data.opp_meter_stage(game.n.p)


        for special in data.specials[game.n.p]:

            if special.startswith('junk'):
                amount = int(special.split()[1])

                start_meter_animation((game.opp_screen_junk_meter_rect.x + game.opp_screen_junk_meter_rect.width/2, game.opp_screen_junk_meter_rect.y + game.opp_screen_junk_meter_rect.height + 50), 0)
                game.play_sound('meter recieve')

                game.meter.append(amount)

            elif special.startswith('chat'):
                special = special[5:]

                chat.append(f"opp {special}")

        if game.level != data.speed_level():
            display_until = time.time() + 3
            game.level = data.speed_level()
            fall_speed = (0.8 - ((game.level - 1) * 0.007))**(game.level-1)

            if speedUp:
                fall_speed /= sds

        
        if data.countdown > time.time():
            countdown = data.countdown
        else:
            countdown = 0


mouse_number_key = {
    1: 'left click',
    2: 'middle click',
    3: 'right click'
}

meter_animations = []
number_animations = []


def start_meter_animation(pos, against):

    if game.multiplayer:
        meter_animations.append((pos, time.time(), 15, against))

        for _ in range(randint(3, 5)):
            random_pos = pos[0] + \
                random.randint(-60, 60), pos[1] + random.randint(-60, 60)
            random_size = random.randint(3, 10)

            meter_animations.append(
                (random_pos, time.time(), random_size, against))


def start_number_animation(pos, number):
    if game.multiplayer:
        number_animations.append((pos, time.time(), number))


def play_number_animations():
    
    if game.multiplayer:

        duration = 0.5
        travel_distance = 30

        removed = []

        for pos, start_time, number in number_animations:

            if time.time() - start_time > duration:
                removed.append((pos, start_time, number))
                continue

            start_time = time.time() - start_time

            traveled = (pos[0], (travel_distance /
                                duration * start_time * -1) + pos[1])

            text = game.font.render(str(number), True, game.preview_color)
            game.screen.blit(text, traveled)

        for remove in removed:
            number_animations.remove(remove)


def play_meter_animations():
    
    if game.multiplayer:

        duration = 0.5

        removed = []

        for pos, start_time, size, against in meter_animations:

            # going to opponent
            if against == 1:
                destination = (game.opp_screen_junk_meter_rect.x + game.opp_screen_junk_meter_rect.width/2, game.opp_screen_junk_meter_rect.y + game.opp_screen_junk_meter_rect.height)

            # coming from opponent
            else:
                destination = (game.playing_field_junk_meter_rect.x + game.playing_field_junk_meter_rect.width/2, game.playing_field_junk_meter_rect.y + game.playing_field_junk_meter_rect.height)

            if time.time() - start_time > duration:
                removed.append((pos, start_time, size, against))
                continue

            start_time = time.time() - start_time

            distance = (destination[0] - pos[0], destination[1] - pos[1])
            traveled = ((distance[0]/duration * start_time) +
                        pos[0], (distance[1]/duration * start_time) + pos[1])

            pos_size = traveled[0], traveled[1], size, size
            pygame.draw.rect(game.screen, (255, 255, 255), pos_size)

        for remove in removed:
            meter_animations.remove(remove)

das_start = 0
arr_start = 0
presence_update = 0

muted = False

while True:

    opp_disconnected_after = False
    start_screen.ready = False
    start_screen.started = False

    game.check_random_theme()
    start_screen.main()
    chat = []

    if game.multiplayer:
        _thread.start_new_thread(server_connection, ())
    else:
        countdown = time.time() + 6

    if game.multiplayer:
        first_bag = True

    # waiting for countdown so it doesn't flash
    # failsafe just in case the message actually took longer than 5 seconds to deliver, so the game doesn't crash
    failsafe = time.time() + 6
    while countdown < time.time() and failsafe > time.time():
        pass

    with open(get_path('settings.json')) as f:
        settings = json.load(f)

    music_volume = settings['audio']['main'] * settings['audio']['music']

    controls = settings['controls']
    gameplay_settings = settings['gameplay']

    das = gameplay_settings['das'] * 0.5
    arr = 0.205 - ((gameplay_settings['arr'] * 0.195) + 0.005)
    sds = int(gameplay_settings['sds']*78) + 2

    pygame.mouse.set_visible(False)

    while game.running:
        

        if disconnected:

            game.update_presence(
                details=f"In Disconnected Screen",
                state=f"Idle",
                start=game.time_opened,
                large_image="tetrium"
            )

            game.running = False
            pygame.mouse.set_visible(True)
            game.disconnected_screen(*disconnected)
            game.screen.fill((0, 0, 0))
            reset()
            disconnected = None
            break

        if won != None:
            opp_rematched = False
            pygame.mouse.set_visible(True)
            restart = game_over(won)
            reset()
            won = None

            if not restart:
                game.screen.fill((0, 0, 0))
                break

            if not game.multiplayer and restart:
                countdown = time.time() + 6

            game.check_random_theme()

            if game.multiplayer:
                first_bag = True

        
        if countdown > time.time():
            # meaning if the user quit in the countdown
            if not game.countdown(countdown):
                stop()

        # updating discord presence
        if time.time() > presence_update:
        
            if game.multiplayer:

                if game.opp_name:
                    presence_update = time.time() + 5

                    # getting y value of highest block
                    highest_y = 20
                    for block in game.resting:
                        if block.y < highest_y:
                            highest_y = block.y

                    highest_y = int(20 - highest_y)


                    game.update_presence(
                        details=f"Dueling {game.opp_name}",
                        state=f"{highest_y} Lines High",
                        start=game.time_started,
                        large_image="tetrium"
                    )
            
            else:
                presence_update = time.time() + 5

                game.update_presence(
                    details=f"Playing Singleplayer",
                    state=f"Score: {game.score}",
                    start=game.time_started,
                    large_image="tetrium"
                )


        # increasing speed level FOR SINGLEPLAYER
        if not game.multiplayer:
            level = (game.lines // 10) + 1

            if level > game.level:
                game.level = level
                fall_speed = (0.8 - ((game.level - 1) * 0.007))**(game.level-1)
                display_until = time.time() + 3
                
                if speedUp:
                    fall_speed /= sds
            




        # if there are fading blocks, pause the game for a quick moment
        if game.rows_cleared:

            # checking if the fading blocks can be removed yet
            if game.rows_cleared[0][0].fade_start + 0.5 < time.time():

                for row in game.rows_cleared:

                    for block in row:
                        game.resting.remove(block)

                    for block in game.resting:
                        if block.y < row[0].y:
                            block.y += 1

                game.rows_cleared.clear()

            game.render(bag[:3], held)

            play_meter_animations()
            play_number_animations()
            render_texts()

            pygame.display.update()
            game.clock.tick(60)

            continue

        if not current:
            current = Piece(5, 1, pick_bag())

            # checking if game is over
            if current.overlapping_blocks():

                if current.piece_type != "O":
                    current.rotate(1, play_sound=False)

                    if current.overlapping_blocks():
                        current.rotate(-1, play_sound=False)

                else:
                    current.move(0, -1)

                    if current.overlapping_blocks():
                        current.move(1, 0)

                        if current.overlapping_blocks():
                            current.move(-2, 0)

                if current.overlapping_blocks():
                    won = False

        if moving:

            if moving == -1:
                if time.time() > arr_start and time.time() > das_start:
                    if not current.check_left():
                        current.move(-1, 0)
                        arr_start = time.time() + arr

                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)


            elif moving == 1:
                if time.time() > arr_start and time.time() > das_start:
                    if not current.check_right():
                        current.move(1, 0)
                        arr_start = time.time() + arr

                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)


        backToTop = False

        for event in pygame.event.get():
            game.check_fullscreen(event, True)

            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):

                if event.type == pygame.KEYDOWN:
                    key_name = pygame.key.name(event.key)

                else:

                    if 1 <= event.button <= 3:
                        key_name = mouse_number_key[event.button]
                    else:
                        key_name = None

                if key_name == controls['Move Left']:

                    if not current.check_left():

                        if not game.continuous:
                            current.move(-1, 0)

                        else:
                            current.move(-1, 0)
                            das_start = max(time.time() + das, time.time() + arr)


                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)

                    if game.continuous:
                        moving = -1

                elif key_name == controls['Move Right']:

                    if not current.check_right():

                        if not game.continuous:
                            current.move(1, 0)

                        else:
                            current.move(1, 0)
                            das_start = max(time.time() + das, time.time() + arr)



                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)

                    if game.continuous:
                        moving = 1

                elif key_name == controls['Rotate Clockwise']:

                    current.rotate(0)

                    current.move(0, 1)
                    if current.check_floor():
                        if avoids < 15:
                            fall = time.time() + 0.5
                            avoids += 1
                    current.move(0, -1)


                elif key_name == controls['Rotate Counter-Clockwise']:
                    current.rotate(1)

                    current.move(0, 1)
                    if current.check_floor():
                        if avoids < 15:
                            fall = time.time() + 0.5
                            avoids += 1

                    current.move(0, -1)


                elif key_name == controls['Hold Piece']:

                    if canSwitch:
                        game.play_sound('hold')

                        if not held:
                            held = current.piece_type
                            current = None

                        else:
                            past_held = held
                            held = current.piece_type
                            current = Piece(5, 1, past_held)

                        avoids = 0
                        canSwitch = False

                        backToTop = True

                elif key_name == controls['Soft Drop']:
                    if not speedUp:
                        fall_speed /= sds
                        speedUp = True
                        last_fall -= 2

                elif key_name == controls['Hard Drop']:

                    downCount = 0
                    if current:
                        while not current.check_floor():
                            current.move(0, 1)
                            downCount += 1

                    current.move(0, -1)
                    downCount -= 1

                    last_fall -= 5
                    fall -= 5
                    touched_floor = True
                    last_touched -= 5

                    game.score += downCount*2

                    game.vfx(VFX.hard_drop, current)

                elif key_name == controls['Toggle Movement']:
                    game.continuous = not game.continuous
                    moving = 0

                elif key_name == controls['Pause'] and not game.multiplayer:
                    
                    def pause_render():
                        game.render(bag[:3], held)
                        current and current.render()

                    game.pause(pygame.key.key_code(key_name), pause_render)

            elif event.type == pygame.VIDEORESIZE:
                try:
                    game.width, game.height = event.w, event.h
                except: pass
                game.resize_all_screens()

            elif event.type in (pygame.KEYUP, pygame.MOUSEBUTTONUP):

                if event.type == pygame.KEYUP:
                    key_name = pygame.key.name(event.key)
                else:
                    if 1 <= event.button <= 3:
                        key_name = mouse_number_key[event.button]
                    else:
                        key_name = None

                if key_name == controls['Soft Drop']:
                    if speedUp:
                        fall_speed *= sds
                        speedUp = False

                elif key_name == controls['Move Left']:
                    if moving == -1:
                        moving = 0

                elif key_name == controls['Move Right']:
                    if moving == 1:
                        moving = 0

                elif key_name == controls['Toggle Music']:

                    if not muted:
                        game.music = 0
                        pygame.mixer.music.set_volume(0)
                    else:
                        game.music = music_volume
                        pygame.mixer.music.set_volume(game.music)

                    muted = not muted

            elif event.type == pygame.QUIT:
                stop()

        if backToTop:
            continue

        game.render(bag[:3], held)

        current.move(0, 1)
        if current.check_floor() and not touched_floor:
            fall = time.time() + 0.5
            touched_floor = True

        elif not current.check_floor():
            touched_floor = False
        current.move(0, -1)

        # makes the piece fall by one
        if time.time() > last_fall:
            last_fall = time.time() + fall_speed
            current.move(0, 1)

            if speedUp and not current.check_floor():
                game.score += 1

            if current.check_floor():

                if time.time() > fall:

                    # Any piece spin detection

                    current.move(0, -1)

                    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

                    spin_move = True

                    for direction in directions:

                        current.move(*direction)

                        if not current.check_overlap():
                            spin_move = False

                        current.move(*tuple(-1 * i for i in direction))

                        if not spin_move:
                            break

                    else:

                        if current.piece_type != "T":
                            texts.append((f'{current.piece_type}-Spin', time.time() + 3, 30))

                    current.move(0, 1)


                    current.flash()
                    # turn piece into resting blocks
                    for block in current.blocks:
                        block.y -= 1
                        game.resting.append(block)

                    touched_floor = False

                    # detect if a row was made
                    lines_cleared = 0
                    for y in range(1, 21):
                        row = list(
                            filter(lambda block: block.y == y, game.resting))

                        # line clear
                        if len(row) == 10:

                            for block in row:
                                block.fade_start = time.time()

                            lines_cleared += 1

                            game.rows_cleared.append(row)

                    tspin = None



                    # T-Spin detection
                    if current.piece_type == "T" and spin_move:

                        filled_corners = {}

                        # getting all filled corners, either by blocks or walls
                        for name, value in current.corners.items():
                            x, y = value
                            y -= 1

                            if not 0 <= x <= 10 or y > 20:
                                filled_corners[name] = True
                                continue

                            for block in game.resting:
                                if (block.x, block.y) == (x, y):
                                    filled_corners[name] = True
                                    break
                            else:
                                filled_corners[name] = False


                        # normal t-spin
                        if (filled_corners["point left"] and filled_corners["point right"]) and (filled_corners["flat right"] or filled_corners["flat left"]):
                            tspin = "normal"

                        # mini t-spin
                        elif (filled_corners["flat right"] and filled_corners["flat left"]) and (filled_corners["point left"] or filled_corners["point right"]):
                            tspin = "mini"

                    lines_sent = 0

                    if lines_cleared:

                        game.play_sound('row cleared')
                        game.lines += lines_cleared

                        combo += 1

                        if combo > 0:
                            texts.append(
                                (f"{combo+1} Combo", time.time() + 3, 20))

                            for minimum, maximum in combo_line_key:
                                if minimum <= combo <= maximum:
                                    lines_sent += combo
                                    break

                        # calcualting combos
                        game.score += 50 * combo * game.level

                        if not tspin:

                            lines_sent += line_key[lines_cleared-1]

                            # for adding normal value
                            line_clear_value = game.level * score_key[lines_cleared-1]

                            # checking for back-to-back difficult line clear
                            if lines_cleared == 4:

                                texts.append(('Tetris', time.time() + 3, 30))

                                if difficult_before:
                                    line_clear_value *= 1.5
                                    line_clear_value = int(line_clear_value)
                                    texts.append(
                                        (f"Back to Back", time.time() + 3, 15))
                                    lines_sent += 1
                                else:
                                    difficult_before = True

                            game.score += line_clear_value

                        else:

                            lines_sent += t_spin_line_key[lines_cleared-1]

                            # any line clears with t-spins are considered difficult
 
                            score_value = game.level * tspin_key[lines_cleared-1][tspin]

                            if tspin == "normal":
                                spin_text, size = "T-Spin", 30
                            else:
                                spin_text, size = "T-Spin Mini", 17

                            if lines_cleared == 1:
                                lines_text = "Single"
                            elif lines_cleared == 2:
                                lines_text = "Double"
                            else:
                                lines_text = "Triple"

                            texts.append(
                                ([spin_text, lines_text], time.time() + 3, size))

                            if difficult_before:
                                score_value *= 1.5
                                texts.append(
                                    (f"Back to Back", time.time() + 3, 15))
                                lines_sent += 1
                            else:
                                difficult_before = True

                            game.score += score_value

                    # no line t-spins
                    elif tspin:

                        # getting block with lowest y value
                        lowest_y = 0
                        for block in current.blocks:
                            if block.y > lowest_y:
                                lowest_y = block.y

                        lowest_y -= 19

                        if tspin == "normal":
                            game.score += 400 * lowest_y
                            texts.append((f"T-Spin", time.time() + 3, 30))

                        elif tspin == "mini":
                            game.score += 100 * lowest_y
                            texts.append((f"T-Spin Mini", time.time() + 3, 17))

                    if not list(filter(lambda block: not block.fade_start, game.resting)):
                        lines_sent = 10
                        texts.append((f"Perfect Clear", time.time() + 3, 17))

                    if lines_cleared:
                        
                        # clearing junk from own meter
                        amount = max(lines_cleared, lines_sent)

                        while game.meter and amount > 0:
                            game.meter[0] -= 1
                            amount -= 1

                            if game.meter[0] <= 0:
                                game.meter.pop(0)
                                game.meter_stage = 1

                    
                    if lines_sent:
                        send(f"junk {lines_sent}")

                        if game.multiplayer:
                            game.play_sound('meter send')

                        # getting the block with the highest y
                        highest_y = 0
                        chosen_block = None
                        for block in current.blocks:
                            if block.y > highest_y:
                                highest_y = block.y
                                chosen_block = block

                        pos = (chosen_block.x-1) * chosen_block.size + game.playing_field_rect.x, (chosen_block.y-1) * chosen_block.size + game.playing_field_rect.y

                        start_meter_animation(pos, 1)
                        start_number_animation(pos, lines_sent)

                    if not lines_cleared:
                        combo = -1

                        if game.meter:
                            # increasing the stage of the incoming junk
                            game.meter_stage += 1

                            if game.meter_stage > 3:
                                attacked = False
                                
                                game.meter_stage = 1
                                
                                amount = game.meter.pop(0)
                                game.play_sound('garbage recieve')

                                for block in game.resting:
                                    block.y -= amount

                                position = random.randint(1, 10)

                                for y in range(amount):
                                    for x in range(1, 11):
                                        if x != position:
                                            game.resting.append(
                                                Block(x, 20-y, "gray"))

                    game.render(bag[:3], held)

                    canSwitch = True

                    # make new falling piece
                    current = None
                    avoids = 0

                else:
                    last_fall -= 10
                    current.move(0, -1)

        if current:
            current.render()

        play_meter_animations()
        play_number_animations()

        if display_until > time.time():
            text = game.font.render(
                f'Speed Level {game.level}', True, game.background_color)
            textRect = text.get_rect()
            textRect.center = (game.playing_field_rect.x + 150, game.height // 2)
            game.screen.blit(text, textRect)

        render_texts()

        pygame.display.update()
