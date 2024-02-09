import pygame
import threading
import time
import numpy as np

SIZE = height, width = 224, 256


def xy(addr):
    absaddr = addr-0x2400
    return absaddr//32, absaddr % 32


def bitlist(x):
    return [int(i) for i in '{:08b}'.format(x)]

# Game data as byte arrays


demoCommands = bytearray([0x01, 0x01, 0x00, 0x00, 0x01, 0x00,
                          0x02, 0x01, 0x00, 0x02, 0x01, 0x00])

alienA0 = [0x00, 0x00, 0x39, 0x79, 0x7A, 0x6E, 0xEC, 0xFA,
           0xFA, 0xEC, 0x6E, 0x7A, 0x79, 0x39, 0x00, 0x00]
alienB0 = [0x00, 0x00, 0x00, 0x78, 0x1D, 0xBE, 0x6C, 0x3C,
           0x3C, 0x3C, 0x6C, 0xBE, 0x1D, 0x78, 0x00, 0x00]
alienC0 = [0x00, 0x00, 0x00, 0x00, 0x19, 0x3A, 0x6D, 0xFA,
           0xFA, 0x6D, 0x3A, 0x19, 0x00, 0x00, 0x00, 0x00]

alienA1 = [0x00, 0x00, 0x38, 0x7A, 0x7F, 0x6D, 0xEC, 0xFA,
           0xFA, 0xEC, 0x6D, 0x7F, 0x7A, 0x38, 0x00, 0x00]
alienB1 = [0x00, 0x00, 0x00, 0x0E, 0x18, 0xBE, 0x6D, 0x3D,
           0x3C, 0x3D, 0x6D, 0xBE, 0x18, 0x0E, 0x00, 0x00]
alienC1 = [0x00, 0x00, 0x00, 0x00, 0x1A, 0x3D, 0x68, 0xFC,
           0xFC, 0x68, 0x3D, 0x1A, 0x00, 0x00, 0x00, 0x00]

squiglyShot = [[0x44, 0xAA, 0x10], [0x88, 0x54, 0x22],
               [0x10, 0xAA, 0x44], [0x22, 0x54, 0x88]]

rollShot = [[0x00, 0xFE, 0x00], [0x24, 0xFE, 0x12],
            [0x00, 0xFE, 0x00], [0x48, 0xFE, 0x90]]

plungerShot = [[0x04, 0xFC, 0x04], [0x10, 0xFC, 0x10],
               [0x20, 0xFC, 0x20], [0x80, 0xFC, 0x80]]


alienExplode = [0x00, 0x08, 0x49, 0x22, 0x14, 0x81, 0x42, 0x00,
                0x42, 0x81, 0x14, 0x22, 0x49, 0x08, 0x00, 0x00]

aShotExplod = [0x4A, 0x15, 0xBE, 0x3F, 0x5E, 0x25]


player = bytearray([0x00, 0x00, 0x0F, 0x1F, 0x1F, 0x1F, 0x1F, 0x7F,
                    0xFF, 0x7F, 0x1F, 0x1F, 0x1F, 0x1F, 0x0F, 0x00])

playerBlow = [[0x00, 0x04, 0x01, 0x13, 0x03, 0x07, 0xB3, 0x0F,
               0x2F, 0x03, 0x2F, 0x49, 0x04, 0x03, 0x00, 0x01],
              [0x40, 0x08, 0x05, 0xA3, 0x0A, 0x03, 0x5B, 0x0F,
               0x27, 0x27, 0x0B, 0x4B, 0x40, 0x84, 0x11, 0x48]]

playerShot = [0x0F]

shotExploding = [0x99, 0x3C, 0x7E, 0x3D, 0xBC, 0x3E, 0x7C, 0x99]

shield = [0xFF, 0x0F, 0xFF, 0x1F, 0xFF, 0x3F, 0xFF, 0x7F, 0xFF, 0xFF, 0xFC,
          0xFF, 0xF8, 0xFF, 0xF0, 0xFF, 0xF0, 0xFF, 0xF0, 0xFF, 0xF0, 0xFF,
          0xF0, 0xFF, 0xF0, 0xFF, 0xF0, 0xFF, 0xF8, 0xFF, 0xFC, 0xFF, 0xFF,
          0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0xFF, 0x3F, 0xFF, 0x1F, 0xFF, 0x0F]

saucer = [0x00, 0x00, 0x00, 0x00, 0x04, 0x0C, 0x1E, 0x37,
          0x3E, 0x7C, 0x74, 0x7E, 0x7E, 0x74, 0x7C, 0x3E,
          0x37, 0x1E, 0x0C, 0x04, 0x00, 0x00, 0x00, 0x00]

char = {'A': [0x00, 0x1F, 0x24, 0x44, 0x24, 0x1F, 0x00, 0x00],
        'B': [0x00, 0x7F, 0x49, 0x49, 0x49, 0x36, 0x00, 0x00],
        'C': [0x00, 0x3E, 0x41, 0x41, 0x41, 0x22, 0x00, 0x00],
        'E': [0x00, 0x7F, 0x49, 0x49, 0x49, 0x41, 0x00, 0x00],
        'D': [0x00, 0x7F, 0x41, 0x41, 0x41, 0x3E, 0x00, 0x00],
        'H': [0x00, 0x7F, 0x08, 0x08, 0x08, 0x7F, 0x00, 0x00],
        'I': [0x00, 0x00, 0x41, 0x7F, 0x41, 0x00, 0x00, 0x00],
        'L': [0x00, 0x7F, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00],
        'M': [0x00, 0x7F, 0x20, 0x18, 0x20, 0x7F, 0x00, 0x00],
        'N': [0x00, 0x7F, 0x10, 0x08, 0x04, 0x7F, 0x00, 0x00],
        'O': [0x00, 0x3E, 0x41, 0x41, 0x41, 0x3E, 0x00, 0x00],
        'P': [0x00, 0x7F, 0x48, 0x48, 0x48, 0x30, 0x00, 0x00],
        'R': [0x00, 0x7F, 0x48, 0x4C, 0x4A, 0x31, 0x00, 0x00],
        'S': [0x00, 0x32, 0x49, 0x49, 0x49, 0x26, 0x00, 0x00],
        'T': [0x00, 0x40, 0x40, 0x7F, 0x40, 0x40, 0x00, 0x00],
        'U': [0x00, 0x7E, 0x01, 0x01, 0x01, 0x7E, 0x00, 0x00],
        'V': [0x00, 0x7C, 0x02, 0x01, 0x02, 0x7C, 0x00, 0x00],
        'Y': [0x00, 0x60, 0x10, 0x0F, 0x10, 0x60, 0x00, 0x00],
        'y': [0x00, 0x03, 0x04, 0x78, 0x04, 0x03, 0x00, 0x00],
        '=': [0x00, 0x14, 0x14, 0x14, 0x14, 0x14, 0x00, 0x00],
        '*': [0x00, 0x22, 0x14, 0x7F, 0x14, 0x22, 0x00, 0x00],
        '-': [0x00, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00],
        '<': [0x00, 0x08, 0x14, 0x22, 0x41, 0x00, 0x00, 0x00],
        '>': [0x00, 0x00, 0x41, 0x22, 0x14, 0x08, 0x00, 0x00],
        '0': [0x00, 0x3E, 0x45, 0x49, 0x51, 0x3E, 0x00, 0x00],
        '1': [0x00, 0x00, 0x21, 0x7F, 0x01, 0x00, 0x00, 0x00],
        '2': [0x00, 0x23, 0x45, 0x49, 0x49, 0x31, 0x00, 0x00],
        '3': [0x00, 0x42, 0x41, 0x49, 0x59, 0x66, 0x00, 0x00],
        ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        '?': [0x00, 0x20, 0x40, 0x4D, 0x50, 0x20, 0x00, 0x00]
        }

AlienSprCYA = [0x00, 0x03, 0x04, 0x78, 0x14, 0x13, 0x08, 0x1A,
               0x3D, 0x68, 0xFC, 0xFC, 0x68, 0x3D, 0x1A, 0x00]
AlienSprCYB = [0x00, 0x00, 0x03, 0x04, 0x78, 0x14, 0x0B, 0x19,
               0x3A, 0x6D, 0xFA, 0xFA, 0x6D, 0x3A, 0x19, 0x00]
AlienSprCA = [0x60, 0x10, 0x0F, 0x10, 0x60, 0x30, 0x18, 0x1A,
              0x3D, 0x68, 0xFC, 0xFC, 0x68, 0x3D, 0x1A, 0x00]
AlienSprCB = [0x00, 0x60, 0x10, 0x0F, 0x10, 0x60, 0x38, 0x19,
              0x3A, 0x6D, 0xFA, 0xFA, 0x6D, 0x3A, 0x19, 0x00]

ColFireTable = [0x01, 0x07, 0x01, 0x01, 0x01, 0x04, 0x0B, 0x01,
                0x06, 0x03, 0x01, 0x01, 0x0B, 0x09, 0x02, 0x08,
                0x02, 0x0B, 0x04, 0x07, 0x0A]

# Game sounds as wav samples

# SHOT_SOUND = pygame.mixer.Sound("sound/shoot.wav")
# HIT_SOUND = pygame.mixer.Sound("sound/invaderkilled.wav")
# EXPLODE_SOUND = pygame.mixer.Sound("sound/explosion.wav")
# ALIEN_SOUND = [pygame.mixer.Sound("sound/fastinvader1.wav"),
#               pygame.mixer.Sound("sound/fastinvader2.wav"),
#               pygame.mixer.Sound("sound/fastinvader3.wav"),
#               pygame.mixer.Sound("sound/fastinvader4.wav")]


class GameInfo():
    def __init__(self):
        self.gameMode = 0
        self.hiscore = 0
        self.score = [0, 0]
        self.coindeposit = 0
        self.credit = 0
        self.splashAnimate = 1
        self.ISRsplashtask = 0
        self.p1ShipsRem = 0
        self.p1startbut = 0
        self.p2ShipsRem = 0
        self.p2startbut = 0


class PlayerInfo():
    def __init__(self):
        self.aliens = [1] * 55
        self.shields = shield*4


class splashanimateRAM():
    def __init__(self, i, dx, dy, x, y, sprite, target, reached):
        self.form = i
        self.dx = dx
        self.dy = dy
        self.x = x
        self.y = y
        self.sprite = sprite
        self.target = target
        self.reached = reached


class alienShotObjects():
    def __init__(self, extra, handler, shottrack, cFir, image):
        self.timer = 0x00
        self.timerExtra = extra
        self.handler = handler
        self.status = 0x00
        self.stepCnt = 0x00
        self.ShotTrack = shottrack
        self.ShotCFir = cFir
        self.ShotBlowCnt = 0x04
        self.ShotImage = image
        self.ShotYr = 0x00
        self.ShotXr = 0x00

    def gameObj2(self):
        self.timerExtra = 0x02  # restore timer
        # I dont get this code
        # if self.ShotCFir > 0:
        #    self.ShotCFir -= 1
        #    return
        ram.otherShot1 = alienshots[1].stepCnt
        ram.otherShot2 = alienshots[2].stepCnt
        self.handleShot()
        if self.ShotBlowCnt == 0:
            self.__init__(*rolling)

    def gameObj3(self):
        if ram.skipPlunger:
            return
        # Shot sync code goes here
        if ram.shotSync - 1 != 0:
            return
        ram.otherShot1 = alienshots[0].stepCnt
        ram.otherShot2 = alienshots[2].stepCnt
        self.handleShot()
        if self.ShotBlowCnt == 0:
            cFir = self.ShotCFir
            self.__init__(*plunger)
            self.ShotCFir = cFir
        if sum(playerinfo[0].aliens) == 1:
            ram.skipPlunger = 1
            self.ShotCFir = 0

    def gameObj4(self):
        ram.otherShot1 = alienshots[0].stepCnt
        ram.otherShot2 = alienshots[1].stepCnt
        self.handleShot()

    def handleShot(self):
        if self.status//0x80 != 1:
            # initiate the shot
            if gameinfo.ISRsplashtask == 4:
                # We are in "Shooting the c"-mode
                self.status = 0x80
                self.stepCnt = 1
                return
            if ram.enableAlienFire:
                self.stepCnt = 0
                if 0 < ram.otherShot1 < gameinfo.aShotReloadRate:
                    return
                if 0 < ram.otherShot2 < gameinfo.aShotReloadRate:
                    return

                if not self.ShotTrack:  # This is reversed (shottrack = 0)
                    # Make tracking shot - this does not work at the moment
                    col = (ram.playerXr+0x08 - ram.refAlienXr) // 16
                    col = np.minimum(np.maximum(0, col), 10)
                else:
                    # Don't track
                    col = ColFireTable[self.ShotCFir] - \
                        1  # -1 to get zero-index column
                    self.ShotCFir = (self.ShotCFir+1) % 21
                # switch player here
                aliens = [playerinfo[0].aliens[col+i*11] for i in range(5)]
                if sum(aliens) == 0:
                    # No aliens in column
                    return
                else:
                    for c in range(5):
                        if aliens[c] > 0:
                            break
                    # use getaliencoords() instead
                    self.ShotXr = (ram.refAlienXr + col * 16) + 7
                    self.ShotYr = (ram.refAlienYr + c * 16) - 10
                    self.status = 0x80
                    self.stepCnt = 1
                    return
        else:
            # move the shot
            if self.status % 2 == 1:
                # Shot is blowing up code here
                self.shotBlowingUp()
                return

            videomem.eraseshifted(
                self.ShotImage[self.stepCnt % 4], self.ShotXr-0x24, self.ShotYr)
            self.stepCnt += 1
            self.ShotYr += ram.alienShotDelta
            ram.collision = videomem.plotshiftedspritecol(
                self.ShotImage[self.stepCnt % 4], self.ShotXr-0x24, self.ShotYr)

            if self.ShotYr <= 21:
                self.status += 0x01
                return

            if ram.collision:
                if 30 < self.ShotYr < 39:
                    # Player has been hit
                    self.status += 0x01
                    ram.playerAlive = 0
                if self.ShotYr > 39:
                    # Shield has been hit
                    self.status += 0x01
            return

    def shotBlowingUp(self):
        # Alien shot blowing up
        self.ShotBlowCnt -= 1
        if self.ShotBlowCnt == 3:
            # Draw the explosion
            videomem.eraseshifted(
                self.ShotImage[self.stepCnt % 4], self.ShotXr-0x24, self.ShotYr)
            videomem.plotshiftedspritecol(
                aShotExplod, self.ShotXr-0x24, self.ShotYr)
        if self.ShotBlowCnt == 0:
            videomem.eraseshifted(aShotExplod, self.ShotXr-0x24, self.ShotYr)


rolling = (0x02, 2, 0x00, 0x00, rollShot)
plunger = (0x00, 3, 0x01, 0x00, plungerShot)
squigly = (0x00, 4, 0x01, 0x06, squiglyShot)

alienshots = [alienShotObjects(*rolling),
              alienShotObjects(*plunger),
              alienShotObjects(*squigly)]


class ROMmirror():
    def __init__(self):
        self.waitOnDraw = 0x01

        self.alienIsExploding = 0x00
        self.expAlienTimer = 0x10
        self.alienRow = 0x00
        self.alienFrame = 0x00
        self.alienCurIndex = 0x00
        self.refAlienDYr = 0x00
        self.refAlienDXr = 0x02
        self.refAlienYr = 0x78
        self.refAlienXr = 0x38
        self.alienPosLSB = 0x78
        self.alienPosMSB = 0x38
        self.rackDirection = 0x00
        self.rackDownDelta = 0xF8

        self.obj0TimerMSB = 0x00
        self.obj0TimerLSB = 0x80
        self.obj0TimerExtra = 0x00
        self.obj0HanlderLSB = 0x8E
        self.oBJ0HanlderMSB = 0x02
        self.playerAlive = 0xFF
        self.expAnimateTimer = 0x05
        self.expAnimateCnt = 0x0C
        self.plyrSprPicL = 0x60
        self.plyrSprPicM = 0x1C
        self.playerYr = 0x20
        self.playerXr = 0x30
        self.plyrSprSiz = 0x10
        self.nextDemoCmd = 0x01
        self.hidMessSeq = 0x00

        self.obj1TimerMSB = 0x00
        self.obj1TimerLSB = 0x00
        self.obj1TimerExtra = 0x00
        self.obj1HandlerLSB = 0xBB
        self.obj1HandlerMSB = 0x03
        self.plyrShotStatus = 0x00
        self.blowUpTimer = 0x10
        self.obj1ImageLSB = 0x90
        self.obj1ImageMSB = 0x1C
        self.obj1CoorYr = 0x28
        self.obj1CoorXr = 0x30
        self.obj1ImageSize = 0x01
        self.shotDeltaX = 0x04
        self.fireBounce = 0x00

        self.endOfTasks = 0xFF
        self.collision = 0x00
        self.expAlienLSB = 0xC0
        self.expAlienMSB = 0x1C
        self.expAlienYr = 0x00
        self.expAlienXr = 0x00
        self.expAlienSize = 0x10
        self.playerDataMSB = 0x21
        self.playerOK = 0x01
        self.enableAlienFire = 0x00
        self.alienFireDelay = 0x30
        self.oneAlien = 0x00
        self.temp206C = 0x12
        self.invaded = 0x00
        self.skipPlunger = 0x00

        self.otherShot1 = 0x00
        self.otherShot2 = 0x00
        self.vblankStatus = 0x00
        self.aShotStatus = 0x00
        self.aShotStepCnt = 0x00
        self.aShotTrack = 0x00
        self.aShotCFirLSB = 0x00
        self.aShotCFirMSB = 0x00
        self.aShotBlowCnt = 0x00
        self.aShotImageLSB = 0x00
        self.aShotImageMSB = 0x00
        self.alienShotYr = 0x00
        self.alienShotXr = 0x00
        self.alienShotSize = 0x00
        self.alienShotDelta = -1  # where is this set in the code?
        self.shotPicEnd = 0x00
        self.shotSync = 0x01
        self.tmp2081 = 0xFF
        self.numAliens = 0xFF
        self.saucerStart = 0x00
        self.saucerActive = 0x00
        self.saucerHit = 0x00
        self.saucerHitTime = 0x20
        self.saucerPriLocLSB = 0x64
        self.saucerPriLocMSB = 0x1D
        self.saucerPriPicLSB = 0xD0
        self.saucerPriPicMSB = 0x29
        self.saucerPriSize = 0x18
        self.saucerDeltaY = 0x02
        self.sauScoreLSB = 0x54
        self.sauScoreMSB = 0x1D
        self.shotCountLSB = 0x00
        self.shotCountMSB = 0x08
        self.tillSaucerLSB = 0x00
        self.tillSaucerMSB = 0x06
        self.waitStartLoop = 0x00
        self.soundPort3 = 0x00
        self.changeFleetSnd = 0x01
        self.fleetSndCnt = 0x40
        self.fleetSndReload = 0x00
        self.soundPort5 = 0x01
        self.extraHold = 0x00
        self.tilt = 0x00
        self.fleetSndHold = 0x10


class VideoMem(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen = pygame.display.set_mode(SIZE)

    def clear(self):
        self = [0x00 for i in range(SIZE[1]//8*SIZE[0])]

    def printmsg(self, mesg, y, x, delay=False):
        sprite = sum([char[c] for c in mesg], [])
        for idx, n in enumerate(sprite):
            if delay and idx % 8 == 0:
                pygame.time.delay(100)
            self[(0x1F - x) + ((y + idx) * 0x20)] = n

    def plotsprite(self, sprite, y, x):
        for idx, n in enumerate(sprite):
            if ((y+idx) <= 223):
                self[(0x1F - x) + ((y + idx) * 0x20)] = n

    def plotshiftedsprite(self, sprite, y, x):
        shift = x % 8
        x = x // 8
        for idx, n in enumerate(sprite):
            n = n << shift
            n1 = n//256
            n2 = n % 256
            if ((y+idx) <= 223):
                self[(0x1F - x) + ((y + idx) * 0x20)
                     ] = self.getmemory(y+idx, x) | n2
                self[(0x1F - x-1) + ((y + idx) * 0x20)
                     ] = self.getmemory(y+idx, x+1) | n1

    def eraseshifted(self, sprite, y, x):
        shift = x % 8
        x = x // 8
        for idx, n in enumerate(sprite):
            n = n << shift
            n1 = n//256
            n2 = n % 256
            if ((y+idx) <= 223):
                self[(0x1F - x) + ((y + idx) * 0x20)] = np.maximum(0,
                                                                   self.getmemory(y+idx, x) - n2)
                self[(0x1F - x-1) + ((y + idx) * 0x20)] = np.maximum(0,
                                                                     self.getmemory(y+idx, x+1) - n1)

    def plotshiftedspritecol(self, sprite, y, x):
        shift = x % 8
        x = x // 8
        collision = 0
        for idx, n in enumerate(sprite):
            n = n << shift
            n1 = n//256
            n2 = n % 256
            field = self.getmemory(y+idx, x)
            collision += int(field & n2)
            field = self.getmemory(y+idx, x+1)
            collision += int(field & n1)
            if ((y+idx) <= 223):
                self[(0x1F - x) + ((y + idx) * 0x20)
                     ] = self.getmemory(y+idx, x) | n2
                self[(0x1F - x-1) + ((y + idx) * 0x20)
                     ] = self.getmemory(y+idx, x+1) | n1
        return collision

    def getmemory(self, y, x):
        return self[(0x1F - x) + y*0x20]

    def clearsprite(self, n_bytes, y, x):
        ''' Clear n bytes at x, y'''
        for idx in range(n_bytes):
            self[(0x1F - x) + ((y + idx) * 0x20)] = 0x00

    def clearplayfield(self):
        for x in range(26):
            for y in range(224):
                self[(0x1F - (x+2)) + (y * 0x20)] = 0x00

    def updatescreen(self):
        vmem = 255*np.array([sum([bitlist(self[a+b*32])
                                  for a in range(32)], []) for b in range(224)])
        surface = pygame.surfarray.make_surface(vmem)
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()


def init():

    videomem.clear()
    videomem.printmsg(" SCORE<1> HI-SCORE SCORE<2>", *xy(0x241E))
    videomem.printmsg(str(gameinfo.score[0]).zfill(4), *xy(0x271C))
    videomem.printmsg(str(gameinfo.score[1]).zfill(4), *xy(0x391C))
    videomem.printmsg(str(gameinfo.hiscore).zfill(4), *xy(0x2F1C))
    videomem.printmsg("CREDIT ", *xy(0x3501))
    videomem.printmsg(str(gameinfo.credit).zfill(2), *xy(0x3C01))
    if interrupt_event.is_set():
        return

    # Why is this initialied here?
    gameinfo.aShotReloadRate = 8

    # Splash screens
    # TODO: turn off sound here
    pygame.time.delay(1000)
    if interrupt_event.is_set():
        return

    if gameinfo.splashAnimate % 2 == 0:
        # Print play with upside down y
        videomem.printmsg("PLAy", *xy(0x3017), delay=True)
    else:
        # Print with normal y
        videomem.printmsg("PLAY", *xy(0x3017), delay=True)

    videomem.printmsg("SPACE INVADERS", *xy(0x2B14), delay=True)
    if interrupt_event.is_set():
        return
    pygame.time.delay(1000)
    videomem.printmsg("*SCORE ADVANCE TABLE*", *xy(0x2810))
    # Saucer is a 24 byte sprite. Don't know why. Should only
    # plot 16 byte sprites here:
    videomem.plotsprite(saucer[4:20], *xy(0x2C0E))
    videomem.plotsprite(alienC0, *xy(0x2C0C))
    videomem.plotsprite(alienB1, *xy(0x2C0A))
    videomem.plotsprite(alienA0, *xy(0x2C08))
    videomem.printmsg("=? MYSTERY", *xy(0x2E0E), delay=True)
    if interrupt_event.is_set():
        return
    videomem.printmsg("=30 POINTS", *xy(0x2E0C), delay=True)
    if interrupt_event.is_set():
        return
    videomem.printmsg("=20 POINTS", *xy(0x2E0A), delay=True)
    if interrupt_event.is_set():
        return
    videomem.printmsg("=10 POINTS", *xy(0x2E08), delay=True)
    if interrupt_event.is_set():
        return
    pygame.time.delay(2000)

    # Alien stealing upside-down y animation
    if gameinfo.splashAnimate % 2 == 0:
        splash.__init__(0, 0, -1, 0xB8//8, 0xD9-0x24,
                        [alienC0, alienC1], 0x9E-0x24, 0)
        gameinfo.ISRsplashtask = 2
        while splash.reached == 0:
            if interrupt_event.is_set():
                return
        splash.__init__(0, 0, 1, 0xB8//8, 0x98-0x24,
                        [AlienSprCYA, AlienSprCYB], 0xFF-0x24, 0)
        while splash.reached == 0:
            if interrupt_event.is_set():
                return
        pygame.time.delay(1000)
        splash.__init__(0, 0, -1, 0xB8//8, 0xFF-0x24,
                        [AlienSprCA, AlienSprCB], 0x97-0x24, 0)
        while splash.reached == 0:
            if interrupt_event.is_set():
                return
        gameinfo.ISRsplashtask = 0
        pygame.time.delay(1000)
        if interrupt_event.is_set():
            return
        videomem.clearsprite(10, *xy(0x33B7))
        pygame.time.delay(2000)
        if interrupt_event.is_set():
            return

    # Play demo
    videomem.clearplayfield()
    # Draw ships remaining
    if gameinfo.p1ShipsRem == 0:
        gameinfo.p1ShipsRem = 3
        videomem.printmsg(str(gameinfo.p1ShipsRem), *xy(0x2501))
        gameinfo.p1ShipsRem -= 1
        for i in range(gameinfo.p1ShipsRem):
            videomem.plotsprite(player, *xy(0x2701+i*0x200))
    # Initialize RAM
    ram.__init__()
    playerinfo[0].__init__()
    # Draw player1 shields
    for i in range(4):
        for idx, n in enumerate(playerinfo[0].shields[0+44*i:44+44*i]):
            videomem[(0x1F - 0x07-(idx % 2)) +
                     (((0x20+i*45) + idx//2) * 0x20)] = n
    gameinfo.ISRsplashtask = 1
    # Draw bottom line
    videomem.plotsprite([0x01]*224, *xy(0x2402))
    # Run demo play
    n = 0
    '''
    while ram.playerAlive == 0xFF:
        plrFireOrDemo(n)
        n += 1
        playerShotHit()
        rackBump()
        if interrupt_event.is_set():
            return
    ram.plyrShotStatus = 0
    while ram.playerAlive != 0xFF:
        # Wait for blow-up to finish
        pass
    # Demo done. Goto next splash
    '''
    gameinfo.ISRsplashtask = 0
    pygame.time.delay(1000)
    videomem.clearplayfield()
    videomem.printmsg("INSERT  COIN", *xy(0x2C11))
    if gameinfo.splashAnimate % 2 == 1:
        videomem.printmsg("C", *xy(0x3311))
    videomem.printmsg("<1 OR 2 PLAYERS>  ", *xy(0x2A0D), delay=True)
    # I don't quite understand the rule for displaying the next line
    videomem.printmsg("*1 PLAYER  1 COIN ", *xy(0x2A0A), delay=True)
    pygame.time.delay(2000)
    if gameinfo.splashAnimate % 2 == 1:
        splash.__init__(0, 0, 1, 0xD0//8, 0x22-0x24,
                        [alienC0, alienC1], 0x94-0x24, 0)
        gameinfo.ISRsplashtask = 2
        while splash.reached == 0:
            if interrupt_event.is_set():
                return
        # What is this data structure?
        de = [0x00, 0x10, 0x00, 0x0E, 0x05, 0x00, 0x00, 0x00,
              0x00, 0x00, 0x07, 0xD0, 0x1C, 0xC8, 0x9B, 0x03]
        alienshots[2] = alienShotObjects(*squigly)
        ram.shotSync = 0x02
        # This value never changes anywhere in the code, so why set it here?
        # ram.alienShotDelta = -1
        gameinfo.ISRsplashtask = 4
        while alienshots[2].status != 1:
            pass
        while alienshots[2].status == 1:
            pass

        gameinfo.ISRsplashtask = 0
        videomem.printmsg(" ", *xy(0x3311))
        pygame.time.delay(2000)

    gameinfo.splashAnimate += 1
    videomem.clearplayfield()
    gameinfo.aShotReloadRate = 0x08
    init()


def waitforstart():
    videomem.clearplayfield()
    videomem.printmsg("PRESS", *xy(0x3013))
    if gameinfo.credit == 1:
        videomem.printmsg("ONLY 1PLAYER BUTTON ", *xy(0x2810))
    else:
        videomem.printmsg("1 OR 2PLAYERS BUTTON", *xy(0x2810))


def drawalien():
    # Choose player 1 or player 2 code goes here
    if ram.alienIsExploding:
        ram.expAlienTimer -= 1
        if ram.expAlienTimer > 0:
            return
        videomem.clearsprite(0x10, ram.expAlienXr, ram.expAlienYr)
        # in the code this is set to 4 here. How does it go back to zero then?
        ram.plyrShotStatus = 0
        ram.blowUpTimer = 10   #
        # The code does not re-initialize the obj1 struct here. But where else?
        ram.obj1CoorYr = 0x28
        ram.obj1CoorXr = 0x30  #
        ram.alienIsExploding = 0
        # TODO: Turn off alien is exploding sound here
    else:
        if playerinfo[0].aliens[ram.alienCurIndex]:
            if ram.alienCurIndex // 11 < 2:
                sprite = [alienA0, alienA1]
            elif 2 <= ram.alienCurIndex // 11 < 4:
                sprite = [alienB0, alienB1]
            else:
                sprite = [alienB0, alienB1]
            videomem.plotsprite(
                sprite[ram.alienFrame], ram.alienPosMSB - 0x24, ram.alienPosLSB // 8)
            videomem.plotsprite([0x00]*16, ram.alienPosMSB -
                                0x24, (ram.alienPosLSB // 8)+1)
    ram.waitOnDraw = 0
    return


def cursorNextAlien():
    if ram.playerOK:
        if ram.waitOnDraw:
            return
        # switch here between player 1 and 2
        ram.alienCurIndex += 1
        if ram.alienCurIndex == 55:
            moveRefAlien()
        if not playerinfo[0].aliens[ram.alienCurIndex]:
            cursorNextAlien()
        getAlienCoords()
        # TODO: Here goes code that handles "Invaded" situation - game over
        ram.waitOnDraw = 1


def getAlienCoords():
    ram.alienPosMSB = ram.refAlienXr + (ram.alienCurIndex % 11) * 16
    ram.alienPosLSB = ram.refAlienYr + (ram.alienCurIndex // 11) * 16


def moveRefAlien():
    # TODO: Here goes code that handles "No aliens left" - next level
    ram.alienCurIndex = 0
    ram.refAlienYr += ram.refAlienDYr
    ram.refAlienXr += ram.refAlienDXr
    ram.alienFrame = (ram.alienFrame + 1) % 2
    ram.refAlienDYr = 0


def plrFireOrDemo(n):
    if ram.playerAlive == 0xFF:
        if ram.obj0TimerLSB > 0:
            # return if timer not zero
            return
        if ram.plyrShotStatus > 0:
            return
        if gameinfo.gameMode:
            pass
        else:
            # Demo mode
            ram.plyrShotStatus = 1
            ram.nextDemoCmd = demoCommands[n % 12]


def playerShotHit():
    if ram.plyrShotStatus == 2:
        if ram.obj1CoorYr > 216:
            ram.plyrShotStatus = 3
            ram.alienIsExploding = 0
            # Turn off exploding sound
            return
        if ram.alienIsExploding > 0:
            if ram.obj1CoorYr > 206:
                ram.saucerHit = 1
                ram.plyrShotStatus = 4
                ram.alienIsExploding = 0
                # turn off exploding sound
                return
            if ram.obj1CoorYr >= ram.refAlienYr:
                # Detect which alien has been hit - or alien shot
                row = (ram.obj1CoorYr - ram.refAlienYr) // 16
                col = (ram.obj1CoorXr - ram.refAlienXr) // 16
                ram.plyrShotStatus = 5
                if not playerinfo[0].aliens[row*11+col]:
                    # Alien shot was hit
                    ram.plyrShotStatus = 3
                    ram.alienIsExploding = 0
                    # turn off exploding sound
                    return
                else:
                    playerinfo[0].aliens[row*11+col] = 0
                    # Adjust score for alien hit
                    ram.expAlienYr = (ram.refAlienYr+(row*16)) // 8
                    ram.expAlienXr = (ram.refAlienXr+(col*16)) - 0x24
                    videomem.plotsprite(
                        alienExplode, ram.expAlienXr, ram.expAlienYr)
                    ram.expAlienTimer = 16
                    return
            else:
                # Shield was hit - special case where aliens are in the shield area
                ram.plyrShotStatus = 3
                ram.alienIsExploding = 0
                # turn off exploding sound


def rackBump():
    if not ram.rackDirection:
        # moving right
        tot = sum([videomem.getmemory(*xy(0x3EA4+n)) for n in range(23)])
        if tot > 0:
            ram.refAlienDXr = -2
            ram.refAlienDYr = -8
            ram.rackDirection = 1
    else:
        # moving left
        tot = sum([videomem.getmemory(*xy(0x2524+n)) for n in range(23)])
        if tot > 0:
            ram.refAlienDXr = 2
            ram.refAlienDYr = -8
            ram.rackDirection = 0


def DrawPlayerDie():
    ram.playerAlive = (ram.playerAlive + 1) % 2
    videomem.plotsprite(playerBlow[ram.playerAlive],
                        ram.playerXr-0x24, ram.playerYr // 8)


def rungameobjs():
    if ram.obj0TimerLSB == 0:
        gameObj0()
    else:
        ram.obj0TimerLSB -= 1
    gameObj1()

    # Alien shot objectives
    if alienshots[0].timer == 0:
        alienshots[0].gameObj2()
    else:
        ram.obj2TimerLSB -= 1
    alienshots[1].gameObj3()
    alienshots[2].gameObj4()


def gameObj0():
    if ram.playerAlive == 0xFF:
        ram.enableAlienFire = 1
        if gameinfo.gameMode:
            # use switch to control player
            pass
        else:
            if ram.nextDemoCmd:
                ram.playerXr = np.minimum(
                    ram.playerXr+1, 242)  # Is this right?
            else:
                ram.playerXr = np.maximum(ram.playerXr-1, 0x24)
            videomem.plotsprite(player, ram.playerXr-0x24, ram.playerYr // 8)
    else:
        # Handle player blowing up
        ram.expAnimateTimer -= 1
        if ram.expAnimateTimer > 0:
            return
        ram.playerOK = 0
        ram.enableAlienFire = 0
        ram.alienFireDelay = 0x30
        ram.expAnimateTimer = 0x05
        ram.expAnimateCnt -= 0x01
        if ram.expAnimateCnt > 0:
            DrawPlayerDie()
            return
        videomem.clearsprite(16, ram.playerXr - 0x24, ram.playerYr // 8)
        # This reinit of the player data should be done better
        ram.obj0TimerMSB = 0x00
        ram.obj0TimerLSB = 0x80
        ram.obj0TimerExtra = 0x00
        ram.obj0HanlderLSB = 0x8E
        ram.oBJ0HanlderMSB = 0x02
        ram.playerAlive = 0xFF
        ram.expAnimateTimer = 0x05
        ram.expAnimateCnt = 0x0C
        ram.plyrSprPicL = 0x60
        ram.plyrSprPicM = 0x1C
        ram.playerYr = 0x20
        ram.playerXr = 0x30
        ram.plyrSprSiz = 0x10
        ram.nextDemoCmd = 0x01
        ram.hidMessSeq = 0x00
        # Turn off sound here
        if ram.invaded:
            return
        if not gameinfo.gameMode:
            return
        # if we are in game mode, here goes code to switch player and remove ship from bottom bar and clear play field


def gameObj1():
    if ram.plyrShotStatus == 0:
        return
    if ram.plyrShotStatus == 1:
        ram.plyrShotStatus = 2
        ram.obj1CoorXr = ram.playerXr+8
        videomem.plotshiftedsprite(
            playerShot, ram.obj1CoorXr - 0x24, ram.obj1CoorYr)
        return
    if ram.plyrShotStatus == 2:
        videomem.eraseshifted(playerShot, ram.obj1CoorXr-0x24, ram.obj1CoorYr)
        ram.obj1CoorYr += ram.shotDeltaX
        ram.alienIsExploding = videomem.plotshiftedspritecol(playerShot, ram.obj1CoorXr -
                                                             0x24, ram.obj1CoorYr)
        return
    if ram.plyrShotStatus == 3:
        ram.blowUpTimer -= 1
        if ram.blowUpTimer == 0:
            videomem.eraseshifted(
                shotExploding, ram.obj1CoorXr-0x24, ram.obj1CoorYr)
            ram.blowUpTimer = 10
            ram.plyrShotStatus = 0
            ram.obj1CoorYr = 0x28
            ram.obj1CoorXr = 0x30
            # update saucer score table
        if ram.blowUpTimer == 9:
            videomem.eraseshifted(
                playerShot, ram.obj1CoorXr-0x24, ram.obj1CoorYr)
            # Adjust explosion position here. Not quite right at the moment
            ram.obj1CoorXr -= 0x02
            ram.obj1CoorYr -= 0x03
            videomem.plotshiftedsprite(
                shotExploding, ram.obj1CoorXr-0x24, ram.obj1CoorYr)


gameinfo = GameInfo()
ram = ROMmirror()
playerinfo = [PlayerInfo(), PlayerInfo()]
splash = splashanimateRAM(0, 0, 0, 0, 0, 0, 0, 0)
videomem = VideoMem([0x00 for _ in range(SIZE[1]//8*SIZE[0])])
interrupt_event = threading.Event()


def main():
    ''' Initialize game '''
    pygame.init()
    clock = pygame.time.Clock()

    parallel_thread = threading.Thread(target=init)
    # Daemonize the thread to automatically exit when the main program exits
    # parallel_thread.daemon = True
    parallel_thread.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    gameinfo.coindeposit = 1
                if event.key == pygame.K_1:
                    gameinfo.p1startbut = 1
                if event.key == pygame.K_2:
                    gameinfo.p2startbut = 1

        # End-of-screen interrupt (scanline 224)
        # TODO: Check and handle tilt goes here. Not really needed.
        # Handle coin deposit
        if gameinfo.coindeposit:
            gameinfo.credit = min(99, gameinfo.credit+1)
            videomem.printmsg(str(gameinfo.credit).zfill(2), *xy(0x3C01))
            gameinfo.coindeposit = 0
        # Are we moving game objects test goes here:
        # if suspendPlay:
        #   break
        if gameinfo.gameMode:
            # process game objects
            pass
        elif gameinfo.credit > 0:
            gameinfo.ISRsplashtask = 0
            interrupt_event.set()
            waitforstart()
        else:
            # process ISR splash tasks
            if gameinfo.ISRsplashtask == 1:
                # Play demo - call main game-play timing loop without sound (0x0072)
                # sync shots here
                ram.shotSync = alienshots[0].timerExtra
                drawalien()
                rungameobjs()
                # timetosaucer()
                # This next function should be handled by mid-screen interrupt.
                cursorNextAlien()
            if gameinfo.ISRsplashtask == 2:
                # Animate alien stealing y
                splash.y += splash.dy
                videomem.plotsprite(
                    splash.sprite[(splash.form//4) % 2], splash.y, splash.x)
                splash.form += 1
                if splash.y == splash.target:
                    splash.reached = 1
            if gameinfo.ISRsplashtask == 4:
                alienshots[2].gameObj4()

        # Update the display
        videomem.updatescreen()

        # Control the frame rate
        clock.tick(60)

    # Quit Pygame and the program
    pygame.quit()


if __name__ == '__main__':
    main()
