import pygame
import copy
from laser import Laser
from scipy.spatial.distance import euclidean
from algorithms import minimax


MOVE_LEFT_ACTION = 0
MOVE_RIGHT_ACTION = 1
SHOOT_ACTION = 2
PLAYER_SPEED = 2
PLAYER_LASER_SPEED = -8


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, constraint):
        super().__init__()
        self.image = pygame.image.load(
            '../graphics/player.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = PLAYER_SPEED
        self.max_x_constraint = constraint
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600

        self.lasers = pygame.sprite.Group()

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.ready:
            self.fire()

    def fire(self):
        if self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()

    def recharge(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    def constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.max_x_constraint:
            self.rect.right = self.max_x_constraint

    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center, PLAYER_LASER_SPEED, self.rect.bottom))

    def update(self):
        self.get_input()
        self.constraint()
        self.recharge()
        self.lasers.update()

    def get_available_actions(self):
        act_lst = []
        if self.rect.left - self.speed > 0:
            act_lst.append(MOVE_LEFT_ACTION)

        if self.rect.right + self.speed < self.max_x_constraint:
            act_lst.append(MOVE_RIGHT_ACTION)

        if self.ready:
            act_lst.append(SHOOT_ACTION)

        return act_lst

    def perform_action(self, action):
        if action == MOVE_LEFT_ACTION:
            self.rect.x -= self.speed
        elif action == MOVE_RIGHT_ACTION:
            self.rect.x += self.speed
        elif action == SHOOT_ACTION:
            self.fire()

    def dist_to_closest_laser(self, lasers):
        if not lasers:
            return float('inf')
        return min(euclidean(self.rect.center, laser.rect.center)
                   for laser in lasers)

    def dists_to_lasers(self, lasers):
        return [euclidean(self.rect.center, laser.rect.center)
                   for laser in lasers]

    def dist_to_closest_alien(self, aliens):
        if not aliens:
            return 100
        return euclidean(self.rect.center, aliens[0].rect.center)

    def copy(self):
        new = Player(self.rect.midbottom, self.max_x_constraint)
        for sprite in self.lasers.sprites():
            new.lasers.add(sprite.copy())
        return new


