import pygame


ASTEROID_COLOR = (241, 79, 80)
OBS_BLOCK_SIZE = 2


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((OBS_BLOCK_SIZE, OBS_BLOCK_SIZE))
        self.image.fill(ASTEROID_COLOR)

        self.rect = self.image.get_rect(topleft=(x, y))

    def copy(self):
        return Block(*self.rect.topleft)


OBSTACLE_SHAPE = [
    '  xxxxxxx',
    ' xxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxx     xxx',
    'xx       xx'
]
