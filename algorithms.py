import collections
from queue import PriorityQueue
from config import *


def bfs(grid, start):
    skip = True
    queue = collections.deque([[start]])
    seen = set([start])
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if grid[y][x] == -1:
            return path
        for x2, y2 in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= x2 < int(Config.WORLD_DIM[0] / zoom) + 1 \
                    and 0 <= y2 < int(Config.SPACESHIP_STARTING_POSITION[1] / zoom) + 1 \
                    and (x2, y2) not in seen and grid[y2][x2] != 3:

                if grid[y2][x2] != 2 or skip:
                    queue.append(path + [(x2, y2)])
                    seen.add((x2, y2))

                if grid[y2][x2] != 2:
                    skip = False


def ucs(grid, start):
    skip = True
    visited = set()
    queue = PriorityQueue()
    queue.put((0, [start]))

    while queue:
        cost, path = queue.get()
        x, y = path[-1]

        if (x, y) not in visited:
            visited.add((x, y))

            if grid[y][x] == -1:

                return path

            for x2, y2 in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= x2 < int(Config.WORLD_DIM[0] / zoom) + 1 \
                        and 0 <= y2 < int(
                    Config.SPACESHIP_STARTING_POSITION[1] / zoom) + 1 \
                        and (x2, y2) not in visited and grid[y2][x2] != 3:

                    if grid[y2][x2] != 2 or skip:
                        total_cost = cost + 1
                        queue.put((total_cost, path + [(x2, y2)]))

                    if grid[y2][x2] != 2:
                        skip = False


def dfs(grid, start):
    skip = True
    visited = set()
    stack = collections.deque([[start]])

    while stack:
        path = stack.pop()
        x, y = path[-1]

        if (x, y) in visited:
            continue

        visited.add((x, y))

        if grid[y][x] == -1:
            return path

        for x2, y2 in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= x2 < int(Config.WORLD_DIM[0] / zoom) + 1 \
                    and 0 <= y2 < int(Config.SPACESHIP_STARTING_POSITION[1] / zoom) + 1\
                    and (x2, y2) not in visited and grid[y2][x2] != 3:

                if grid[y2][x2] != 2 or skip:
                    stack.append(path + [(x2, y2)])

                if grid[y2][x2] != 2:
                    skip = False