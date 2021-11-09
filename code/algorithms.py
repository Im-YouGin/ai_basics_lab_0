import itertools
import random


class Node:
    def __init__(self, game):
        self.game = game

    def get_children(self, max_player, rand_behavior=False):
        children = []
        if max_player:
            for action in self.game.player.sprite.get_available_actions():
                game_cp = self.game.copy()
                game_cp.player.sprite.perform_action(action)
                game_cp.player.sprite.recharge()
                game_cp.player.sprite.lasers.update()
                game_cp.collision_checks()
                children.append(Node(game_cp))
        else:
            act_lst = []
            for alien in self.game.aliens:
                a = alien.get_available_actions(
                    self.game.player.sprite.lasers.sprites(),
                    self.game.aliens.sprites(), self.game.max_x_constraint)

                act_lst.append(a)

            for p in itertools.product(*act_lst):
                game_cp = self.game.copy()
                game_cp.alien_shoot()
                for alien, action in zip(game_cp.aliens, p):
                    if rand_behavior and random.random() > .5:
                        alien.perform_action(action, game_cp.alien_direction)
                game_cp.alien_lasers.update()
                game_cp.alien_position_checker()
                game_cp.collision_checks()
                children.append(Node(game_cp))

        return children

    def evaluate(self):
        ds = self.game.player.sprite.dists_to_lasers(self.game.alien_lasers.sprites())
        if not ds:
            ds.append(float('inf'))

        a = self.game.player.sprite.dist_to_closest_laser(
                   self.game.alien_lasers.sprites())
        b = self.game.dist_from_ship_to_alien()

        return a - b - sum(ds) / len(ds)

    def victory(self):
        return not self.game.aliens.sprites()

    def game_over(self):
        return self.game.lives <= 0


def best_move(game, algo='minimax'):
    acts = game.player.sprite.get_available_actions()

    best_act = None
    best_score = -float('inf')

    for action in acts:
        game_cp = game.copy()
        game_cp.player.sprite.perform_action(action)

        if algo == 'minimax':
            score = \
                minimax(Node(game_cp), 4, -float('inf'), float('inf'), False)
        else:
            score = \
                expectimax(Node(game_cp), 5, False)

        if score > best_score:
            best_score = score
            best_act = action

    return best_act


def minimax(node, depth, alpha, beta, max_player):
    if depth == 0 or node.victory() or node.game_over():
        return node.evaluate()

    if max_player:
        max_eval = -float('inf')
        for child_node in node.get_children(max_player):
            score = minimax(child_node, depth - 1, alpha, beta, False)

            max_eval = max(alpha, score)
            if beta <= alpha:
                break
        return max_eval

    else:
        min_eval = float('inf')
        for child_node in node.get_children(max_player):
            score = minimax(child_node, depth - 1, alpha, beta, True)
            min_eval = min(beta, score)
            if beta <= alpha:
                break
        return min_eval


def expectimax(node, depth, max_player):
    if depth == 0 or node.victory() or node.game_over():
        return node.evaluate()

    if max_player:
        max_eval = -float('inf')
        for child_node in node.get_children(max_player):
            score = expectimax(child_node, depth - 1, False)
            max_eval = max(max_eval, score)
        return max_eval

    else:
        scores = [expectimax(child_node, depth - 1, True)
                  for child_node in node.get_children(max_player,
                                                      rand_behavior=True)]
        return sum(scores) / len(scores)

