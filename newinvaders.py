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

objects = {'player': {'refpos': [0, 216],
                      'active': 1,
                      'direction': (0, 0),
                      'cooldown': [0],
                      'sprite': [0*bm.tank, bm.tank, 0*bm.tank]
                      },
           'plshot': {'refpos': [0, 0],
                      'active': 0,
                      'direction': (0, -4),
                      'cooldown': 0,
                      'sprite': [0*bm.shot,
                                 bm.shot,
                                 bm.shot_exploding,
                                 0*bm.shot_exploding]
                      },
           'saucer': {'refpos': [0, 40],
                      'active': 0,
                      'direction': (0, 0),
                      'cooldown': 600,
                      'sprite': [0*bm.saucer,
                                 bm.saucer,
                                 bm.saucer_exploding,
                                 0*bm.saucer_exploding]
                      },
           'aliens': {'refpos': [24, 120],
                      'active': [1 for _ in range(55)],
                      'direction': (2, 0),
                      'cooldown': [0],
                      'sprite': [0*bm.alien_exploding,
                                 bm.aliens,
                                 bm.alien_exploding,
                                 0*bm.alien_exploding]
                      },
           'rolling': {'refpos': [0, 0],
                       'active': 0,
                       'direction': (0, 4),
                       'cooldown': 48,
                       'sprite': [4*[0*bm.shot],
                                  bm.rolling,
                                  4*[bm.alien_shot_exploding],
                                  4*[0*bm.alien_shot_exploding]]
                       },
           'plunger': {'refpos': [0, 0],
                       'active': 0,
                       'direction': (0, 4),
                       'cooldown': 48,
                       'sprite': [4*[0*bm.shot],
                                  bm.plunger,
                                  4*[bm.alien_shot_exploding],
                                  4*[0*bm.alien_shot_exploding]]
                       },
           'squigly': {'refpos': [0, 0],
                       'active': 0,
                       'direction': (0, 4),
                       'cooldown': 48,
                       'sprite': [4*[0*bm.shot],
                                  bm.squigly,
                                  4*[bm.alien_shot_exploding],
                                  4*[0*bm.alien_shot_exploding]]
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


pygame.init()


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
        self.refpos = []
        self.active = None
        self.direction = None
        self.cooldown: None
        self.sprite = []
        self.movecounter = 0

        for key in attr:
            self.__dict__[key] = attr[key]

    def move(self):
        ''' Move the game element '''
        self.refpos = list(map(sum, zip(self.direction, self.refpos)))
        self.refpos[0] = np.maximum(0, self.refpos[0])
        self.refpos[0] = np.minimum(self.refpos[0], width-self.sprite[1].shape[1])
        if (self.refpos[0] == 0 and self.direction[0] < 0) or \
           (self.refpos[0] == width-self.sprite[1].shape[1] and self.direction[0] > 0):
            self.edgeflag = 1

    def edgedetect(self, number=0):
        ''' Check if sprite has hot the border. TODO: Remove code from move() '''
        if self.refpos[1] <= 32 or self.refpos[1]+8 >= 236:
            return True
        xcoord = (self.refpos[0]+16*(number % 11))
        if (xcoord == 0 and self.direction[0] < 0) or \
           (xcoord == width-len(self.sprite[2][0]) and self.direction[0] > 0):
            return True
        return False

    def animate(self):
        ''' write some code here '''
        pass


class SpaceInvaders():
    ''' A class to contain all the game house keeping '''

    def __init__(self):
        self.highscore = 0
        self.credit = 0
        self.numberofshots = 0

    def welcomescreen(self, canvas):
        ''' Draw the welcome screen and wait for game to start '''
        canvas.fill(0)
        canvas.write("score<1>_hi-score_score<2>", (8, 8))
        canvas.write("0000____"+str(self.highscore).zfill(4)+"______0000", (24, 24))
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
        while True:
            canvas.write("credit_"+str(self.credit).zfill(2), (134, 240))
            canvas.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.credit += 1
                    if event.key == pygame.K_1 and self.credit > 0:
                        self.credit -= 1
                        return

    def board(self, canvas):
        ''' Draw the initial game board '''
        canvas.fill(0)
        canvas.write("score<1>_hi-score_score<2>", (8, 8))
        canvas.write("0000____"+str(self.highscore).zfill(4), (24, 24))
        _ = [canvas.drawsprite(bm.shield, (30+45*i, 192)) for i in range(4)]
        canvas.drawsprite(bm.tank, (0, 216))
        canvas.write("3", (6, 240))
        _ = [canvas.drawsprite(bm.tank,  (i, 240)) for i in [22, 38]]
        canvas.write("credit_"+str(self.credit).zfill(2), (134, 240))
        canvas.drawsprite(np.array([[1 for _ in range(224)]]), (0, 239))
        canvas.update()


# im = Image.fromarray(canvas*250)
# im.save("screen.gif")


def main():
    ''' Main game loop '''
    clock = pygame.time.Clock()
    canvas = CanvasClass(SIZE)
    game = SpaceInvaders()

    game.welcomescreen(canvas)
    game.board(canvas)

    aliens = GameObject(objects["aliens"])
    alshot = [GameObject(objects["rolling"]), GameObject(
        objects["plunger"]), GameObject(objects["squigly"])]
    player = GameObject(objects["player"])
    plshot = GameObject(objects["plshot"])
    saucer = GameObject(objects["saucer"])

    tick = 0

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get player input
        key = pygame.key.get_pressed()
        if key[pygame.K_q]:
            pygame.quit()
        elif key[pygame.K_SPACE] and plshot.cooldown == 0 and plshot.active == 0:
            plshot.refpos = tuple(map(sum, zip(player.refpos, (8, 0))))
            plshot.active = 1
            plshot.cooldown = 5
            game.numberofshots += 1
        elif key[pygame.K_RIGHT]:
            player.direction = (1, 0)
        elif key[pygame.K_LEFT]:
            player.direction = (-1, 0)

        # Move player and draw player
        player.move()
        player.direction = (0, 0)
        canvas.drawsprite(player.sprite[player.active], player.refpos)

        # Move player's shot and draw shot
        plshot.cooldown = np.maximum(plshot.cooldown-1, 0)
        if plshot.active == 1:
            plshot.move()
            if plshot.edgedetect():
                plshot.active = 2
        canvas.drawsprite(plshot.sprite[plshot.active], plshot.refpos)
        if plshot.active > 1:
            plshot.active = (plshot.active+1) % 4

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

        # Flying saucer
        saucer.cooldown = np.maximum(saucer.cooldown-1, 0)
        if saucer.active == 0:  # Saucer is inactive, check if it is time for saucer
            if saucer.cooldown == 0:  # add check for squigly and alien rack size
                saucer.cooldown = 600
                saucer.active = 1
                saucer.direction = (2*(game.numberofshots % 2) - 1, 0)
                saucer.refpos[0] = saucer.direction[0] % (width-24)
        if saucer.active == 1:  # Saucer is active, move it and check if escaped
            saucer.move()
            if saucer.edgedetect():
                saucer.active = 3
        canvas.drawsprite(saucer.sprite[saucer.active], saucer.refpos)
        if saucer.active > 1:
            saucer.active = (saucer.active+1) % 4

        # The Aliens
        number = tick % 55
        aliens.edgeflag = np.logical_or(aliens.edgeflag, aliens.edgedetect(number))
        if number == 0:  # Move the rack once every cycle through rack
            if aliens.edgeflag:  # Drop rack if edge has been detected
                aliens.refpos = list(map(sum, zip(aliens.refpos, (0, 8))))
                aliens.direction = (-1*aliens.direction[0], 0)
                aliens.edgeflag = 0
            aliens.move()
        canvas.drawsprite(aliens.sprite[aliens.active[0]][number//22][(tick//55) % 2],
                          (aliens.refpos[0]+16*(number % 11), aliens.refpos[1]-16*(number // 11)))

        tick += 1
        clock.tick(60)
        canvas.update()


if __name__ == '__main__':
    main()
