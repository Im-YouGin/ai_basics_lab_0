import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Convolution2D
from tensorflow.keras.optimizers import Adam
from rl.agents import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy

from space_env import SpaceInvadersEnv


def build_model(h, w, ch, acts):
    model = Sequential()
    model.add(Convolution2D(32, (8, 8), strides=(4, 4), activation='relu',
                            input_shape=(3, h, w, ch)))
    model.add(Convolution2D(64, (4, 4), strides=(2, 2), activation='relu'))
    model.add(Convolution2D(64, (3, 3), activation='relu'))
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(acts, activation='linear'))
    return model


def build_agent(height, width, channels, actions):
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1.,
                                  value_min=.1, value_test=.2, nb_steps=10000)
    memory = SequentialMemory(limit=1000, window_length=3)
    model = build_model(height, width, channels, actions)
    dqn = DQNAgent(
        model=model, memory=memory, policy=policy,
        enable_dueling_network=True, dueling_type='avg',
        nb_actions=actions, nb_steps_warmup=1000
    )
    dqn.compile(Adam(lr=1e-4))
    return dqn


def fit_agent():
    dqn = build_agent(HEIGHT, WIDTH, CHANNELS, ACTIONS)

    dqn.fit(env, nb_steps=10000, visualize=False, verbose=2)

    dqn.save_weights('dqn_weights.h5')


if __name__ == '__main__':
    env = SpaceInvadersEnv()
    HEIGHT, WIDTH, CHANNELS = env.observation_space.shape
    ACTIONS = env.action_space.n

    fit_agent()

