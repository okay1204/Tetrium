# pylint: disable=no-member, unused-wildcard-import
import pygame
from game import *
import time
import random
import sys


pieces = ["T", "L", "BL", "S", "BS", "I", "O"]

bag = pieces.copy()
random.shuffle(bag)
next_bag = pieces.copy()
random.shuffle(next_bag)

fall_speed = 1 # means once per second
speed_up_rate = 30 # every 30 seconds speed up


last_fall = time.time() + fall_speed
fall = 0

current = Piece(5, 1, bag.pop(0))

speedUp = False

avoids = 0

held = ''

last_speed_up = time.time() + speed_up_rate
speedLevel = 1
display_until = 0

canSwitch = True


def game_over():

    global bag, next_bag, avoids, speedLevel, current

    gameOver = True

    pygame.mixer.music.set_volume(0.03)
    button_dimensions = (140 ,40)
    button_pos = (game.width/2 - 70, game.height/2)

    while gameOver:

        mouse = pygame.mouse.get_pos()
        #Game over loop

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                if game.width/2 <= mouse[0] <= game.width/2 + button_dimensions[0] and game.height/2 <= mouse[1] <= game.height/2 + button_dimensions[1]: 

                    gameOver = False
                    game.resting.clear()
                    game.removing.clear()
                    speedLevel = 0
                    bag = pieces.copy()
                    random.shuffle(bag)
                    next_bag = pieces.copy()
                    random.shuffle(next_bag)
                    avoids = 0
                    current = Piece(5, 1, bag.pop(0))
                    pygame.mixer.music.set_volume(0.15)


        pygame.draw.rect(game.screen, (0,0,0), (button_pos, button_dimensions))

        s = pygame.Surface((game.width, game.height), pygame.SRCALPHA) # noqa pylint: disable=too-many-function-args
        s.fill((255,255,255, 2))      
        game.screen.blit(s, (0,0))
        game_over_font = pygame.font.Font('assets/arial.ttf', 60)
        button_font  = pygame.font.Font('assets/arial.ttf', 32)
        game_over_text = game_over_font.render(f'Game Over', True, (0, 0 ,0), game.screen)
        button_text = button_font.render(f'RESTART', True, (255, 255 , 255), game.screen)
        textRect = game_over_text.get_rect() 
        textRect.center = (game.width // 2, 200) 
        game.screen.blit(game_over_text, textRect)
        game.screen.blit(button_text, (button_pos[0] + 10, button_pos[1] + 3))
        pygame.display.update()

        game.clock.tick(60)



moving = 0
last_moved = 0


last_rotation_fall = 0

score = 0
combo = -1
score_key = [100, 300, 500, 800]
difficult_before = False

#This runs the start screen loop, it cant be in the main loop or it will mess things up
#NOTE uncomment start screen in final version
# game.start_screen()

while game.running:


    if moving:

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


        if moving == 1:
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


    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:

            # move left
            if event.key == pygame.K_a:

                if not game.continuous:
                    if not current.check_left():
                        current.move(-1, 0)

                        current.move(0, 1)
                        if current.check_floor():
                            if avoids < 15:
                                fall = time.time() + 0.3
                                avoids += 1
                        current.move(0, -1)

                else:
                    moving = -1
            
            # move right
            elif event.key == pygame.K_d:

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

            # rotate clockwise
            elif event.key == pygame.K_RIGHT:
                current.rotate(0)

                current.move(0, 1)
                if current.check_floor():
                    if avoids < 15:
                        fall = time.time() + 1
                        avoids += 1
                current.move(0, -1)

            # rotate counter-clockwise
            elif event.key == pygame.K_LEFT:
                current.rotate(1)

                current.move(0, 1)
                if current.check_floor():
                    if avoids < 15:
                        fall = time.time() + 1
                        avoids += 1
                
                current.move(0, -1)

          
            # hold block
            elif event.key == pygame.K_UP:
                
                
                if canSwitch:
                    game.holdSFX.play()
                    
                    if not held:
                        held = current.piece_type
                        current = Piece(5, 1, bag.pop(0))
                    
                    else:
                        past_held = held
                        held = current.piece_type
                        current = Piece(5, 1, past_held)

                    avoids = 0
                    canSwitch = False

                    # checking if game is over
                    if current.overlapping_blocks():
                        current.rotate(1)

                        if current.overlapping_blocks():
                            current.rotate(-1)
                            current.rotate(-1)

                            if current.overlapping_blocks():
                                game_over()

                    if current.y <= -2:
                        game_over()


            # speed down
            elif event.key == pygame.K_s:
                if not speedUp:
                    fall_speed /= 10
                    speedUp = True
                    last_fall -= 2
            
            # force down
            elif event.key == pygame.K_DOWN:
                
                downCount = 0
                while not current.check_floor():
                    current.move(0, 1)
                    downCount += 1

                current.move(0,-1)
                downCount -= 1

                last_fall -= 2

                score += downCount*2

            elif event.key == pygame.K_g:
                game.continuous = not game.continuous
                moving = 0

        elif event.type == pygame.KEYUP:

            # stop speed down
            if event.key == pygame.K_s:
                if speedUp:
                    fall_speed *= 10
                    speedUp = False

            
            # stop hold moving
            if event.key == pygame.K_a:
                if moving == -1:
                    moving = 0

            if event.key == pygame.K_d:
                if moving == 1:
                    moving = 0
                

        elif event.type == pygame.QUIT:
            game.running = False
            sys.exit()




    # for getting the next three items
    if len(bag) >= 3:
        game.render(bag[:3], held, score)

    elif len(bag) > 0:
        amount = len(bag)

        temp = bag.copy()
        temp.extend(next_bag[:3 - amount])
        game.render(temp, held, score)
    else:
        bag = next_bag.copy()
        next_bag = pieces.copy()
        random.shuffle(next_bag)
        game.render(bag[:3], held, score)



    # speed up fall
    if time.time() > last_speed_up:
        last_speed_up = time.time() + speed_up_rate
        fall_speed /= 1.2
        speedLevel += 1
        display_until = time.time() + 3

    # makes the piece fall by one
    if time.time() > last_fall:
        last_fall = time.time() + fall_speed
        current.move(0, 1)
        
        if speedUp and not current.check_floor():
            score += 1

        if current.check_floor():

            if time.time() > fall:
                # turn piece into resting blocks
                for block in current.blocks:
                    game.resting.append(Block(block.x, block.y-1, block.color, colorByName=False))
                
                # detect if a row was made
                lines_cleared = 0
                lowest_y = 0
                for y in range(1, 21):
                    row = list(filter(lambda block: block.y == y, game.resting))

                    # line clear
                    if len(row) == 10:

                        removed_blocks = []
                        # set the fade increments for blocks
                        for block in row:
                            
                            fade_increments = []
                            for color in block.color:
                                fade_increments.append((255 - color) // 15)

                            block.fade_increments = tuple(fade_increments)
                            removed_blocks.append(block)
                        
                        game.removing.append(removed_blocks)

                        lines_cleared += 1
                        if lowest_y < y:
                            lowest_y = y

                if lines_cleared:
                    combo += 1

                    # for adding normal value
                    line_clear_value = (21 - lowest_y) * score_key[lines_cleared-1]

                    # calcualting combos
                    score += 50 * combo * (21 - lowest_y)

                    # checking for back-to-back difficult line clear
                    if lines_cleared == 4:
                        if difficult_before:
                            line_clear_value *= 1.5
                            line_clear_value = int(line_clear_value)
                        else:
                            difficult_before = True
                    else:
                        difficult_before = False
                    
                    score += line_clear_value
                    
                else:
                    combo = -1


    
                # for getting the next three items
                if len(bag) >= 3:
                    game.render(bag[:3], held, score)



                elif len(bag) > 0:
                    amount = len(bag)
                    temp = bag.copy()
                    temp.extend(next_bag[:3 - amount])
                    game.render(temp, held, score)
                else:
                    bag = next_bag.copy()
                    next_bag = pieces.copy()
                    random.shuffle(next_bag)
                    game.render(bag[:3], held, score)


                #TODO play land sound here
                canSwitch = True

                # make new falling piece
                current = Piece(5, 1, bag.pop(0))
                avoids = 0


                # checking if game is over
                if current.overlapping_blocks():
                    current.rotate(1)

                    if current.overlapping_blocks():
                        current.rotate(-1)
                        current.rotate(-1)

                        if current.overlapping_blocks():
                            game_over()

                if current.y <= -2:
                    game_over()


            else:
                current.move(0, -1)

    
    current.render()

    if display_until > time.time():
        text = game.font.render(f'Speed Level {speedLevel}', True, (0, 0 ,0))
        textRect = text.get_rect() 
        textRect.center = (game.width // 2, game.height // 2) 
        game.screen.blit(text, textRect)

    
    pygame.display.update()

    game.clock.tick(60)