import pygame
import numpy as np


def bitlist(x):
    return [int(i) for i in '{:08b}'.format(x)]


pygame.init()

SIZE = height, width = 224, 256
screen = pygame.display.set_mode(SIZE)
pygame.display.update()


player = [0x00, 0x00, 0x0F, 0x1F, 0x1F, 0x1F, 0x1F,
          0x7F, 0xFF, 0x7F, 0x1F, 0x1F, 0x1F, 0x1F, 0x0F, 0x00]

videomem = [0x00]*32*224


game_over = False
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

        # vmem = np.array([[videomem[a + b*224] for a in range(224)]
        #                for b in range(256)])

        vmem = 255*np.array([sum([bitlist(videomem[a+b*32])
                                  for a in range(32)], []) for b in range(224)])

        surface = pygame.surfarray.make_surface(vmem)
        screen.blit(surface, (0, 0))
        pygame.display.update()
        input()
        for idx, n in enumerate(player):
            videomem[2+idx*32] = n

pygame.quit()
quit()
