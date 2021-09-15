import pygame
import os
import random
from config import *


class Rocket:

    def __init__(self):
        self.movement_speed = Config.ROCKET_MOVESPEED
        self.rocket_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(Config.SPRITES_DIR,
                                           Config.ROCKET_SPRITE)),
            (27, 27)
        )
        self.time_since_explosion = 0
        self.explosion_sprite = pygame.transform.scale(
            pygame.image.load(
                os.path.join(Config.SPRITES_DIR,
                             Config.ROCKET_EXPLOSION_SPRITE_FNAME)),
            Config.MISSILE_EXPLOSION_SIZE
        )
        self.is_active = False
        self.sound = pygame.mixer.Sound(os.path.join(
            Config.SOUNDS_DIR, Config.ROCKET_SHOOT_SOUND))
        self.rect = None

    def shoot(self, rect):
        self.rect = rect
        self.is_exploded = False
        self.is_active = True
        self.time_since_explosion = 0
        self.sound.play()

    def _move(self):
        self.rect.y -= self.movement_speed

    def update(self, dt):
        if not self.is_active:
            return

        if self.is_exploded:
            self.time_since_explosion += dt
        else:
            self._move()

    def draw(self, surface):
        if not self.is_active:
            return

        if self.is_exploded:
            surface.blit(
                self.explosion_sprite,
                self.explosion_sprite.get_rect(center=self.rect.center))

        else:
            # pygame.draw.rect(surface, (0, 255, 0), self.rect)
            surface.blit(
                self.rocket_sprite,
                self.rocket_sprite.get_rect(center=self.rect.center)
            )

    def explode(self):
        self.is_exploded = True

    def set_inactive(self):
        self.is_active = False


class Spaceship:

    def __init__(self):
        self.sprite = pygame.image.load(
            os.path.join(Config.SPRITES_DIR, Config.SPACESHIP_SPRITE_FNAME))
        self.sprite.convert_alpha()
        self.sprite = pygame.transform.scale(
            self.sprite,
            (35, 35)
        )

        self.rect = self.sprite.get_rect(
            center=Config.SPACESHIP_STARTING_POSITION)
        self.destruction_sprite = pygame.transform.scale(
            pygame.image.load(
                os.path.join(Config.SPRITES_DIR,
                             Config.UFO_EXPLOSION_SPRITE_NAME)
            ), (50, 50)
        )
        self.moving_direction = Directions.IDLE
        self.is_firing = False

        self.rocket = Rocket()

        self.is_destroyed = False
        self.delay_since_explosion = 0
        self.is_active = True

    def draw(self, surface):
        if self.is_active:
            if self.is_destroyed:
                surface.blit(self.destruction_sprite, self.rect)

            else:
                surface.blit(self.sprite, self.rect)

        if self.rocket.is_active:
            self.rocket.draw(surface)

    def update(self, dt, events):
        self._perform_user_input(events)

        if not self.is_destroyed:
            self._update_rocket(dt)
            self._fire()

        else:
            self.delay_since_explosion += dt
            if self.is_destroyed and self.delay_since_explosion > \
                    Config.SPACESHIP_EXPLOSION_DURATION_MS:
                self._reset()

    def _perform_user_input(self, events):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if self.rect.left < 0:
                self.rect.x = 0
            else:
                self.rect.x -= 4

        if keys[pygame.K_RIGHT]:
            if self.rect.right > Config.WORLD_DIM[0]:
                self.rect.x = Config.WORLD_DIM[0] - 1
            else:
                self.rect.x += 4

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.is_firing = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.is_firing = False

    def _fire(self):
        if not self.is_firing:
            return

        if self.rocket.is_active:
            return

        self._shoot_rocket()

    def _shoot_rocket(self):
        rect = pygame.Rect(
            self.rect.centerx - (Config.MISSILE_RECT_DIM[0] // 2),
            self.rect.top - Config.MISSILE_RECT_DIM[1],
            Config.MISSILE_RECT_DIM[0],
            Config.MISSILE_RECT_DIM[1]
        )
        self.rocket.shoot(rect)

    def _update_rocket(self, dt):
        if not self.rocket.is_active:
            return

        self.rocket.update(dt)

        if self.rocket.rect.top < 0:
            self.rocket.rect.top = 0
            self.rocket.explode()

        if self.rocket.time_since_explosion > Config.EXPLOSION_DURATION_MS:
            self.rocket.set_inactive()

    def destroy(self):
        self.is_destroyed = True

    def _reset(self):
        self.is_destroyed = False
        self.is_active = True
        self.delay_since_explosion = 0
        self.rect.center = Config.SPACESHIP_STARTING_POSITION


class Laser:
    def __init__(self):
        self.time_since_explosion = 0
        self.is_active = False
        self.movement_speed = Config.LASER_MOVESPEED
        self.rect = None
        self.laser_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(Config.SPRITES_DIR, 'laser.png')),
            Config.LASER_RECT_DIM
        )
        self.sound = pygame.mixer.Sound(
            os.path.join(Config.SOUNDS_DIR, Config.LASER_SHOOT_SOUND))
        self.explosion_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(
                Config.SPRITES_DIR, Config.LASER_EXPLOSION_SPRITE_FNAME)),
            Config.MISSILE_EXPLOSION_SIZE
        )

    def _move(self):
        self.rect.y += self.movement_speed

    def update(self, dt):
        if not self.is_active:
            return

        if self.is_exploded:
            self.time_since_explosion += dt
        else:
            self._move()

    def shoot(self, rect):
        self.rect = rect
        self.is_exploded = False
        self.is_active = True
        # self.sound.play()

    def draw(self, surface):
        if not self.is_active:
            return

        if self.is_exploded:
            surface.blit(
                self.explosion_sprite,
                self.explosion_sprite.get_rect(center=self.rect.center))

        surface.blit(
            self.laser_sprite,
            self.laser_sprite.get_rect(center=self.rect.center)
        )

        # pygame.draw.rect(surface, (0, 255, 0), self.rect)

    def explode(self):
        self.is_exploded = True

    def set_inactive(self):
        self.is_active = False


class Alien:

    def __init__(self, type_, top_left_pos):
        self.last_sprite_shift_delay = 0
        self.type = type_
        self.sprites = [
            pygame.image.load(os.path.join(Config.SPRITES_DIR, s))
            for s in Config.ALIEN_SPRITE_NAMES[self.type - 1]]
        self.explosion_sprite = pygame.image.load(
            os.path.join(Config.SPRITES_DIR,
                         Config.ALIEN_EXPLOSION_SPRITE_NAME))

        self.is_exploded = False
        self.delay_since_explosion = 0
        self.sprite_index = 0

        self.rect = self.sprites[self.sprite_index].get_rect(
            topleft=top_left_pos)

        self.shift_sprite_period = Config.ALIEN_SPRITE_SHIFT_PERIOD_MS

        self.laser = Laser()

    def update(self, dt, movement):
        if self.is_exploded:
            self.delay_since_explosion += dt

        self._move(movement)
        self._sprite_shift(dt)
        self._update_laser(dt)

    def _move(self, movement):
        self.rect.y += movement[1]
        self.rect.x += movement[0]

    def _sprite_shift(self, dt):
        self.last_sprite_shift_delay += dt
        if self.last_sprite_shift_delay > self.shift_sprite_period:
            self.sprite_index += 1
            self.sprite_index %= len(self.sprites)
            self.last_sprite_shift_delay -= self.shift_sprite_period

    def draw(self, window_surface):
        if self.is_exploded:
            explosion_rect = self.explosion_sprite.get_rect()
            explosion_rect.center = self.rect.center
            window_surface.blit(self.explosion_sprite, explosion_rect)
        else:
            window_surface.blit(self.sprites[self.sprite_index], self.rect)
            self.laser.draw(window_surface)

    def explode(self):
        self.is_exploded = True

    def shoot_laser(self):
        rect = pygame.Rect(
            self.rect.centerx - (Config.LASER_RECT_DIM[0] // 2),
            self.rect.top - Config.LASER_RECT_DIM[1],
            Config.LASER_RECT_DIM[0],
            Config.LASER_RECT_DIM[1]
        )
        self.laser.shoot(rect)

    def _update_laser(self, dt):
        if not self.laser.is_active:
            return

        self.laser.update(dt)

        if self.laser.rect.bottom > Config.WORLD_DIM[1]:
            self.laser.rect.top = Config.WORLD_DIM[1] + 40
            self.laser.explode()

        if self.laser.time_since_explosion > Config.EXPLOSION_DURATION_MS:
            self.laser.set_inactive()


class Aliens:
    def __init__(self):
        self.delay_since_last_shoot = 0
        self.alien_list = self.create_aliens()
        self.rect = self._get_rect()

        self.movement_direction = Directions.RIGHT
        self.acceleration_step = 0
        self.ufo = UFO()

    def create_aliens(self):
        aliens = []
        alien_sprites = [[pygame.image.load(os.path.join(Config.SPRITES_DIR, s))
                          for s in ss] for ss in Config.ALIEN_SPRITE_NAMES]

        max_w = max([sprites[0].get_rect().w for sprites in alien_sprites])
        max_row_size = max([len(row) for row in Config.ALIEN_FORMATION])
        step = Config.ALIEN_FORMATION_WIDTH_PIXELS / max_row_size
        x0 = (-max_w) // 2 + (Config.WORLD_DIM[0] -
                              Config.ALIEN_FORMATION_WIDTH_PIXELS) // 2
        xs = [x0 + (step * i) for i in range(max_row_size)]
        for row_index, alien_row in enumerate(Config.ALIEN_FORMATION):
            for i, alien_index in enumerate(alien_row):
                sprites = alien_sprites[alien_index - 1]
                w, h = (sprites[0].get_rect().w, sprites[0].get_rect().h)
                center_x = xs[i]
                center_y = h + (2 * h * row_index) + Config.ALIEN_STARTING_POS_Y

                aliens.append(
                    Alien(alien_index, (center_x - w // 2, center_y - h // 2)))
        return aliens

    def update(self, dt):
        self._update_aliens(dt)
        self._update_lasers(dt)
        self._update_ufo(dt)

    def draw(self, window_surface):
        for alien in self.alien_list:
            alien.draw(window_surface)
        self.ufo.draw(window_surface)

    def _update_lasers(self, dt):
        if self.delay_since_last_shoot > Config.LASER_SHOOT_FREQ:
            self._fire()
            self.delay_since_last_shoot = 0
        else:
            self.delay_since_last_shoot += dt

    def _update_aliens(self, dt):
        # self._fire(dt)
        self._remove_aliens()
        self._update_alien(dt)

    def _update_alien(self, dt):
        if not self.alien_list:
            return

        movement = self._get_alien_movement(dt)
        for alien in self.alien_list:
            alien.update(dt, movement)

    def _update_ufo(self, dt):
        self.ufo.update(dt)
        if self.ufo.time_since_explosion > Config.EXPLOSION_DURATION_MS:
            self.ufo.set_inactive()

    def _get_alien_movement(self, dt):
        direction = self.movement_direction[0]

        movement = (1 * direction[0], 0)

        self.rect = self._get_rect()
        self.rect.left += movement[0]
        self.rect.top += movement[1]

        if self.movement_direction == Directions.RIGHT and \
                self.rect.right >= Config.WORLD_DIM[0]:
            movement = (movement[0] - (self.rect.right - Config.WORLD_DIM[0]),
                        movement[1] + self.alien_list[0].rect.h)
            self.movement_direction = Directions.LEFT

            # If too far left, we drop one line and go right
        if self.movement_direction == Directions.LEFT and self.rect.left <= 0:
            movement = (movement[0] - self.rect.left,
                        movement[1] + self.alien_list[0].rect.h)
            self.movement_direction = Directions.RIGHT

        return movement

    def _get_rect(self):
        if not self.alien_list:
            return pygame.Rect((0, 0), (0, 0))

        x0 = min(alien.rect.left for alien in self.alien_list)
        y0 = min(alien.rect.top for alien in self.alien_list)
        x1 = max(alien.rect.right for alien in self.alien_list)
        y1 = max(alien.rect.bottom for alien in self.alien_list)
        rect = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
        return rect

    def _remove_aliens(self):
        for alien in self.alien_list:
            if alien.delay_since_explosion > Config.EXPLOSION_DURATION_MS:
                self._remove_alien(alien)

    def _remove_alien(self, alien):
        self.alien_list.remove(alien)

    def _fire(self):
        random.choice(self.alien_list).shoot_laser()


class Score:

    def __init__(self):
        self.value = 0
        self.digit_sprites = {
            i: pygame.transform.scale(
                pygame.image.load(os.path.join(Config.SPRITES_DIR, f'{i}.png')),
                (8, 12))
            for i in range(10)
        }
        self.score_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(
                Config.SPRITES_DIR, "score.png")), (75, 10))

    def draw(self, surf: pygame.Surface):
        score_str = str(self.value)
        while len(score_str) < Config.SCORE_DIGIT_COUNT:
            score_str = '0' + score_str

        x0, y0 = Config.SCORE_POS
        step = Config.SCORE_DIGIT_X_SPACE_PIXELS
        r = self.digit_sprites[0].get_rect()
        r.topleft = (x0, y0 - (r.h * 2))
        surf.blit(self.score_sprite, r)

        for digit in score_str:
            r.topleft = (x0, y0)
            surf.blit(self.digit_sprites[int(digit)], r)
            x0 += r.w + step


class Lives:
    def __init__(self):
        self.value = 3
        self.life_point_size = 30

        self.spaceship_sprite = pygame.transform.scale(pygame.image.load(
            os.path.join(Config.SPRITES_DIR, Config.SPACESHIP_SPRITE_FNAME)),
            (self.life_point_size, self.life_point_size)
        )
        self.numbers_sprites = {
            i: pygame.transform.scale(
                pygame.image.load(os.path.join(Config.SPRITES_DIR, f'{i}.png')),
                (8, 12))
            for i in range(4)
        }
        self.y_pos = Config.LIVES_Y_COORDINATE
        self.x_pos = Config.LIVES_X_COORDINATE

    def draw(self, surface):
        x_0, y_0 = self.x_pos, self.y_pos
        curr_number_sprite = self.numbers_sprites.get(self.value)
        if curr_number_sprite is None:
            return
        r = curr_number_sprite.get_rect()
        r.center = (x_0, y_0)
        surface.blit(curr_number_sprite, r)

        x_0 += self.life_point_size
        y_0 -= 15
        for i in range(self.value):
            surface.blit(
                self.spaceship_sprite,
                pygame.Rect(
                    self.life_point_size * (i + 1), y_0,
                    self.life_point_size, self.life_point_size
                )
            )

    def die(self):
        self.value -= 1


class GameOver:
    def __init__(self):
        self.game_over_sprite = pygame.image.load(
            os.path.join(Config.SPRITES_DIR, "game_over.png"))

    def draw(self, surf: pygame.Surface):
        w, h = Config.WORLD_DIM
        center = (w // 2, h // 2)
        surf.blit(self.game_over_sprite,
                  self.game_over_sprite.get_rect(center=center))


class BestScore:
    def __init__(self):
        self.value = 0
        self.best_score_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(
                Config.SPRITES_DIR, Config.BEST_SCORE_SPRITE_FNAME)), (90, 10))

        self.digit_sprites = {
            i: pygame.transform.scale(
                pygame.image.load(os.path.join(Config.SPRITES_DIR, f'{i}.png')),
                (8, 12))
            for i in range(10)
        }

    def draw(self, surface):
        score_str = str(self.value)
        score_str = '0' * (
                    Config.SCORE_DIGIT_COUNT - len(score_str)) + score_str
        x_0, y_0 = Config.HIGH_SCORE_POS
        step = Config.SCORE_DIGIT_X_SPACE_PIXELS
        r = self.digit_sprites[0].get_rect()
        r.topleft = (x_0, y_0 - (r.h * 2))
        surface.blit(self.best_score_sprite, r)

        for digit in score_str:
            r.topleft = (x_0, y_0)
            surface.blit(self.digit_sprites[int(digit)], r)
            x_0 += r.w + step


class UFO:

    def __init__(self):

        self.is_destroyed = False
        self.sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(Config.SPRITES_DIR,
                                           Config.UFO_SPRITE_NAME)),
            (90, 55)
        )
        self.explosion_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(Config.SPRITES_DIR,
                                           Config.UFO_EXPLOSION_SPRITE_NAME)),
            (70, 70)
        )

        self.rect = self.sprite.get_rect()
        self.is_exploded = False
        self.time_since_explosion = 0

        self.is_active = False
        self.direction = 1

    def launch(self):
        self.rect = self.sprite.get_rect(topleft=(50, 50))
        self.is_active = True

        self.is_exploded = False
        self.time_since_explosion = 0

    def update(self, dt):
        if self.is_exploded:
            self.time_since_explosion += dt
        self._move()

    def _move(self):
        if self.is_exploded:
            return

        self.rect.x += self.direction * 8

        if self.rect.right > Config.WORLD_DIM[0]:
            self.direction = -1
        elif self.rect.left < 0:
            self.direction = 1

    def draw(self, surf: pygame.Surface):
        if not self.is_active:
            return

        if self.is_exploded:
            surf.blit(self.explosion_sprite, self.rect)
        else:
            surf.blit(self.sprite, self.rect)

    def explode(self):
        self.is_exploded = True

    def set_inactive(self):
        self.is_active = False

    def destroy(self):
        self.explode()
        self.is_destroyed = True


class Asteroids:
    def __init__(self):
        self.sprite = pygame.transform.scale(pygame.image.load(
            os.path.join(Config.SPRITES_DIR, Config.ASTEROID_SPRITE_FNAME)),
                                             (15, 15))
        self.asteroids = self.generate_asteroids()

    def generate_asteroids(self):
        xmin, ymin, xmax, ymax = 20, 240, Config.WINDOW_SIZE[0] - 20, 290
        container = []

        while len(container) < 8:
            sprite = pygame.transform.scale(pygame.image.load(
                os.path.join(Config.SPRITES_DIR, Config.ASTEROID_SPRITE_FNAME)),
                (40, 40))
            x, y = random.choice(range(xmin, xmax)), \
                   random.choice(range(ymin, ymax))
            rect = sprite.get_rect(center=(x, y))

            ignore = False
            for a, r in container:
                if r.colliderect(rect):
                    ignore = True
                    break

            if not ignore:
                container.append((sprite, rect))
        return container

    def draw(self, surface):
        for ast, r in self.asteroids:
            if ast is None:
                continue
            surface.blit(ast, r)
