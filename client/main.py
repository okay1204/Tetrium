# pylint: disable=no-member, unused-wildcard-import
import pygame
from game import *
import time
import random

pieces = ["T", "L", "BL", "S", "BS", "I", "O"]
bag = pieces.copy()


fall_speed = 1 # means once per second
last_fall = time.time() + fall_speed


current = Piece(5, 1, bag.pop(random.randint(0, len(bag)-1)))

holding = ''
holdCount = 0
while game.running:


    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_a:
                if not current.check_left():
                    current.move(-1, 0)
            
            elif event.key == pygame.K_d:
                if not current.check_right():
                    current.move(1, 0)
            
            elif event.key == pygame.K_DOWN:
                
                while not current.check_floor():
                    current.move(0, 1)

                current.move(0,-1)
                

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

            # turn piece into resting blocks
            for block in current.blocks:
                game.resting.append(Block(block.x, block.y-1, block.color, colorByName=False))
            game.render()


            # make new falling piece
            current = Piece(5, 1, bag.pop(random.randint(0, len(bag)-1)))

            

    
    current.render()
    pygame.display.update()

    game.clock.tick(60)