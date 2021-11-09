import pygame


ASTEROID_COLOR = (241, 79, 80)
ASTEROID_SIZE = 6


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ASTEROID_SIZE, ASTEROID_SIZE))
        self.image.fill(ASTEROID_COLOR)

        self.rect = self.image.get_rect(topleft=(x, y))

    def copy(self):
        return Block(*self.rect.topleft)


shape = [
    '  xxxxxxx',
    ' xxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxx     xxx',
    'xx       xx'
]
