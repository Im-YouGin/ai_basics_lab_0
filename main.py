import random
import numpy as np

import pygame
import os
import sys
from math import floor
from algorithms import *
from itertools import cycle
from config import *
from game_objets import *


pygame.display.set_caption("Space Invaders")

        
class SpaceInvaders:
    def __init__(self):
        self.window_surface = pygame.display.set_mode(Config.WINDOW_SIZE)

        self.game_over = False
        self.is_playing = True

        self.spaceship = Spaceship()
        self.aliens = Aliens()
        self.score = Score()
        self.lives = Lives()
        self.game_over_screen = GameOver()
        self.best_score = BestScore()
        self.asteroids = Asteroids()

        self.bg_image = pygame.transform.scale(pygame.image.load(
            os.path.join(Config.SPRITES_DIR, 'background.jpg')),
            Config.WINDOW_SIZE
        )
        self.curr_algo = None
        self.algo_list = cycle(['bfs', 'dfs', 'ucs', None])

    def start(self):
        clock = pygame.time.Clock()

        while True:
            dt = clock.tick(45)
            # --- Main event loop


            # --- Game logic should go here
            if self.lives.value < 0:
                self._game_over()

            # --- Screen-clearing code goes here

            # Here, we clear the screen to white. Don't put other drawing commands
            # above this, or they will be erased with this command.

            # If you want a background image, replace this clear with blit'ing the
            # background image.

            self.window_surface.blit(self.bg_image, (0, 0))
            # --- Drawing code should go here
            if self.is_playing:
                self._update(dt)
                self._collide()

            self.score.draw(self.window_surface)
            self.spaceship.draw(self.window_surface)
            self.aliens.draw(self.window_surface)
            self.score.draw(self.window_surface)
            self.lives.draw(self.window_surface)
            self.best_score.draw(self.window_surface)
            self.asteroids.draw(self.window_surface)

            pygame.draw.line(self.window_surface, (255, 255, 255), (0, Config.WINDOW_SIZE[1] * 0.9),
                             (Config.WINDOW_SIZE[0], Config.WINDOW_SIZE[1] * 0.9))

            if self.curr_algo is not None:
                func = {
                    'bfs': bfs,
                    'dfs': dfs,
                    'ucs': ucs
                }.get(self.curr_algo)
                matrix = np.ones(shape=(int(Config.SPACESHIP_STARTING_POSITION[1] / zoom) + 1,
                                        int(Config.WORLD_DIM[0] / zoom) + 1))

                ship_x, ship_y = self.spaceship.rect.center
                matrix[int(ship_y / zoom) - 1][int(ship_x / zoom) - 1] = -1

                for alien in self.aliens.alien_list:
                    tl, tr, bl, br = alien.rect.topleft, alien.rect.topright, \
                                     alien.rect.bottomleft, alien.rect.bottomright
                    for rx in range(tl[0], tr[0]):
                        for ry in range(tl[1], bl[1]):
                            matrix[int(ry / zoom)][int(rx / zoom)] = 2

                for ast, rect in self.asteroids.asteroids:
                    if ast is None:
                        continue

                    tl, tr, bl, br = rect.topleft, rect.topright, \
                                     rect.bottomleft, rect.bottomright

                    for rx in range(tl[0], tr[0]):
                        for ry in range(tl[1], bl[1]):

                            matrix[int(ry / zoom)][int(rx / zoom)] = 3

                for alien in self.aliens.alien_list[:]:
                    test_x, test_y = alien.rect.center
                    points = func(matrix, (int(test_x / zoom) - 1,
                                          int(test_y / zoom) - 1))
                    points = [(x * zoom, y * zoom) for x, y in points]
                    # color =
                    pygame.draw.lines(
                        self.window_surface, (random.choice(range(256)), random.choice(range(256)), random.choice(range(256))), False, points)

            if self.game_over:
                self.best_score.value = \
                    max(self.best_score.value, self.score.value)
                self.game_over_screen.draw(self.window_surface)
                if self._ask_restart():
                    self.restart_game()
            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second


    def _update(self, dt):
        events = self._get_events()
        self.spaceship.update(dt, events)
        self.aliens.update(dt)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.curr_algo = next(self.algo_list)

    def _get_events(self):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            events.append(event)

        return events
    
    def _collide(self):
        self._collide_rocket_and_aliens()
        self._collide_laser_and_spaceship()
        self._collide_laser_and_rocket()
        self._collide_ufo_and_rocket()
        self._collide_aliens_and_spaceship()
        self._collide_rocket_and_asteroid()
        self._collide_laser_and_asteroid()

    def _collide_rocket_and_aliens(self):
        if not self.spaceship.rocket.is_active:
            return

        # Get rectangle from missile
        missile_rect = self.spaceship.rocket.rect

        # Get each alien rectangle and check collision
        for alien in self.aliens.alien_list:
            if missile_rect.colliderect(alien.rect):
                # if collision, make the alien explode and remove missile
                alien.explode()
                if len(self.aliens.alien_list) < 54 and \
                        not self.aliens.ufo.is_active:
                    self.aliens.ufo.launch()

                self.spaceship.rocket.is_active = False

                # increase score
                self.score.value += alien.type * 10

    def _collide_laser_and_spaceship(self):
        for alien in self.aliens.alien_list:
            if not alien.laser.is_active:
                continue

            if alien.laser.rect.colliderect(self.spaceship.rect):
                # alien.laser.explode()
                alien.laser.set_inactive()

                self.lives.die()
                self.spaceship.destroy()

    def _game_over(self):
        self.game_over = True
        self.is_playing = False

    def restart_game(self):

        self.game_over = False
        self.is_playing = True

        self.spaceship = Spaceship()
        self.aliens = Aliens()
        self.score = Score()
        self.lives = Lives()
        self.game_over_screen = GameOver()

    def _ask_restart(self):
        events = self._get_events()

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                return True
        return False

    def _collide_laser_and_rocket(self):
        for alien in self.aliens.alien_list:
            if not alien.laser.is_active or self.spaceship.rocket.rect is None:
                continue

            if alien.laser.rect.colliderect(self.spaceship.rocket.rect):
                alien.laser.explode()
                self.spaceship.rocket.explode()

    def _collide_ufo_and_rocket(self):
        if not (self.spaceship.rocket.is_active and
                self.aliens.ufo.is_active and
                not self.aliens.ufo.is_destroyed):
            return

        if self.spaceship.rocket.rect.colliderect(self.aliens.ufo.rect):
            self.aliens.ufo.destroy()

    def _collide_aliens_and_spaceship(self):
        for alien in self.aliens.alien_list:
            if alien.is_exploded:
                continue

            if alien.rect.colliderect(self.spaceship.rect):
                self._game_over()

    def _collide_rocket_and_asteroid(self):
        if not self.spaceship.rocket.is_active:
            return

        for ix, (ast, rect) in enumerate(self.asteroids.asteroids):
            if ast is None:
                continue

            if rect.colliderect(self.spaceship.rocket.rect):
                self.asteroids.asteroids[ix] = (None, None)
                self.spaceship.rocket.explode()


    def _collide_laser_and_asteroid(self):
        for alien in self.aliens.alien_list:
            if not alien.laser.is_active:
                continue

            for ix, (ast, rect) in enumerate(self.asteroids.asteroids):
                if ast is None:
                    continue

                if rect.colliderect(alien.laser.rect):
                    alien.laser.explode()
                    self.asteroids.asteroids[ix] = (None, None)


if __name__ == '__main__':
    pygame.init()
    SpaceInvaders().start()
