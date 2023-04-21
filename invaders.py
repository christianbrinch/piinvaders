''' Python clone of Space Invaders, C. Brinch, 2019 '''

import numpy as np
import pygame
import bitmaps as bm
from PIL import Image

SIZE = height, width = 256, 224
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
GREEN = (32, 180, 10, 255)
RED = (252, 72, 8, 255)

objects = {
           
           'alshot': {'refpos': [0, 0],
                       'active': 0,
                       'direction': (0, 4),
                       'cooldown': 48,
                       'sprite': [bm.alshot,
                                  bm.alien_shot_exploding]
                       },
           }


def alienscore(row):
    ''' Determine the score for hitting an alien '''
    scoretable = [10, 10, 20, 20, 30]
    return scoretable[row]


def saucerscore(shots):
    ''' Determine the score for hitting the saucer.
        It should be modulo 16, but the original Space Invaders has a bug.
    '''
    scoretable = [100, 50, 50, 100, 150, 100, 100, 50, 300, 100, 100, 100, 50, 150, 100, 50]
    return scoretable[shots % 15]


def alienreloadtime(score):
    ''' Given player score, set the alien reload time '''
    reloadlimits = [200, 1000, 2000, 3000]
    reloadtimes = [48, 16, 11, 8, 7]
    return reloadtimes[np.searchsorted(reloadlimits, score)]


def alienfirecolumn(tick):
    ''' This table gives the column from which the aliens fire '''
    column = [1, 7, 1, 1, 1, 4, 11, 1, 6, 3, 1, 1, 11, 9, 2, 8]
    return column[tick]


class CanvasClass(np.ndarray):
    ''' A class to contain everything related to drawing on screen '''

    def __init__(self, SIZE):
        np.ndarray.__init__(self)
        self.screen = pygame.display.set_mode((SIZE[1], SIZE[0]))

    def drawsprite(self, bitmap, position):
        ''' Put bitmap on the canvas at position '''
        self[position[1]:position[1]+bitmap.shape[0],
             position[0]:position[0]+bitmap.shape[1]] = bitmap

    def write(self, text, position):
        ''' Write text to the screen at position '''
        for idx, letter in enumerate(text):
            self.drawsprite(bm.fonts[letter], tuple(map(sum, zip(position, (8*idx, 0)))))

    def overlayfilter(self):
        ''' Filter the canvas through the overlay gel '''
        return super() * bm.overlay_gel

    def update(self):
        ''' Update screen and flip display '''
        surface = pygame.surfarray.make_surface(self.overlayfilter().T)
        for idx, color in enumerate([BLACK, WHITE, GREEN, RED]):
            surface.set_palette_at(idx, color)
        self.screen.blit(surface, (0, 0))
        pygame.display.update()


class GameObject():
    ''' A base class to contain each game element '''

    def __init__(self, attr):
        self.edgeflag = 0
        self.refpos = np.array([0,0])
        self.active = 0
        self.direction = (0,0)
        self.cooldown = 0
        self.sprite = []
        self.movecounter = 0
        self.hittime = 0

        for key in attr:
            self.__dict__[key] = attr[key]

    def move(self, edge=0):
        ''' Move the game element '''
        self.refpos += np.array(self.direction)
        self.refpos[0] = np.maximum(0+edge, self.refpos[0])
        self.refpos[0] = np.minimum(self.refpos[0], width-self.sprite[0].shape[1]-edge)
        if (self.refpos[0] == 0 and self.direction[0] < 0) or \
           (self.refpos[0] == width-self.sprite[0].shape[1] and self.direction[0] > 0):
            self.edgeflag = 1

    def edgedetect(self):
        ''' Check if sprite has hit the border. TODO: Remove code from move() '''
        if self.refpos[1] <= 32 or self.refpos[1]+8 >= 236:
            return True
        if (self.refpos[0] == 0 and self.direction[0] < 0) or \
           (self.refpos[0] == width-len(self.sprite[0][0]) and self.direction[0] > 0):
            return True
        return False

    def update(self, canvas, tick=0):
        if self.active>1:
            canvas.drawsprite(self.explode, self.refpos)
        elif self.active==1:
            canvas.drawsprite(self.sprite[tick], self.refpos)
        else:
            canvas.drawsprite(0*self.explode, self.refpos)        



class SpaceInvaders():
    ''' A class to contain all the game house keeping '''

    def __init__(self):
        self.highscore = 0
        self.score = 0
        self.credit = 0
        self.numberofshots = 0
        self.elements = {"aliens" : [GameObject({'refpos': np.array([24, 120])+np.array([+16*(i % 11), -16*(i // 11)]),
                                                 'active': 1,
                                                 'direction': (2,0),
                                                 'sprite': bm.aliens[i//22],
                                                 'explode': bm.alien_exploding
                                                }) for i in range(55)],
                         "alshot" : GameObject(objects["alshot"]),
                         "player" : GameObject({'refpos': np.array([7, 216]), 
                                                'sprite': [bm.tank]}),
                         "plshot" : GameObject({'direction': (0,-4), 
                                                'sprite': [bm.shot],
                                                'explode': bm.shot_exploding}),
                         "saucer" : GameObject({'refpos': np.array([0,40]),
                                                'cooldown': 600,
                                                'sprite': [bm.saucer],
                                                'explode': bm.saucer_exploding})}

    def update(self, canvas, gameon):
        canvas.write("score<1>_hi-score_score<2>", (8, 8))
        canvas.write(str(self.score).zfill(4)+"____"+str(self.highscore).zfill(4)+"______0000", (24, 24))
        canvas.write("credit_"+str(self.credit).zfill(2), (134, 240))
        if not gameon:
            canvas.write("play", (96, 64))
            canvas.write("space_invaders", (56, 88))
            canvas.write("*score_advance_table*", (32, 120))
            canvas.drawsprite(bm.saucer, (60, 136))
            canvas.write("=?_mystery", (80, 136))
            canvas.drawsprite(bm.alienC[0][2:], (64, 144))
            canvas.write("=30_points", (80, 152))
            canvas.drawsprite(bm.alienB[1], (64, 160))
            canvas.write("=20_points", (80, 168))
            canvas.drawsprite(bm.alienA[0], (64, 176))
            canvas.write("=10_points", (80, 184))
        else:
            canvas.write("3", (6, 240))
            _ = [canvas.drawsprite(bm.tank,  (i, 240)) for i in [22, 38]]
            canvas.write("credit_"+str(self.credit).zfill(2), (134, 240))
            canvas.drawsprite(np.array([[1 for _ in range(224)]]), (0, 239))
        canvas.update()
        

    def shields(self, canvas):
        _ = [canvas.drawsprite(bm.shield, (30+45*i, 192)) for i in range(4)]
        



# im = Image.fromarray(canvas*250)
# im.save("screen.gif")

pygame.init()

def main():
    ''' Main game loop '''
    clock = pygame.time.Clock()
    canvas = CanvasClass(SIZE)
    game = SpaceInvaders()
    gameon = False

    game.update(canvas, gameon)

    while not gameon:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    game.credit += 1
                    game.update(canvas, gameon)
                if event.key == pygame.K_1 and game.credit > 0:
                    game.credit -= 1
                    gameon = True
                    canvas.fill(0)
                    game.update(canvas,gameon)
                    
    tick = 0

    game.shields(canvas)   

    while gameon:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameon = False

        # Get player input
        key = pygame.key.get_pressed()
        if key[pygame.K_q]:
            pygame.quit()
        elif key[pygame.K_SPACE] and game.elements['plshot'].cooldown == 0 and game.elements['plshot'].active == 0 and game.elements['player'].active:
            game.elements['plshot'].refpos = game.elements['player'].refpos+np.array([8, 0])
            game.elements['plshot'].active = 1
            game.elements['plshot'].cooldown = 5
            game.numberofshots += 1
        elif key[pygame.K_SPACE] and game.elements['player'].active == 0:
            game.elements['player'].active = 1
            game.elements['plshot'].cooldown = 5
        elif key[pygame.K_RIGHT]:
            game.elements['player'].direction = (1, 0)
        elif key[pygame.K_LEFT]:
            game.elements['player'].direction = (-1, 0)

        # Move player and draw player
        if game.elements['player'].active:
            game.elements['player'].move(7)
            game.elements['player'].direction = (0, 0)
            game.elements['player'].update(canvas)

        # Move player's shot and draw shot
        game.elements['plshot'].cooldown = np.maximum(game.elements['plshot'].cooldown-1, 0)
        if game.elements['plshot'].active:
            if game.elements['plshot'].edgedetect():
                game.elements['plshot'].active = (game.elements['plshot'].active+1)%3
                game.elements['plshot'].update(canvas)
            else:
                game.elements['plshot'].move()
                game.elements['plshot'].update(canvas)

        
        if game.elements['plshot'].active == 1:
            if sum([sum(canvas.screen.get_at([game.elements['plshot'].refpos[0],game.elements['plshot'].refpos[1]+i])[:2]) for i in range(4)]) != 0:
                # Shot has hit something. What is it?
                # Is it an alien?
                for number, alien in enumerate(game.elements['aliens']):
                    if alien.active == 1:
                        alienpos = (alien.refpos[0], alien.refpos[1])
                        if game.elements['plshot'].refpos[0] >= alienpos[0] and game.elements['plshot'].refpos[0] <= alienpos[0]+16 and game.elements['plshot'].refpos[1] >= alienpos[1] and game.elements['plshot'].refpos[1] <= alienpos[1]+12:
                            canvas.drawsprite(bm.alien_exploding, alienpos)
                            game.elements['aliens'][number].active = 2
                            game.elements['plshot'].active = 0
                            game.elements['aliens'][number].hittime = tick
                            game.score += alienscore(number // 11)
                # Or is it an alien shot?
                # pass
                # If not, then is is either a shield or the saucer
                # Has player shot hit shield?
                if game.elements['plshot'].refpos[1] > 170:
                    # Could be shield
                    target = canvas[game.elements['plshot'].refpos[1]:game.elements['plshot'].refpos[1]+8,
                                 game.elements['plshot'].refpos[0]-4:game.elements['plshot'].refpos[0]+4]
                    canvas.drawsprite(target-(np.logical_and(target,bm.shot_exploding).astype(int)), [game.elements['plshot'].refpos[0]-4,game.elements['plshot'].refpos[1]])
                    game.elements['plshot'].active=0
                # Then it must be the saucer
                if game.elements['plshot'].refpos[1] < 48 and game.elements['saucer'].active == 1:
                    game.elements['saucer'].active = 2
                    game.elements['saucer'].update(canvas)
                    game.elements['plshot'].active = 0
                    game.elements['saucer'].hittime = tick
                    game.score += saucerscore(game.numberofshots)
                
        
        
        
        '''
            
        # Here goes alien shots
        shotnumber = tick % 3
        alshot[shotnumber].cooldown = np.maximum(alshot[shotnumber].cooldown-1, 0)
        if shotnumber == 0:
            shotcolumn = canvas[48:192, player.refpos[0]+7]
        elif shotnumber == 1:
            column = alienfirecolumn(tick % 15)-1
            shotcolumn = canvas[48:192, (aliens.refpos[0]+16*column)+8]
        else:
            column = alienfirecolumn((tick % 9)+6)
            shotcolumn = canvas[48:192, (aliens.refpos[0]+16*column)+8]

        if min([item.movecounter for idx, item in enumerate(alshot) if idx != shotnumber]) >= alshot[shotnumber].cooldown \
                and sum(shotcolumn) != 0 and alshot[shotnumber].active == 0:
            alshot[shotnumber].active = 1
            alshot[shotnumber].movecounter = 0
            alshot[shotnumber].cooldown = alienreloadtime(0)
            for idx, ypos in enumerate(reversed(shotcolumn)):
                if ypos == 1:
                    break
            if shotnumber == 0:
                alshot[shotnumber].refpos = [player.refpos[0]+8, 192-idx]
            else:
                alshot[shotnumber].refpos = [(aliens.refpos[0]+16*column)+8, 192-idx]

        if alshot[shotnumber].active == 1:
            alshot[shotnumber].move()
            alshot[shotnumber].movecounter += 1
            if alshot[shotnumber].edgedetect():
                alshot[shotnumber].active = 2

        canvas.drawsprite(alshot[shotnumber].sprite[alshot[shotnumber].active]
                          [tick % 4], alshot[shotnumber].refpos)

        if alshot[shotnumber].active > 1:
            alshot[shotnumber].active = (alshot[shotnumber].active+1) % 4
        '''
            
        # Flying saucer
        game.elements['saucer'].cooldown = np.maximum(game.elements['saucer'].cooldown-1, 0)
        if not game.elements['saucer'].active:  # Saucer is inactive, check if it is time for saucer
            if game.elements['saucer'].cooldown == 0:  # add check for squigly and alien rack size
                game.elements['saucer'].cooldown = 600
                game.elements['saucer'].active = 1
                game.elements['saucer'].direction = (2*(game.numberofshots % 2) - 1, 0)
                game.elements['saucer'].refpos[0] = game.elements['saucer'].direction[0] % (width-24)
        elif game.elements['saucer'].active == 1:  # Saucer is active, move it and check if escaped
            if game.elements['saucer'].edgedetect():
                game.elements['saucer'].active = 0 # saucer has escaped
                canvas.drawsprite(0.*bm.saucer, game.elements['saucer'].refpos) # erase saucer
            else:
                game.elements['saucer'].move()
                game.elements['saucer'].update(canvas)
        else: # Saucer was hit. Keep the saucer explosion for a second and then erase
            if tick-game.elements['saucer'].hittime == 30:
                game.elements['saucer'].active = 0
                game.elements['saucer'].update(canvas)

        
        # The Aliens
        number = tick % 55
        game.elements['aliens'][0].edgeflag = np.logical_or(game.elements['aliens'][0].edgeflag, game.elements['aliens'][number].edgedetect())
        if number == 0:  # Move the rack once every cycle through rack
            if game.elements['aliens'][0].edgeflag:  # Drop rack if edge has been detected
                for i in range(55):
                    game.elements['aliens'][i].refpos += np.array([0, 8])
                    game.elements['aliens'][i].direction = (-1*game.elements['aliens'][i].direction[0], 0)
                    game.elements['aliens'][i].edgeflag = 0
        if game.elements['aliens'][number].active:
            game.elements['aliens'][number].move()
            game.elements['aliens'][number].update(canvas, tick%2)
        
        if game.elements['aliens'][number].active > 1:
            if tick-game.elements['aliens'][number].hittime > 10:
                game.elements['aliens'][number].active = 0
                game.elements['aliens'][number].update(canvas)
        

        tick += 1
        clock.tick(60)
        game.update(canvas, gameon)
        


if __name__ == '__main__':
    main()
