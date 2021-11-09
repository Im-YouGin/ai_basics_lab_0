import pygame
import sys
import copy
import csv
import time
from scipy.spatial.distance import euclidean
import random
from player import Player
import obstacle
from alien import Alien
from random import choice, randint
from laser import Laser
from algorithms import best_move


pg_timer = pygame.time.get_ticks

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# ALIENLASER = pygame.USEREVENT + 1
# pygame.time.set_timer(ALIENLASER, 800)


class Game:
    def __init__(self):
        # Player setup
        self.alien_shoot_cooldown = 2000
        self.last_shoot_time = 0
        self.max_x_constraint = SCREEN_WIDTH
        player_sprite = Player((SCREEN_WIDTH / 2, SCREEN_HEIGHT), SCREEN_WIDTH)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # health and score setup
        self.lives = 3
        self.live_surf = pygame.image.load(
            '../graphics/player.png').convert_alpha()
        self.live_x_start_pos = SCREEN_WIDTH - (
                    self.live_surf.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font('../font/Pixeled.ttf', 20)
        self.running = True
        # Obstacle setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (SCREEN_WIDTH / self.obstacle_amount)
                                     for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions,
                                       x_start=SCREEN_WIDTH / 15, y_start=480)

        # Alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows=2, cols=4)
        self.alien_direction = 1
        self.game_result = None
        self.ai_algo = random.choice(['minimax', 'expectimax'])

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance=90,
                    y_distance=48, x_offset=70, y_offset=100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0:
                    alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien('green', x, y)
                else:
                    alien_sprite = Alien('red', x, y)
                self.aliens.add(alien_sprite)

    def min_dist_to_player_laser(self):
        player_lasers = self.player.sprite.lasers.sprites()

        if not player_lasers:
            return 0
        return min(euclidean(alien.rect.center, enemy_laser.rect.center)
                   for alien in self.aliens.sprites()
                   for enemy_laser in player_lasers)

    def dist_from_ship_to_alien(self):
        if not self.aliens:
            return -float('inf')

        return euclidean(self.player.sprite.rect.center,
                         self.aliens.sprites()[len(self.aliens) // 2].rect.center)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= SCREEN_WIDTH:
                self.alien_direction = -1
                self.alien_move_down(20)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(20)

    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if pg_timer() - self.last_shoot_time > \
                self.alien_shoot_cooldown and self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 10, SCREEN_HEIGHT)
            self.alien_lasers.add(laser_sprite)
            self.last_shoot_time = pg_timer()

    def update_alien_shoot_cd(self):
        self.alien_shoot_cooldown = max(len(self.aliens) * 250, 1000)
        # print(self.alien_shoot_cooldown)

    def collision_checks(self):

        # player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                if pygame.sprite.spritecollide(laser, self.alien_lasers, True):
                    laser.kill()

                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens,
                                                         True)

                if aliens_hit:
                    self.update_alien_shoot_cd()
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()

        # alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collisions
                # print(laser, self.blocks)
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    # print('hit1')
                    laser.kill()

                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        self.running = False
                        self.game_result = 'l'

        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)

                if pygame.sprite.spritecollide(alien, self.player, False):
                    self.running = False
                    self.game_result = 'l'

    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (
                        live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf, (x, 8))

    def display_score(self):
        score_surf = self.font.render(f'score: {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft=(10, -10))
        screen.blit(score_surf, score_rect)

    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('You won', False, 'white')
            victory_rect = victory_surf.get_rect(center=(SCREEN_WIDTH / 2,
                                                         SCREEN_HEIGHT / 2))
            screen.blit(victory_surf, victory_rect)
            self.running = False
            self.game_result = 'w'

    def run(self):
        mv = best_move(self, algo=self.ai_algo)
        self.player.sprite.perform_action(mv)
        self.player.update()

        self.alien_shoot()
        self.alien_lasers.update()
        self.aliens.update(self.player.sprite.lasers.sprites(),
                           self.aliens.sprites(), self.max_x_constraint,
                           direction=self.alien_direction)
        self.alien_position_checker()

        self.collision_checks()

        # if self.game_over():
        #     return
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)

        self.display_lives()
        self.display_score()
        self.victory_message()

    def copy_player(self):
        return pygame.sprite.GroupSingle(self.player.sprite.copy())

    def copy_blocks(self):
        cp = pygame.sprite.Group()
        for sprite in self.blocks.sprites():
            cp.add(sprite.copy())
        return cp

    def copy_aliens(self):
        cp = pygame.sprite.Group()
        for sprite in self.aliens.sprites():
            cp.add(sprite.copy())
        return cp

    def copy_alien_lasers(self):
        cp = pygame.sprite.Group()
        for sprite in self.alien_lasers.sprites():
            cp.add(sprite.copy())
        return cp

    def copy(self):
        copy_obj = Game()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                # print('copy #', name, attr)
                cp = None
                if name == 'player':
                    cp = self.copy_player()
                elif name == 'blocks':
                    cp = self.copy_blocks()
                elif name == 'aliens':
                    cp = self.copy_aliens()
                elif name == 'alien_lasers':
                    cp = self.copy_alien_lasers()
                else:
                    cp = attr.copy()
                copy_obj.__dict__[name] = cp
            else:
                try:
                    copy_obj.__dict__[name] = copy.deepcopy(attr)
                except TypeError:
                    # print('except #', name, attr)
                    copy_obj.__dict__[name] = attr
                else:
                    # print('deepcopy #', name, attr)
                    pass
        return copy_obj


if __name__ == '__main__':
    pygame.init()

    for i in range(50):
        st = time.time()
        ###########################################
        game = Game()
        while game.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((30, 30, 30))
            game.run()

            pygame.display.flip()
            clock.tick(60)
        ###########################################
        end = time.time()

        with open('results.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(
                [game.game_result, end - st, game.score, game.ai_algo])

    pygame.quit()


