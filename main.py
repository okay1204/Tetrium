# pylint: disable=no-member, unused-wildcard-import
import pygame
from game import *
import time
import random
import sys
import json
import _thread
import socket
import onlineGame
from oooooooooooooooooooooooooooooooooooooooooooootils import resource_path

import sys


pieces = ["T", "L", "J", "S", "Z", "I", "O"]

bag = pieces.copy()
random.shuffle(bag)
next_bag = pieces.copy()
random.shuffle(next_bag)

def stop():

    game.running = False
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

            font = pygame.font.Font(resource_path('assets/arial.ttf'), size)

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
                    450, 500 + (texts.index((original, display_time, size)) * 50) + (index * 25))

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
rotation_last = False

gameOver = False


def reset():
    global bag, next_bag, avoids, current, held, canSwitch, moving, fall_speed

    game.resting.clear()
    game.level = 1
    game.score = 0
    game.lines = 0
    bag = pieces.copy()
    random.shuffle(bag)
    next_bag = pieces.copy()
    random.shuffle(next_bag)
    avoids = 0
    current = None
    pygame.mixer.music.set_volume(game.volume)
    held = None
    canSwitch = True
    moving = 0
    game.meter.clear()
    game.time_started = time.time()
    fall_speed = 1


opp_disconnected_after = False
opp_rematched = False

def game_over(win: bool):

    global gameOver, opp_disconnected_after

    gameOver = True

    pygame.mixer.music.set_volume(game.lowered_volume)
    button_dimensions = (250, 40)
    button_pos = (
        int(game.width/2 - button_dimensions[0]/2), int(game.height/2))

    restart_button_font = pygame.font.Font(resource_path('assets/arial.ttf'), 32)
    restart_button_rect = pygame.Rect(button_pos, button_dimensions)
    restart_button_color = (255, 255, 255)
    restart_button_text = restart_button_font.render(
        'Find new match', True, (0, 0, 0))
    game_over_font = pygame.font.Font(resource_path('assets/arial.ttf'), 50)

    rematch_text_font = pygame.font.Font(resource_path('assets/arial.ttf'), 40)
    self_rematch_text = opp_rematch_text = "Deciding..."
    
    rematch_active = True

    rematch_button_font = pygame.font.Font(resource_path('assets/arial.ttf'), 26)
    rematch_button_dimensions = (120, 40)
    rematch_button_text = rematch_button_font.render('Rematch', True, (0, 0, 0))

    self_rematch_button_pos = (int(game.width/2 - rematch_button_dimensions[0]/2), int(game.height/2)+150)
    self_rematch_button_rect = pygame.Rect(self_rematch_button_pos, rematch_button_dimensions)
    self_rematch_button_color = (255, 255, 255)


    text_font = pygame.font.Font(resource_path('assets/arial.ttf'), 25)
    you_text = text_font.render("You", True, (0, 0, 0))
    opponent_text = text_font.render(game.opp_name, True, (0, 0, 0))
    opponent_rect = opponent_text.get_rect(center=((game.width/4)*3, int(game.height/2)+100+opponent_text.get_rect().height/2))

    if not win:
        send('game over')
        game_over_text = game_over_font.render('You lost...', True, (0, 0, 0))

    else:
        game_over_text = game_over_font.render('You win!', True, (0, 0, 0))

    textRect = game_over_text.get_rect()
    textRect.center = (game.width // 2, 200)

    def draw_restart_button():

        pygame.draw.rect(game.screen, restart_button_color,
                         restart_button_rect)
        game.screen.blit(restart_button_text,
                         (button_pos[0] + 10, button_pos[1] + 3))

    def draw_bkg():
        game.screen.blit(game.opaque_bkg, (0, 0))
        game.opaque_bkg.set_alpha(120)

    def draw_self_rematch_button():
        pygame.draw.rect(game.screen, self_rematch_button_color, self_rematch_button_rect)
        game.screen.blit(rematch_button_text, (self_rematch_button_pos[0]+10, self_rematch_button_pos[1]+4))

    def draw_self_rematch_text():
        
        self_rendered_text = rematch_text_font.render(self_rematch_text, True, (0, 0, 0))
        game.screen.blit(self_rendered_text, (int(game.width/4)-100, int(game.height/2)+250))


        opp_rendered_text = rematch_text_font.render(opp_rematch_text, True, (0, 0, 0))
        game.screen.blit(opp_rendered_text, (int(game.width/2)+80, int(game.height/2)+250))

    def draw_texts():
        game.screen.blit(you_text, (int(game.width/4)-30, int(game.height/2)+100))

        game.screen.blit(opponent_text, opponent_rect)


    while gameOver:


        if opp_disconnected_after:
            opp_rematch_text = "Disconnected"
        elif opp_rematched:
            opp_rematch_text = "Rematching..."


        mouse = pygame.mouse.get_pos()

        # Game over loop

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                stop()

            elif event.type == pygame.VIDEORESIZE:
                game.width, game.height = event.w, event.h
                game.resize_all_screens()
            

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # find new match
                if restart_button_rect.collidepoint(event.pos):
                    reset()
                    game.running = False

                    if not opp_disconnected_after:

                        # while loop to wait until it can disonnect safely
                        while True:
                            if can_disconnect:
                                game.n.disconnect()
                                break

                    gameOver = False
                    return False

                
                if self_rematch_button_rect.collidepoint(event.pos) and rematch_active and not opp_disconnected_after:
                    rematch_active = False
                    self_rematch_text = "Rematching..."
                    send("rematch")

        # for hover effects
        if restart_button_rect.collidepoint(mouse):
            restart_button_color = tuple(map(darken, (255, 255, 255)))
        else:
            restart_button_color = (255, 255, 255)

        

        if self_rematch_button_rect.collidepoint(mouse):
            self_rematch_button_color = tuple(map(darken, (255, 255, 255)))
        else:
            self_rematch_button_color = (255, 255, 255)


        if won == None:
            gameOver = False
            return True

        game.screen.blit(game_over_text, textRect)

        draw_restart_button()

        if not opp_disconnected_after:
            draw_self_rematch_button()

        draw_self_rematch_text()
        draw_texts()
        draw_bkg()

        pygame.display.update()
        game.clock.tick(60)


moving = 0
last_moved = 0


last_rotation_fall = 0

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
    global specials

    specials.append(string)


# for getting information about opponent
disconnected = None
attacked = True


can_disconnect = False
countdown = 0

def server_connection():
    
    global disconnected, current, specials, display_until, fall_speed, won, opp_disconnected_after, attacked, can_disconnect, opp_rematched, countdown

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
            data = game.n.send([resting_coords, piece_block_coords, sent_specials])
        except:
            # lost connection unexpectedly
            disconnected = ("You disconnected", "Try again?")
            break

        can_disconnect = True

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


        meter = data.own_meter(game.n.p)
        if len(meter) > len(game.meter):

            if attacked:
                start_meter_animation((700, 600), 0)
                game.meter_recieveSFX.play()
            else:
                attacked = True

        game.meter = meter

        game.meter_stage = data.own_meter_stage(game.n.p)

        if game.level != data.speed_level():
            display_until = time.time() + 3
            game.level = data.speed_level()
            fall_speed = (0.8 - ((game.level - 1) * 0.007))**(game.level-1)

            if speedUp:
                fall_speed /= 10

        
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
    global meter_animations

    meter_animations.append((pos, time.time(), 15, against))

    for _ in range(randint(3, 5)):
        random_pos = pos[0] + \
            random.randint(-60, 60), pos[1] + random.randint(-60, 60)
        random_size = random.randint(3, 10)

        meter_animations.append(
            (random_pos, time.time(), random_size, against))


def start_number_animation(pos, number):
    global number_animations

    number_animations.append((pos, time.time(), number))


def play_number_animations():
    global number_animations

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
    global meter_animations

    duration = 0.5

    removed = []

    for pos, start_time, size, against in meter_animations:

        # going to opponent
        if against == 1:
            destination = (550, 550)
        # coming from opponent
        else:
            destination = (50, 700)

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


while True:

    opp_disconnected_after = False
    start_screen.ready = False
    start_screen.started = False

    start_screen.main()
    _thread.start_new_thread(server_connection, ())

    with open('settings.json') as f:
        controls = json.load(f)['controls']

    # NOTE uncomment this line after
    # pygame.mouse.set_visible(False)

    while game.running:

        if disconnected:
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
            reset()
            rematch = game_over(won)
            won = None

            if not rematch:
                game.screen.fill((0, 0, 0))
                break

        
        if countdown > time.time():
            # meaning if the user quit in the countdown
            if not game.countdown(countdown):
                stop()

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
                    current.rotate(1)

                    if current.overlapping_blocks():
                        current.rotate(-1)

                else:
                    current.move(0, -1)

                    if current.overlapping_blocks():
                        current.move(1, 0)

                        if current.overlapping_blocks():
                            current.move(-2, 0)

                if current.overlapping_blocks():
                    won = False

        if moving:

            rotation_last = False

            if moving == -1:
                if time.time() - last_moved > 0.1:
                    if not current.check_left():
                        current.move(-1, 0)
                        last_moved = time.time()

                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)

            elif moving == 1:
                if time.time() - last_moved > 0.1:
                    if not current.check_right():
                        current.move(1, 0)
                        last_moved = time.time()

                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)

        backToTop = False
        for event in pygame.event.get():

            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):

                if event.type == pygame.KEYDOWN:
                    key_name = pygame.key.name(event.key)

                else:

                    if 1 <= event.button <= 3:
                        key_name = mouse_number_key[event.button]
                    else:
                        key_name = None

                if key_name == controls['Move Left']:

                    if not game.continuous:
                        if not current.check_left():
                            current.move(-1, 0)

                            current.move(0, 1)
                            if current.check_floor():
                                if avoids < 15:
                                    fall = time.time() + 0.3
                                    avoids += 1
                            current.move(0, -1)

                            rotation_last = False

                    else:
                        moving = -1

                elif key_name == controls['Move Right']:

                    if not game.continuous:
                        if not current.check_right():
                            current.move(1, 0)

                            current.move(0, 1)
                            if current.check_floor():
                                if avoids < 15:
                                    fall = time.time() + 0.3
                                    avoids += 1
                            current.move(0, -1)

                    else:
                        moving = 1

                elif key_name == controls['Rotate Clockwise']:

                    current.rotate(0)

                    current.move(0, 1)
                    if current.check_floor():
                        if avoids < 15:
                            fall = time.time() + 1
                            avoids += 1
                    current.move(0, -1)

                    rotation_last = True

                elif key_name == controls['Rotate Counter-Clockwise']:
                    current.rotate(1)

                    current.move(0, 1)
                    if current.check_floor():
                        if avoids < 15:
                            fall = time.time() + 1
                            avoids += 1

                    current.move(0, -1)

                    rotation_last = True

                elif key_name == controls['Hold Piece']:

                    if canSwitch:
                        game.holdSFX.play()

                        if not held:
                            held = current.piece_type
                            current = None

                        else:
                            past_held = held
                            held = current.piece_type
                            current = Piece(5, 1, past_held)

                        avoids = 0
                        canSwitch = False
                        rotation_last = False

                        backToTop = True

                elif key_name == controls['Soft Drop']:
                    if not speedUp:
                        fall_speed /= 10
                        speedUp = True
                        last_fall -= 2

                elif key_name == controls['Hard Drop']:

                    downCount = 0
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
                    if downCount:
                        rotation_last = False

                elif key_name == controls['Toggle Movement']:
                    game.continuous = not game.continuous
                    moving = 0


            elif event.type == pygame.VIDEORESIZE:
                game.width, game.height = event.w, event.h
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
                        fall_speed *= 10
                        speedUp = False

                elif key_name == controls['Move Left']:
                    if moving == -1:
                        moving = 0

                elif key_name == controls['Move Right']:
                    if moving == 1:
                        moving = 0

                elif key_name == controls['Toggle Music']:

                    if game.lowered_volume and game.volume:
                        game.lowered_volume, game.volume = 0, 0

                    else:
                        game.lowered_volume, game.volume = 0.025, 0.05

            elif event.type == pygame.QUIT:
                stop()

        if backToTop:
            continue

        game.render(bag[:3], held)

        current.move(0, 1)
        if current.check_floor() and not touched_floor and not rotation_last:
            fall = time.time() + 0.95
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

            if not current.check_floor():
                rotation_last = False

            if current.check_floor():

                if time.time() > fall:

                    current.flash()
                    # turn piece into resting blocks
                    for block in current.blocks:
                        block.y -= 1
                        game.resting.append(block)

                    touched_floor = False

                    # detect if a row was made
                    lines_cleared = 0
                    lowest_y = 0
                    for y in range(1, 21):
                        row = list(
                            filter(lambda block: block.y == y, game.resting))

                        # line clear
                        if len(row) == 10:

                            for block in row:
                                block.fade_start = time.time()

                            lines_cleared += 1
                            if lowest_y < y:
                                lowest_y = y

                            game.rows_cleared.append(row)

                    tspin = None

                    tspin = None

                    # T-Spin detection
                    if current.piece_type == "T" and rotation_last:

                        filled_corners = {}

                        # getting all filled corners, either by blocks or walls
                        for name, value in current.corners.items():
                            x, y = value
                            y -= 1

                            if not 0 < x < 10 or y > 20:
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

                        send(f"clear {lines_cleared}")

                        game.row_clearedSFX.play()
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
                        game.score += 50 * combo * (21 - lowest_y)

                        if not tspin:

                            lines_sent += line_key[lines_cleared-1]

                            # for adding normal value
                            line_clear_value = (
                                21 - lowest_y) * score_key[lines_cleared-1]

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

                            score_value = (21 - lowest_y) * \
                                tspin_key[lines_cleared-1][tspin]

                            if tspin == "normal":
                                spin_text, size = "T-Spin", 30
                            else:
                                spin_text, size = "T-Spin Mini", 17

                            if lines_cleared == 1:
                                lines_text = "Single"
                            elif lines_cleared == 2:
                                lines_text = "Double"
                            elif lines_cleared == 3:
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

                    if lines_sent:
                        send(f"junk {lines_sent}")
                        game.meter_sendSFX.play()

                        # getting the block with the highest y
                        highest_y = 0
                        chosen_block = None
                        for block in current.blocks:
                            if block.y > highest_y:
                                highest_y = block.y
                                chosen_block = block

                        pos = (block.x-1) * block.size + \
                            100, (block.y-1) * block.size + 100

                        start_meter_animation(pos, 1)
                        start_number_animation(pos, lines_sent)

                    if not lines_cleared:
                        combo = -1

                        if game.meter:
                            # increasing the stage of the incoming junk
                            send("meter increase")

                            meter_stage = game.meter_stage

                            if meter_stage >= 3:
                                attacked = False
                                send("meter reset")
                                game.garbage_recieveSFX.play()

                                amount = game.meter[0]
                                game.meter.pop(0)

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
                    current.move(0, -1)

        if current:
            current.render()

        play_meter_animations()
        play_number_animations()

        if display_until > time.time():
            text = game.font.render(
                f'Speed Level {game.level}', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (250, game.height // 2)
            game.screen.blit(text, textRect)

        pygame.mixer.music.set_volume(game.volume)

        render_texts()

        pygame.display.update()

        game.clock.tick(60)
