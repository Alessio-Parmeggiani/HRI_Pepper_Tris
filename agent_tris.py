from tris import *
from planner_tris import GameTree


class Agent:
    def __init__(self, game, player):
        self.game = game         # Tris object
        self.player = player    # what Pepper will play as: Tris.X or Tris.O
        self.tree = GameTree(game.board, Tris.X)
        self.tree.construct_tree()

    def on_my_turn(self):
        # get the best move from the tree
        move = self.tree.get_optimal_move()[0]
        # maintain only the tree with the chosen move
        self.tree = self.tree.get_child_by_move(move)
        return move
    
    def on_opponent_move(self, move):
        # maintain only the tree with the chosen move
        self.tree = self.tree.get_child_by_move(move)
        return
