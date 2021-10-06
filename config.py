import os


thisdir = os.path.dirname(os.path.abspath(__file__))


class Directions:
    LEFT = (-1, 0),
    RIGHT = (1, 0),
    UP = (0, -1),
    DOWN = (0, 1),
    IDLE = (0, 0)


class Config:

    ASTEROID_SPRITE_FNAME = 'asteroid.png'
    SPACESHIP_EXPLOSION_DURATION_MS = 1000
    UFO_EXPLOSION_SPRITE_NAME = 'ufo_explosion.png'
    UFO_SPRITE_NAME = 'ufo.png'

    LASER_SHOOT_FREQ = 2000
    MISSILE_EXPLOSION_SIZE = (40, 40)
    LASER_EXPLOSION_SPRITE_FNAME = 'laser_explosion.png'
    SOUNDS_DIR = os.path.join(thisdir, 'sounds')
    ROCKET_SHOOT_SOUND = 'rocket_sound.wav'
    LASER_SHOOT_SOUND = 'laser_shoot_sound.wav'
    ROCKET_MOVESPEED = 9
    LASER_MOVESPEED = 5
    BEST_SCORE_SPRITE_FNAME = 'best_score.png'

    LASER_RECT_DIM = (10, 25)
    ALIEN_SPRITE_SHIFT_PERIOD_MS = 1000
    ALIEN_SPRITE_NAMES = [
        ["alien1_frame1.png", "alien1_frame2.png"],
        ["alien2_frame1.png", "alien2_frame2.png"],
        ["alien3_frame1.png", "alien3_frame2.png"],
    ]

    ALIEN_EXPLOSION_SPRITE_NAME = "alien_explosion.png"
    EXPLOSION_DURATION_MS = 250
    ROCKET_EXPLOSION_SPRITE_FNAME = 'rocket_explosion.png'
    ROCKET_SPRITE = 'rocket3.png'
    MISSILE_RECT_DIM = (14, 7)
    WINDOW_SIZE = (400, 400)
    WORLD_DIM = (400, 375)

    LIVES_X_COORDINATE = WINDOW_SIZE[0] * 0.05
    LIVES_Y_COORDINATE = WINDOW_SIZE[1] * .95

    SPRITES_DIR = os.path.join(thisdir, 'sprites')
    SPACESHIP_SPRITE_FNAME = 'bgspeedship.png'
    SPACESHIP_DESTRUCTION_SPRITE_FNAME = 'spaceship_explosion.png'
    SPACESHIP_STARTING_POSITION = (WORLD_DIM[0] // 2, WORLD_DIM[1] * 9 // 10)

    SCORE_POS = (40, WORLD_DIM[1] // 10)
    SCORE_DIGIT_COUNT = 5
    SCORE_DIGIT_X_SPACE_PIXELS = 4

    ALIEN_FORMATION = [
        [3, 3, 3, 3, 3,
         # 3, 3, 3,
         # 3, 3, 3
         ],
        # [2, 2, 2, 2, 2,
        #  # 2, 2, 2,
        #  # 2, 2, 2
        #  ],
        [2, 2, 2, 2, 2,
         # 2, 2, 2,
         # 2, 2, 2
         ],
        # [1, 1, 1, 1, 1,
        #  # 1, 1, 1,
        #  # 1, 1, 1
        #  ],
        [1, 1, 1, 1, 1,
         # 1, 1, 1,
         # 1, 1, 1
         ]
    ]
    ALIEN_FORMATION_WIDTH_PIXELS = WORLD_DIM[0] * 0.8
    ALIEN_FIRING_PERIOD_MS = 1000
    ALIEN_STARTING_POS_Y = WORLD_DIM[1] * 3 // 15

    HIGH_SCORE_POS = (WORLD_DIM[0] - 165, WORLD_DIM[1] // 10)


zoom = 5