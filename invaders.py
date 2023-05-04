''' Python clone of Space Invaders, C. Brinch, 2019 '''

import numpy as np
import pygame
import time
import bitmaps as bm
from PIL import Image

SIZE = height, width = 256, 224
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
GREEN = (32, 180, 10, 255)
RED = (252, 72, 8, 255)


def alienscore(row):
    ''' Determine the score for hitting an alien '''
    scoretable = [10, 10, 20, 20, 30]
    return scoretable[row]


def saucerscore(shots):
    ''' Determine the score for hitting the saucer.
        It should be modulo 16, but the original Space Invaders has a bug.
    '''
    scoretable = [100, 50, 50, 100, 150, 100, 100,
                  50, 300, 100, 100, 100, 50, 150, 100, 50]
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


def DrawAlien(alienptr, game, canvas):
    ''' Draw aliens one at the time '''
    row, col = alienptr // 11, alienptr % 11
    if game.aliens.timer > 0:
        canvas.drawsprite(bm.alien_exploding,
                          game.aliens.refpos+game.aliens.hit)
        game.aliens.timer -= 1
        if game.aliens.timer == 0:
            canvas.drawsprite(0*bm.alien_exploding,
                              game.aliens.refpos+game.aliens.hit)
            game.player.shot.status = 0
            game.aliens.hit = None
    canvas.drawsprite(bm.aliens[alienptr//22][game.beat %
                      2], game.aliens.refpos+16*np.array([col, -row]))
    if game.aliens.direction[0] > 0:
        edge = 221
    else:
        edge = 2
    if sum([canvas.screen.get_at([edge, int(i)])[0] for i in np.linspace(49, 238, 190)]):
        game.aliens.edgeflag = True

    check = False
    while not check:
        alienptr = (alienptr+1) % 55
        if alienptr == 0:
            if game.aliens.edgeflag:
                game.aliens.refpos += np.array([0, 8])
                game.aliens.direction = -1*game.aliens.direction
                game.aliens.edgeflag = False
            else:
                game.aliens.refpos += game.aliens.direction
        if game.aliens.rack[alienptr] == 1:
            check = True
    return alienptr


def GameObj0(key, game, canvas, clock):
    if game.player.exploding:
        game.aliens.enableFire = 0
        game.aliens.fireDelay = 30
        # Optimize this
        timer = 12
        while timer > 0:
            canvas.drawsprite(bm.tank_exploding[timer % 2], game.player.refpos)
            game.update(canvas)
            for _ in range(5):
                clock.tick(60)
            timer -= 1

        canvas.drawsprite(0*bm.tank, game.player.refpos)
        game.update(canvas)
        game.player.exploding = 0
        game.player.status = 0
        # Here goes other player dies code such as extracting live etc.
        return
    elif game.player.status:
        if key[pygame.K_LEFT]:
            game.player.move(np.array([-1, 0]))
        elif key[pygame.K_RIGHT]:
            game.player.move(np.array([1, 0]))

        canvas.drawsprite(game.player.sprite, game.player.refpos)


def GameObj1(game, canvas):
    if game.player.shot.status:
        if game.player.shot.status == 1:
            game.player.shot.pos = np.array([game.player.refpos[0]+8, 208])
            game.player.shot.status = 2
        elif game.player.shot.status == 2:
            game.player.shot.pos += np.array([0, -4])
            canvas.drawsprite(game.player.shot.sprite, game.player.shot.pos)
            if game.player.shot.pos[1] < 40:
                # Escaped
                game.player.shot.status = 3
                game.player.shot.timer = 10
                return
            if sum([sum(canvas.screen.get_at(game.player.shot.pos-np.array([0, i]))[:2]) for i in [1, 2]]):
                if game.player.shot.pos[1] < 50:
                    # Saucer
                    game.saucer.explode = 10
                    game.saucer.status = 2
                    canvas.drawsprite(0 * bm.shot, game.player.shot.pos)
                    game.player.shot.status = 0
                    game.player.score += saucerscore(game.player.numberofshots)
                else:
                    # Aliens
                    yr = game.aliens.refpos[1]+16
                    row = (yr-game.player.shot.pos[1])//16
                    xr = game.aliens.refpos[0]
                    col = (game.player.shot.pos[0]-xr)//16
                    if 0 <= row < 6 and 0 <= col < 11:
                        if game.aliens.rack[row*11+col] == 0:
                            game.player.shot.status = 3
                            game.player.shot.timer = 10
                            return
                        else:
                            game.player.shot.status = 5
                            game.aliens.rack[row*11+col] = 0
                            game.player.score += alienscore(row)
                            canvas.drawsprite(
                                0 * bm.shot, [game.player.shot.pos[0], game.player.shot.pos[1]])
                            canvas.drawsprite(
                                bm.alien_exploding, game.aliens.refpos+16*np.array([col, -row]))
                            game.aliens.timer = 16
                            game.aliens.hit = 16*np.array([col, -row])
                            return
                    game.player.shot.status = 3
                    game.player.shot.timer = 10
                    for i in range(3):
                        game.aliens.shots[i].status = 0
                        canvas.drawsprite(
                            0*bm.alien_shot_exploding, game.aliens.shots[i].pos)
                    return
        elif game.player.shot.status == 3:
            if game.player.shot.timer == 10:
                # Erase shot
                canvas.drawsprite(
                    0 * bm.shot, [game.player.shot.pos[0], game.player.shot.pos[1]])
                target = canvas[game.player.shot.pos[1]-6:game.player.shot.pos[1]+8-6,
                                game.player.shot.pos[0]-4:game.player.shot.pos[0]+4]
                canvas.drawsprite(np.logical_or(target, bm.shot_exploding.astype(int)), [
                                  game.player.shot.pos[0]-4, game.player.shot.pos[1]-6])

            game.player.shot.timer -= 1

            if game.player.shot.timer == 0:
                game.player.shot.status = 0
                game.player.shot.collisionflag = 0

                target = canvas[game.player.shot.pos[1]-6:game.player.shot.pos[1]+8-6,
                                game.player.shot.pos[0]-4:game.player.shot.pos[0]+4]
                canvas.drawsprite(target-np.logical_and(target, bm.shot_exploding.astype(int)),
                                  [game.player.shot.pos[0]-4, game.player.shot.pos[1]-6])


def GameObj2(game, canvas, beat):
    j = beat % 3
    if j == 2 and game.saucer.status:
        return

    if game.aliens.shots[j].status == 1:
        game.aliens.shots[j].pos += np.array([0, game.aliens.shotspeed])
        game.aliens.shots[j].movecounter += 1
        canvas.drawsprite(
            game.aliens.shots[j].sprite[beat % 4], game.aliens.shots[j].pos)
        if sum([sum(canvas.screen.get_at(game.aliens.shots[j].pos+np.array([0, 8+i]))[:2]) for i in range(4)]):
            if 225 > game.aliens.shots[j].pos[1] >= 208 and game.player.status:
                game.player.exploding = 1
            # collision detected
            game.aliens.shots[j].status = 2
            game.aliens.shots[j].timer = 10
        if game.aliens.shots[j].pos[1] >= 233:
            # Shot left play field
            game.aliens.shots[j].status = 2
            game.aliens.shots[j].timer = 10

    elif game.aliens.shots[j].status == 2:
        # blow up shot
        canvas.drawsprite(bm.alien_shot_exploding, game.aliens.shots[j].pos)
        game.aliens.shots[j].timer -= 1
        if game.aliens.shots[j].timer == 0:
            game.aliens.shots[j].status = 0
            canvas.drawsprite(0*bm.alien_shot_exploding,
                              game.aliens.shots[j].pos)

    else:
        game.aliens.shots[j].movecounter = 0
        if not any([game.aliens.shots[i].status for i in [0, 1, 2] if i != j]) and game.player.status:
            # Time to fire?
            # x = alienreloadtime(game.player.score)

            if j == 0:
                shotcolumn = canvas[48:192, game.player.refpos[0]+7]
            elif j == 1:
                column = alienfirecolumn(beat % 15)-1
                shotcolumn = canvas[48:192,
                                    (game.aliens.refpos[0]+16*column)+8]
            else:
                column = alienfirecolumn((beat % 9)+6)
                shotcolumn = canvas[48:192,
                                    (game.aliens.refpos[0]+16*column)+8]
            if sum(shotcolumn) != 0:
                for idx, ypos in enumerate(reversed(shotcolumn)):
                    if ypos == 1:
                        break
                if j == 0:
                    game.aliens.shots[j].pos = np.array(
                        [game.player.refpos[0]+7, 192-idx])
                else:
                    game.aliens.shots[j].pos = np.array(
                        [(game.aliens.refpos[0]+16*column)+8, 192-idx])
                game.aliens.shots[j].status = 1


def Saucer(game, canvas):
    if not game.saucer.status:
        game.saucer.status = 1
        game.saucer.direction = np.array(
            [2*(game.player.numberofshots % 2) - 1, 0])
        game.saucer.pos = np.array([game.saucer.direction[0] % (width-24), 40])
    elif game.saucer.status == 1:
        if game.saucer.direction[0] > 0:
            edge = 218
        else:
            edge = 5
        if canvas.screen.get_at([edge, 45])[0]:
            canvas.drawsprite(0*game.saucer.sprite, game.saucer.pos)
            game.saucer.status = 0
            game.saucer.timer = 600
            return
        else:
            game.saucer.pos += game.saucer.direction
            canvas.drawsprite(game.saucer.sprite, game.saucer.pos)
    elif game.saucer.status == 2:
        canvas.drawsprite(bm.saucer_exploding, game.saucer.pos)
        game.saucer.explode -= 1
        if game.saucer.explode == 0:
            game.saucer.status = 0
            game.saucer.timer = 600
            canvas.drawsprite(0*game.saucer.sprite, game.saucer.pos)


def PlrFire(key, game):
    if key[pygame.K_SPACE]:
        # is player active?
        if not game.player.status:
            game.player.status = True
            game.player.shot.cooldown = 5
            game.aliens.enableFire = 1
        elif game.player.shot.cooldown == 0:
            # is a shot already on screen?
            if game.player.shot.status == 0:
                game.player.shot.status = 1
            else:
                game.player.numberofshots += 1
    if game.player.shot.cooldown > 0:
        game.player.shot.cooldown += -1


def CountAliens(game):
    game.aliens.remaining = sum(game.aliens.rack)


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
            self.drawsprite(bm.fonts[letter], tuple(
                map(sum, zip(position, (8*idx, 0)))))

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


class shotInfo():
    ''' A class to keep shot info '''

    def __init__(self, sprite):
        self.status = 0
        self.pos = np.array([0, 0])
        self.collisionflag = 0
        self.cooldown = 0
        self.timer = 0
        self.sprite = sprite


class playerInfo():
    ''' A class to keep player info '''

    def __init__(self):
        self.score = 0
        self.status = 0
        self.refpos = np.array([16, 216])
        self.shot = shotInfo(bm.shot)
        self.exploding = 0
        self.numberofshots = 0
        self.sprite = bm.tank

    def move(self, direction):
        ''' Move the game element '''
        self.refpos += direction
        self.refpos[0] = np.maximum(16, self.refpos[0])
        self.refpos[0] = np.minimum(self.refpos[0], 201-16)


class alienInfo():
    ''' A class to keep alien info '''

    def __init__(self):
        self.rack = 55*[1]
        self.refpos = np.array([24, 120])
        self.hit = None
        self.timer = 0
        self.direction = np.array([2, 0])
        self.edgeflag = False
        self.enableFire = 1
        self.shotspeed = 4
        self.shots = [shotInfo(bm.rolling), shotInfo(
            bm.plunger), shotInfo(bm.squigly)]


class saucerInfo():
    ''' A class to keep saucer info '''

    def __init__(self):
        self.status = 0
        self.pos = None
        self.direction = None
        self.timer = 600
        self.direction = 1
        self.explode = 0
        self.sprite = bm.saucer


class SpaceInvaders():
    ''' A class to contain all the game house keeping '''

    def __init__(self):
        self.highscore = 0
        self.credit = 0
        self.alienexplosion = 0
        self.beat = 0
        self.player = playerInfo()
        self.aliens = alienInfo()
        self.saucer = saucerInfo()

    def bumpcredits(self, canvas):
        self.credit += 1
        if self.credit > 99:
            self.credit = 0
        canvas.write(str(self.credit).zfill(2), (141, 240))

    def promptPlayer(self, canvas, clock):
        canvas.fill(0)
        for isr in range(176):
            self.update(canvas)
            canvas.write("play_player<1>", (64, 120))
            if not (isr // 4) % 2:
                canvas.write("____", (24, 24))
                canvas.update()
            clock.tick(60)
        canvas.fill(0)

    def update(self, canvas):
        canvas.write("score<1>_hi-score_score<2>", (8, 8))
        canvas.write(str(self.player.score).zfill(4)+"____" +
                     str(self.highscore).zfill(4)+"______0000", (24, 24))
        canvas.write("credit_"+str(self.credit).zfill(2), (134, 240))
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

    gamemode = False

    while not gamemode:
        canvas.fill(0)

        if game.credit == 0:
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
        elif game.credit == 1:
            canvas.write("push", (96, 88))
            canvas.write("only_1player_button", (40, 120))
        else:
            canvas.write("push", (96, 88))
            canvas.write("1_or_2player_button", (40, 120))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    game.bumpcredits(canvas)
                if event.key == pygame.K_1 and game.credit > 0:
                    game.credit -= 1
                    game.player.score = 0
                    gamemode = True
                    game.promptPlayer(canvas, clock)
                    game.shields(canvas)
                    canvas.write("3", (6, 240))
                    _ = [canvas.drawsprite(bm.tank,  (i, 240))
                         for i in [22, 38]]
                    canvas.drawsprite(
                        np.array([[1 for _ in range(224)]]), (0, 239))

        game.update(canvas)

    alienptr = 0

    while gamemode:
        # main game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gamemode = False
        # Get player input
        key = pygame.key.get_pressed()

        # Interupt triggered code
        alienptr = DrawAlien(alienptr, game, canvas)
        # RunGameObjs()
        GameObj0(key, game, canvas, clock)  # Move player
        GameObj1(game, canvas)  # Move player shot
        if game.saucer.timer <= 0 and game.aliens.shots[2].status == 0:
            Saucer(game, canvas)

        GameObj2(game, canvas, game.beat)  # Alien rolling shot

        # Game loop
        PlrFire(key, game)

        CountAliens(game)
        if game.aliens.remaining == 0:
            gamemode = False

        AShotReloadRate = alienreloadtime(game.player.score)
        # Check for extra ship award
        if game.aliens.remaining < 9:
            game.aliens.shotspeed = 5

        game.beat += 1
        game.saucer.timer -= 1
        clock.tick(60)
        game.update(canvas)


if __name__ == '__main__':
    main()
