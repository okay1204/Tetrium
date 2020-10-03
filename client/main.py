# pylint: disable=no-member, unused-wildcard-import
import pygame
from game import *
import time
import random

pieces = ["T", "L", "BL", "S", "BS", "I", "O"]
bag = pieces.copy()


fall_speed = 1 # means once per second
last_fall = time.time() + fall_speed
fall = True

current = Piece(5, 1, bag.pop(random.randint(0, len(bag)-1)))

speedUp = False


rotations = 0
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
    

    if not bag:
        bag = pieces.copy()
        
    game.render()

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
                        # remove the row
                        for block in row:
                            game.resting.remove(block)

                        for block in game.resting:
                            if block.y < y:
                                block.y += 1
    
                game.render()


                # make new falling piece
                current = Piece(5, 1, bag.pop(random.randint(0, len(bag)-1)))
                rotations = 0

            else:
                fall = True
                current.move(0, -1)

    
    current.render()
    pygame.display.update()

    game.clock.tick(60)