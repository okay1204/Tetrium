# pylint: disable=no-member, unused-wildcard-import
import pygame
from game import *
import time
import random


pieces = ["T", "L", "BL", "S", "BS", "I", "O"]
# pieces = ["T", "L", "BL"]
bag = pieces.copy()
random.shuffle(bag)
next_bag = pieces.copy()
random.shuffle(next_bag)

fall_speed = 1 # means once per second
speed_up_rate = 30 # every 30 seconds speed up


last_fall = time.time() + fall_speed
fall = True

current = Piece(5, 1, bag.pop(0))

speedUp = False

rotations = 0


last_speed_up = time.time() + speed_up_rate
speedLevel = 1
display_until = 0

canSwitch = True
while game.running:

    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:

            # move left
            if event.key == pygame.K_a:
                if not current.check_left():
                    current.move(-1, 0)
            
            # move right
            elif event.key == pygame.K_d:
                if not current.check_right():
                    current.move(1, 0)

            # rotate clockwise
            elif event.key == pygame.K_RIGHT:
                current.rotate(0)

                current.move(0, 1)
                if current.check_floor():
                    if rotations < 15:
                        fall = False
                        rotations += 1
                current.move(0, -1)

            # rotate counter-clockwise
            elif event.key == pygame.K_LEFT:
                current.rotate(1)

                current.move(0, 1)
                if current.check_floor():
                    if rotations < 15:
                        fall = False
                        rotations += 1
                current.move(0, -1)

            elif event.key == pygame.K_UP:
                if canSwitch:
                    canSwitch = False
                    


            # speed down
            elif event.key == pygame.K_s:
                if not speedUp:
                    fall_speed /= 10
                    speedUp = True
                    last_fall -= 2
            
            # force down
            elif event.key == pygame.K_DOWN:
                
                while not current.check_floor():
                    current.move(0, 1)

                current.move(0,-1)
                last_fall -= 2

        elif event.type == pygame.KEYUP:

            # stop speed down
            if event.key == pygame.K_s:
                if speedUp:
                    fall_speed *= 10
                    speedUp = False
                

        elif event.type == pygame.QUIT:
            game.running = False
    

    # for getting the next three items
    if len(bag) >= 3:
        game.render(bag[:3])

    elif len(bag) > 0:
        amount = len(bag)

        temp = bag.copy()
        temp.extend(next_bag[:3 - amount])
        game.render(temp)
    else:
        bag = next_bag.copy()
        next_bag = pieces.copy()
        random.shuffle(next_bag)
        game.render(bag[:3])



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

        if current.check_floor():

            if fall:
                # turn piece into resting blocks
                for block in current.blocks:
                    game.resting.append(Block(block.x, block.y-1, block.color, colorByName=False))

                
                # detect if a row was made
                for y in range(1, 21):
                    row = list(filter(lambda block: block.y == y, game.resting))

                    if len(row) == 10:
                        # set the fade increments for blocks
                        for block in row:
                            
                            fade_increments = []
                            for color in block.color:
                                fade_increments.append((255 - color) // 15)

                            block.fade_increments = tuple(fade_increments)


    
                # for getting the next three items
                if len(bag) >= 3:
                    game.render(bag[:3])
                elif len(bag) > 0:
                    amount = len(bag)

                    temp = bag.copy()
                    temp.extend(next_bag[:3 - amount])
                    game.render(temp)
                else:
                    bag = next_bag.copy()
                    next_bag = pieces.copy()
                    random.shuffle(next_bag)
                    game.render(bag[:3])


                # make new falling piece
                current = Piece(5, 1, bag.pop(0))
                rotations = 0

                canSwitch = True

            else:
                fall = True
                current.move(0, -1)

    
    current.render()

    if display_until > time.time():
        text = game.font.render(f'Speed Level {speedLevel}', True, (0, 0 ,0))
        textRect = text.get_rect() 
        textRect.center = (game.width // 2, game.height // 2) 
        game.screen.blit(text, textRect)


    pygame.display.update()

    game.clock.tick(5)