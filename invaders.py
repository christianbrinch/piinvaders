''' Python clone of Space Invaders, C. Brinch, 2019 '''

import numpy as np
import pygame
import bitmaps as bm
pygame.init()

size = width, height = 224, 256
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
GREEN = (32, 180, 10, 255)
RED = (252, 72, 8, 255)


def overlay(x, y):
    ''' Emulate the gel overlay '''
    if 31 < y <= 63:
        # Red/orange top part
        color = RED
    elif 183 < y <= 238:
        # Green shield and player
        color = GREEN
    elif (y > 239) and (24 < x < 135):
        # Green extra lives
        color = GREEN
    else:
        # everything else white
        color = WHITE

    return [BLACK, color]


def write(text, screen, x, y):
    ''' Write text to the screen at position (x,y) '''
    for position, letter in enumerate(text):
        draw(bm.fonts[letter], screen, 8*position+x, y)


def draw(sprite, screen, x, y):
    ''' Draw a sprite on the screen at position (x,y) '''
    for j, line in enumerate(sprite):
        for i, pix in enumerate(line):
            color = overlay(x+i, y-len(sprite)+j)
            pygame.draw.line(screen, color[pix], (x+i, y-len(sprite)+j), (x+i, y-len(sprite)+j))


class BaseClass():
    ''' A base class for all game elements (player, enemies, shots).
        To be extended into specific classes below
    '''

    def __init__(self, refpos, racksize, spacing, cols):
        self.refpos = refpos
        self.rack = np.array([1 for i in range(racksize)])
        self.spacing = spacing
        self.cols = cols

    def sprite(self, number):
        ''' Dummy method - will be overwritten '''

    def position(self, number):
        ''' Return the position on the screen, given the element number '''
        return (self.refpos[0]+self.spacing*(number % self.cols),
                self.refpos[1]-self.spacing*(number // self.cols))

    def draw_sprite(self, screen, number):
        ''' Draw the element on the screen at its position '''
        draw(self.sprite(number), screen, *self.position(number))


class EnemyClass(BaseClass):
    ''' An extenstion of the base class to hold the enemy rack '''

    def __init__(self):
        BaseClass.__init__(self, [24, 136], 55, 16, 11)
        self.direction = 1

    def sprite(self, number):
        ''' Determine which sprite to use, given element number '''
        sprites = [np.zeros([8, 16], dtype=int), bm.aliens[number//22]
                   [self.refpos[0]//2 % 2], bm.alien_exploding]
        return sprites[self.rack[number]]

    def move(self):
        ''' Update the reference position
            TODO: Shrink rack if outermost columns are shot
        '''
        if self.refpos[0] > 0 and self.refpos[0] < width-176:
            self.refpos[0] += 2*self.direction
        else:
            self.refpos[1] += 8
            self.direction *= -1
            self.refpos[0] += 2*self.direction


class PlayerClass(BaseClass):
    ''' An extenstion of the base class to hold the player.
        This class will only ever hold one element.
    '''

    def __init__(self):
        BaseClass.__init__(self, [0, 223], 1, 1, 1)
        self.lives_left = 3
        self.score = 0

    def sprite(self, number):
        ''' Select player sprite '''
        return bm.tank

    def move(self, direction):
        ''' Update player position '''
        self.refpos[0] += direction
        self.refpos[0] = np.maximum(0, self.refpos[0])
        self.refpos[0] = np.minimum(self.refpos[0], width-16)

    def update_score(self, screen):
        ''' Update score board '''
        self.score += 10
        write("___"+str(self.score).zfill(4), screen, 0, 31)


class ShotClass(BaseClass):
    ''' An extenstion of the base class to hold the player shot.
        This class will only ever hold one element.
    '''

    def __init__(self):
        BaseClass.__init__(self, [width-1,height-1], 0, 1, 1)
        self.active = 0
        self.shots_fired = 0

    def position(self, number):
        return tuple(self.refpos)

    def sprite(self, number):
        ''' Select shot sprite '''
        sprites = [bm.shot*0, bm.shot, bm.shot_exploding, bm.shot_exploding*0]
        return sprites[self.active]

    def fire(self, position):
        ''' Initiate a shot '''
        self.active = 1
        self.refpos = [position, 215]
        self.shots_fired += 1

    def move(self):
        ''' Update shot position '''
        self.refpos[1] -= 1
        if self.refpos[1] == 40:
            self.active = 2


    def check_collision(self, screen, enemies):
        ''' Check if the shot hits anything '''
        if screen.get_at((self.refpos[0], self.refpos[1]-10)) == WHITE:
            cll = ((self.refpos[0])-enemies.refpos[0]) // 16
            row = (enemies.refpos[1]-(self.refpos[1]-9)) // 16
            enemies.draw_sprite(screen, 11*row+cll)
            self.active = 2
            return 10
        '''
        if screen.get_at((self.refpos[0], self.refpos[1]-10)) == GREEN:
            x, y = self.refpos[0], self.refpos[1]
            buffer = np.array([[1 if screen.get_at(
                (x-4+i, y+j-8)) == GREEN else 0 for j in range(8)] for i in range(8)])
            print(buffer)
            mask = np.logical_and((bm.shot_exploding), buffer).astype(int)

            print(mask)
            draw((buffer+mask) % 2, screen, x-4, y)
        
            self.active = 0
        '''
        return 0


class ShieldClass(BaseClass):
    ''' An extension to the base class to hold the four shields '''

    def __init__(self, screen):
        BaseClass.__init__(self, [31, 207], 4, 45, 4)
        for i in [0, 1, 2, 3]:
            self.draw_sprite(screen, i)

    def sprite(self, number):
        ''' Select shield sprite '''
        return bm.shield


class GameControl():
    ''' A class to contain all the game house keeping '''

    def __init__(self):
        self.highscore = 0
        self.credit = 0

    def welcomescreen(self, screen):
        ''' Draw the welcome screen and wait for game to start '''
        screen.fill(BLACK)
        write("_score<1>_hi-score_score<2>", screen, 0, 15)
        write("___0000____"+str(self.highscore).zfill(4), screen, 0, 31)
        write("play", screen, 100, 64)
        write("space_invaders", screen, 56, 88)
        pygame.display.flip()

    def board(self, screen):
        ''' Draw the initial game board '''
        screen.fill(BLACK)
        write("_score<1>_hi-score_score<2>", screen, 0, 15)
        write("___0000____"+str(self.highscore).zfill(4), screen, 0, 31)
        draw(bm.tank, screen, 0, 223)
        write("3", screen, 8, 247)
        draw(bm.tank, screen, 25, 247)
        draw(bm.tank, screen, 41, 247)
        write("credit_"+str(self.credit).zfill(2), screen, 136, 247)
        pygame.draw.line(screen, GREEN, (0, 239), (width, 239))
        pygame.draw.line(screen, (0,0,255,255), (0, 206), (width, 206))
        pygame.display.flip()

    def insertcoins(self, screen):
        ''' Wait for coins and start game '''
        while True:
            write("credit_"+str(self.credit).zfill(2), screen, 136, 247)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.credit += 1
                    if event.key == pygame.K_1 and self.credit > 0:
                        self.credit -= 1
                        return


def main():
    ''' Main game loop '''
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    game = GameControl()

    game.welcomescreen(screen)
    game.insertcoins(screen)
    game.board(screen)

    enemies = EnemyClass()
    player = PlayerClass()
    shot = ShotClass()
    shields = ShieldClass(screen)

    hit = -10
    i = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Get player input and move player
        key = pygame.key.get_pressed()
        if key[pygame.K_q]:
            pygame.quit()
        elif key[pygame.K_SPACE] and shot.active == 0:
            shot.fire(player.refpos[0]+9)
        elif key[pygame.K_RIGHT]:
            player.move(1)
        elif key[pygame.K_LEFT]:
            player.move(-1)

        # Draw player
        player.draw_sprite(screen, 0)


        for kl in range(4):
            if shot.active == 1:
                print(shot.refpos, shot.active, shot.shots_fired)
                # Move shot
                shot.refpos[1] -= 1
                shot.draw_sprite(screen, shot.active)
                if shot.refpos[1] == 40:
                    shot.active = 2
                    shot.refpos[0] += -3
                    shot.refpos[1] += 3
                if screen.get_at((shot.refpos[0], shot.refpos[1]-6)) == WHITE:
                    shot.active = 0
                    shot.draw_sprite(screen, shot.active)
                    cll = ((shot.refpos[0])-enemies.refpos[0]) // 16
                    row = (enemies.refpos[1]-(shot.refpos[1]-9)) // 16
                    enemies.rack[11*row+cll] = 2
                    enemies.draw_sprite(screen, 11*row+cll)
                    enemies.rack[11*row+cll] = 0
                    player.update_score(screen) 
                if screen.get_at((shot.refpos[0], shot.refpos[1]-6)) == GREEN:
                    shot.active = 0
                    shot.draw_sprite(screen, shot.active)
                    print(shot.refpos, shot.active)
                    #x, y = shot.refpos[0], shot.refpos[1]
                    #buffer = np.array([[1 if screen.get_at((x-3+k, y+j-8)) == GREEN else 0 for k in range(8)] for j in range(8)])
                    #mask = np.logical_and(buffer, np.logical_not(bm.shot_exploding)).astype(int)
                    #draw(mask , screen, x-3, y)
           


        if shot.active > 1:
            shot.draw_sprite(screen, shot.active)
            shot.active = (shot.active + 1) % 4

        # move shot and determine hits
        '''
        if shot.active == 1:
            shot.move(screen)
            hit = shot.check_collision(screen, enemies)
            if hit > -1:
                shot.active = 0
                shot.draw_sprite(screen, 0)
                enemies.rack[hit] = 2
                enemies.draw_sprite(screen, hit)
                enemies.rack[hit] = 0
                player.update_score(screen)
        '''
        # Move and draw enemies
        enemies.draw_sprite(screen, i % 55)

        i += 1
        if i % 55 == 0:
            enemies.move()
                

        # Mysterious ship

        # Enemy shots

        clock.tick(60)
        pygame.display.flip()


if __name__ == '__main__':
    main()
