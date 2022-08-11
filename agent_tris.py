from tris import *
from planner_tris import GameTree


class Agent:
    def __init__(self, game, player, suboptimal_prob=0.5):
        self.game = game         # Tris object
        self.player = player    # what Pepper will play as: Tris.X or Tris.O
        self.tree = GameTree(game.board, Tris.X)
        self.tree.construct_tree()
        self.suboptimal_prob = suboptimal_prob

    def on_my_turn(self):
        # get the best move from the tree
        move = self.tree.get_optimal_or_random_move(self.suboptimal_prob)[0]
        # maintain only the tree with the chosen move
        self.tree = self.tree.get_child_by_move(move)
        return move
    
    def on_opponent_move(self, move):
        opp_made_optimal_move = self.tree.move_is_optimal(move)
        # maintain only the tree with the chosen move
        self.tree = self.tree.get_child_by_move(move)
        return opp_made_optimal_move
