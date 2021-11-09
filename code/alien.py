import copy
import random

import pygame
from scipy.spatial.distance import euclidean



WALK_ACTION = 'sm'
JUMP_LEFT_ACTION = 'jl'
JUMP_RIGHT_ACTION = 'jr'


def point_in_rect(point, rect):
    x1, y1 = rect.topleft
    x2, y2 = rect.bottomright
    x, y = point
    return x1 < x < x2 and y1 < y < y2


class Alien(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        file_path = '../graphics/' + color + '.png'
        self.image = pygame.image.load(file_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.jump_x_delta = 30
        self.color = color
        if color == 'red':
            self.value = 100
        elif color == 'green':
            self.value = 200
        else:
            self.value = 300

    def update(self, player_lasers, all_aliens, max_x, direction=None):
        acts = self.get_available_actions(player_lasers, all_aliens, max_x)

        if len(acts) == 1 and acts[0] == WALK_ACTION and direction is not None:
            self.perform_action(acts[0], direction)
        elif len(acts) == 2:
            acts.remove(WALK_ACTION)
            self.perform_action(acts[0])
        elif len(acts) == 3:
            orig_center_x = self.rect.centerx
            results = []
            for sign, action in \
                    [(-1, JUMP_LEFT_ACTION), (1, JUMP_RIGHT_ACTION)]:
                new_center = \
                    orig_center_x + sign * self.jump_x_delta, self.rect.centery
                dst = min(euclidean(new_center, laser.rect.center)
                          for laser in player_lasers)
                results.append((action, dst))

            best_move, dst = max(results, key=lambda x: x[1])
            self.perform_action(best_move)

    def get_available_actions(self, player_lasers, all_aliens, max_x):
        actions = [WALK_ACTION]
        danger_dist = 35
        orig_centerx = self.rect.centerx

        if player_lasers:
            for laser in player_lasers:
                if euclidean(self.rect.center, laser.rect.center) < danger_dist:
                    for sign, move in [(-1, JUMP_LEFT_ACTION),
                                       (1, JUMP_RIGHT_ACTION)]:
                        if random.random() > .7:
                            continue
                        if (sign == -1 and
                            self.rect.left + sign * self.jump_x_delta <= 0) or \
                           (sign == 1 and
                            self.rect.right + sign * self.jump_x_delta >= max_x):
                            continue

                        shifted_center_coords = \
                            (orig_centerx + sign * self.jump_x_delta,
                             self.rect.centery)

                        if not any(
                                point_in_rect(shifted_center_coords, alien.rect)
                                for alien in all_aliens if self is not alien):
                            actions.append(move)
        return actions

    def perform_action(self, action, direction=None):
        if action == WALK_ACTION:
            self.rect.x += direction
        elif action == JUMP_LEFT_ACTION:
            self.rect.centerx -= self.jump_x_delta
        elif action == JUMP_RIGHT_ACTION:
            self.rect.centerx += self.jump_x_delta

    def copy(self):
        return Alien(self.color, *self.rect.topleft)


