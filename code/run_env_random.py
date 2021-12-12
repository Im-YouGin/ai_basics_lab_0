from space_env import SpaceInvadersEnv
import random


if __name__ == '__main__':
    env = SpaceInvadersEnv()
    obs = env.reset()
    env.render()

    action_length = env.action_space.n

    episodes = 1000
    i = 1

    scores = []

    while i <= episodes:
        action = random.randint(0, action_length - 1)
        obs, reward, done, info = env.step(action)
        env.render()

        if done:
            env.reset()
            i += 1
