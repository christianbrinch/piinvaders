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

demoCommands = [0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 
               0x02, 0x01, 0x00, 0x02, 0x01, 0x00]

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

alienExplode = [0x00, 0x08, 0x49, 0x22, 0x14, 0x81, 0x42, 0x00, 
                0x42, 0x81, 0x14, 0x22, 0x49, 0x08, 0x00, 0x00]

aShotExplod = [0x4A, 0x15, 0xBE, 0x3F, 0x5E, 0x25]


player = [0x00, 0x00, 0x0F, 0x1F, 0x1F, 0x1F, 0x1F, 0x7F,
          0xFF, 0x7F, 0x1F, 0x1F, 0x1F, 0x1F, 0x0F, 0x00]

playerBlow0 = [0x00, 0x04, 0x01, 0x13, 0x03, 0x07, 0xB3, 0x0F, 
               0x2F, 0x03, 0x2F, 0x49, 0x04, 0x03, 0x00, 0x01]
playerBlow1 = [0x40, 0x08, 0x05, 0xA3, 0x0A, 0x03, 0x5B, 0x0F,
               0x27, 0x27, 0x0B, 0x4B, 0x40, 0x84, 0x11, 0x48]

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
    def __init__(self,i,dx,dy,x,y,sprite,target,reached):
        self.form=i
        self.dx=dx
        self.dy=dy
        self.x=x
        self.y=y
        self.sprite=sprite
        self.target=target
        self.reached=reached


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

        self.obj2TimerMSB = 0x00
        self.obj2TimerLSB = 0x00
        self.obj2TimerExtra = 0x02
        self.obj2HandlerLSB = 0x76
        self.obj2HandlerMSB = 0x04
        self.rolShotStatus = 0x00
        self.rolShotStepCnt = 0x00
        self.rolShotTrack = 0x00
        self.rolShotCFirLSB = 0x00
        self.rolShotCFirMSB = 0x00
        self.rolShotBlowCnt = 0x04
        self.rolShotImageLSB = 0xEE
        self.rolShotImageMSB = 0x1C
        self.rolShotYr = 0x00
        self.rolShotXr = 0x00
        self.rolShotSize = 0x03

        self.obj3TimerMSB = 0x00
        self.obj3TimerLSB = 0x00
        self.obj3TimerExtra = 0x00
        self.obj3HandlerLSB = 0xB6
        self.obj3HandlerMSB = 0x04
        self.pluShotStatus = 0x00
        self.pluShotStepCnt = 0x00
        self.pluShotTrack = 0x01
        self.pluShotCFirLSB = 0x00
        self.pluShotCFirMSB = 0x1D
        self.pluShotBlowCnt = 0x04
        self.pluShotImageLSB = 0xE2
        self.pluShotImageMSB = 0x1C
        self.pluShotYr = 0x00
        self.pluSHotXr = 0x00
        self.pluShotSize = 0x03

        self.obj4TimerMSB = 0x00
        self.obj4TimerLSB = 0x00
        self.obj4TimerExtra = 0x00
        self.obj4HandlerLSB = 0x82
        self.obj4HandlerMSB = 0x06
        self.squShotStatus = 0x00
        self.squShotStepCnt = 0x00
        self.squShotTrack = 0x01
        self.squShotCFirLSB = 0x06
        self.squShotCFirMSB = 0x1D
        self.squSHotBlowCnt = 0x04
        self.squShotImageLSB = 0xD0
        self.squShotImageMSB = 0x1C
        self.squShotYr = 0x00
        self.squShotXr = 0x00
        self.squShotSize = 0x03
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
        self.alienShotDelta = 0x00
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

    def getmemory(self, y, x):
        return self[(0x1F - x)+ y*0x20]

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
    aShotReloadRate = 8

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
        splash.__init__(0,0,-1,0xB8//8,0xD9-0x24,[alienC0, alienC1],0x9E-0x24,0)
        gameinfo.ISRsplashtask = 2
        while splash.reached == 0:
            if interrupt_event.is_set():
                return
        splash.__init__(0,0,1,0xB8//8,0x98-0x24,[AlienSprCYA, AlienSprCYB],0xFF-0x24,0)
        while splash.reached == 0:
            if interrupt_event.is_set():
                return
        pygame.time.delay(1000)
        splash.__init__(0,0,-1,0xB8//8,0xFF-0x24,[AlienSprCA, AlienSprCB],0x97-0x24,0)
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
    gameinfo.ISRsplashtask=1
    # Draw bottom line
    videomem.plotsprite([0x01]*224, *xy(0x2402))
    n=0
    while ram.playerAlive:
        plrFireOrDemo(n)
        n += 1
        # playerShotHit() detection
        rackBump()
        if interrupt_event.is_set():
            return
        # Check for players been hit
        # If no - continue, if yes - wait for demo player to stop exploding
        # and return to splash
    # init()

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
        videomem.clearsprite(10, ram.expAlienYr)
        ram.plyrShotStatus = 4
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
            videomem.plotsprite(sprite[ram.alienFrame], ram.alienPosMSB - 0x24, ram.alienPosLSB // 8)
            videomem.plotsprite([0x00]*16, ram.alienPosMSB - 0x24, (ram.alienPosLSB // 8)+1)
    return

def cursorNextAlien():
    if ram.playerOK:
        # switch here between player 1 and 2
        ram.alienCurIndex += 1
        if ram.alienCurIndex == 55:
            moveRefAlien()
        if not playerinfo[0].aliens[ram.alienCurIndex]:
            cursorNextAlien()
        getAlienCoords()
        # Here goes code that handles "Invaded" situation

def getAlienCoords():
    ram.alienPosMSB = ram.refAlienXr + (ram.alienCurIndex % 11) * 16 
    ram.alienPosLSB = ram.refAlienYr + (ram.alienCurIndex // 11) * 16


def moveRefAlien():
    # TODO: Here goes code that handles "No aliens left"
    ram.alienCurIndex = 0
    ram.refAlienYr += ram.refAlienDYr
    ram.refAlienXr += ram.refAlienDXr
    ram.alienFrame = (ram.alienFrame + 1) % 2
    ram.refAlienDYr = 0

def plrFireOrDemo(n):
    if ram.playerAlive:
        # get player task timer here
        # return if timer not zero
        if ram.plyrShotStatus > 0:
            return
        if gameinfo.gameMode:
            pass
        else:
            # Demo mode
            ram.plyrShotStatus = 1
            ram.nextDemoCmd = demoCommands[n % 12]
            #print(ram.nextDemoCmd)
            #time.sleep(1)

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
 

def rungameobjs(): 
    gameObj0()
    gameObj1()

def gameObj0():
    if ram.playerOK:
        ram.enableAlienFire = 1
        if gameinfo.gameMode:
            # use switch to control player
            pass
        else:
            if ram.nextDemoCmd:
                ram.playerXr += 1
            else:
                ram.playerXr -= 1
            videomem.plotsprite(player, ram.playerXr-0x24, ram.playerYr // 8 )
    else:
        # Handle player blowing up
        pass

def gameObj1():
    if ram.plyrShotStatus == 0:
        return
    if ram.plyrShotStatus == 1:
        ram.plyrShotStatus = 2
        ram.obj1CoorYr = ram.playerXr+8
        videomem.plotsprite(playerShot, ram.obj1CoorXr-0x24, ram.obj1CoorYr // 8)
        return
    if ram.plyrShotStatus == 2:
        videomem.clearsprite(1, ram.obj1CoorXr-0x24, ram.obj1CoorYr // 8)
        ram.obj1CoorYr += ram.shotDeltaX
        # Modify method to test for collision
        videomem.plotsprite(playerShot, ram.obj1CoorXr-0x24, ram.obj1CoorYr // 8)
        # if collision, set ram.alienIsExploding
        return
    if ram.plyrShotStatus == 3:
        pass

gameinfo = GameInfo()
ram = ROMmirror()
playerinfo = [PlayerInfo(), PlayerInfo()]
splash = splashanimateRAM(0,0,0,0,0,0,0,0)
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
                #syncrollingshot()
                drawalien()
                rungameobjs()
                #timetosaucer()
                # This next function should be handled by mid-screen interrupt.
                cursorNextAlien()
            if gameinfo.ISRsplashtask == 2:
                # Animate alien stealing y
                splash.y += splash.dy
                videomem.plotsprite(splash.sprite[(splash.form//4) % 2], splash.y, splash.x)
                splash.form += 1
                if splash.y == splash.target:
                    splash.reached = 1
            if gameinfo.ISRsplashtask == 3:
                # alien shooting c code should go here
                pass

        # Update the display
        videomem.updatescreen()

        # Control the frame rate
        clock.tick(60)

    # Quit Pygame and the program
    pygame.quit()

if __name__ == '__main__':
    main()
