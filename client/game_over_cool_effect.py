

#Dont touch this file zack, trust
def start_screen(self):
    pygame.init()
    
    game_started = False

    pygame.mixer.music.set_volume(0.03)
    
    #It might seem confusing whats happeneing here but dw about it, just making sure blocks are spaced out
    x_pos = [0, 4, 8, 12, 0, 4, 8]
    shuffle(x_pos)

    pieces = [

        Piece(x_pos[0], randint(-15, 0), 'T'), 
        Piece(x_pos[1], randint(-15, 0), 'L'), 
        Piece(x_pos[2], randint(-15, 0), 'BL'), 
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
                    
        # self.screen.fill((0,0,0))
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
