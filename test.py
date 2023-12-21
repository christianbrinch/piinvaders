import pygame
import numpy as np


def bitlist(x):
    return [int(i) for i in '{:08b}'.format(x)]


pygame.init()
clock = pygame.time.Clock()

SIZE = height, width = 224, 256
screen = pygame.display.set_mode(SIZE)
pygame.display.update()


player = [0x00, 0x00, 0x0F, 0x1F, 0x1F, 0x1F, 0x1F,
          0x7F, 0xFF, 0x7F, 0x1F, 0x1F, 0x1F, 0x1F, 0x0F, 0x00]

char = {'C':[0x00, 0x3E, 0x41, 0x41, 0x41, 0x22, 0x00, 0x00],
        'E':[0x00, 0x7F, 0x49, 0x49, 0x49, 0x41, 0x00, 0x00],
        'D':[0x00, 0x7F, 0x41, 0x41, 0x41, 0x3E, 0x00, 0x00],
        'H':[0x00, 0x7F, 0x08, 0x08, 0x08, 0x7F, 0x00, 0x00],
        'I':[0x00, 0x00, 0x41, 0x7F, 0x41, 0x00, 0x00, 0x00],
        'M':[0x00, 0x7F, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00],
        'O':[0x00, 0x3E, 0x41, 0x41, 0x41, 0x3E, 0x00, 0x00],
        'R':[0x00, 0x7F, 0x48, 0x4C, 0x4A, 0x31, 0x00, 0x00],
        'S':[0x00, 0x32, 0x49, 0x49, 0x49, 0x26, 0x00, 0x00],
        'T':[0x00, 0x40, 0x40, 0x7F, 0x40, 0x40, 0x00, 0x00],
        '-':[0x00, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00],
        '<':[0x00, 0x08, 0x14, 0x22, 0x41, 0x00, 0x00, 0x00],
        '>':[0x00, 0x00, 0x41, 0x22, 0x14, 0x08, 0x00, 0x00],
        '1':[0x00, 0x00, 0x21, 0x7F, 0x01, 0x00, 0x00, 0x00],
        '2':[0x00, 0x23, 0x45, 0x49, 0x49, 0x31, 0x00, 0x00],
        ' ':[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        }

pos = 8

videomem = [0x00]*32*224


game_over = False
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
    key = pygame.key.get_pressed()
    if key[pygame.K_LEFT]:
        pos = np.maximum(2,pos-1)
    elif key[pygame.K_RIGHT]:
        pos = np.minimum(202-16, pos+1)
        
    for idx, n in enumerate(player):
            videomem[(0x1F - 0x08) + ((pos + idx) * 0x20)] = n

    for idx, n in enumerate(player):
            videomem[(0x1F - 0x01) + ((0x18 + idx) * 0x20)] = n

    message = "CREDIT "
    sprite = sum([char[c] for c in message], [])
    for idx, n in enumerate(sprite):
            videomem[(0x1F - 0x01) + ((0x88 + idx) * 0x20)] = n

    message = " SCORE<1> HI-SCORE SCORE<2>"
    sprite = sum([char[c] for c in message], [])
    for idx, n in enumerate(sprite):
            videomem[(0x1F - 0x1E) + ((0x00 + idx) * 0x20)] = n


    vmem = 255*np.array([sum([bitlist(videomem[a+b*32])
                                  for a in range(32)], []) for b in range(224)])


    surface = pygame.surfarray.make_surface(vmem)
    screen.blit(surface, (0, 0))
    clock.tick(60)
    pygame.display.update()
    

pygame.quit()
quit()
