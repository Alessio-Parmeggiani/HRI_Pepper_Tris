# use a game tree to play tris optimally (or not!)

from tris import *

import random

class GameTree:
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.children = []
        self.score = 0
        self.depth = 0
        self.move = None    # tuple (row,col) : the move that was executed to get to this node


    def __str__(self):
        return str(self.board)

    def __repr__(self):
        return str(self.board)

    def __eq__(self, other):
        return self.board == other.board
    
    def __hash__(self):
        return hash(self.board)
    
    # get child by move
    def get_child_by_move(self, move):
        print ("seachin for ", move)
        for child in self.children:
            print child.move
            if child.move == move:
                return child
        return None

    #remove children that don't correspond to move
    def prune_children_other_than_move(self, move):
        for child in self.children:
            if child.move != move:
                self.children.remove(child)
    
    # construct game tree
    def construct_tree(self):
        # assign score to this based on winner
        goaw = get_game_over_and_winner(self.board)
        if goaw[0] == True: 
            if goaw[1] == Tris.X:
                self.score = 1.0/self.depth    # value early wins higher
            elif goaw[1] == Tris.O:
                self.score = -1.0/self.depth   # value early wins higher
            else:
                self.score = 0
            return

        # TODO possible heruistics in the future


        #for each available move in the game, create a child tree
        # the available moves correspond exactly to the empty spaced in the board
        for i in xrange(len(self.board)):
            for j in xrange(len(self.board)):
                if self.board[i][j] == Tris.EMPTY:
                    # this is an available move, so build new subtree
                    new_board = [row[:] for row in self.board]   # copy board
                    new_board[i][j] = self.player
                    child = GameTree(new_board, Tris.X if self.player == Tris.O else Tris.O)
                    child.depth = self.depth + 1
                    child.move = (i, j)
                    self.children.append(child)
                    child.construct_tree()
        
    def get_max_move(self): 
        if len(self.children) == 0:
            return None, self.score
        max_child = None
        max_score = -1
        for child in self.children:
            #continue match for each children
            subtree_score = child.get_optimal_move()[1]
            if subtree_score >= max_score:
                max_child = child
                max_score = subtree_score
        return max_child.move, max_score
    
    def get_min_move(self):
        if len(self.children) == 0:
            return None, self.score
        min_child = None
        min_score = +1
        for child in self.children:
            subtree_score = child.get_optimal_move()[1]
            if subtree_score <= min_score:
                min_child = child
                min_score = subtree_score
        return min_child.move, min_score

    #get optimal move
    def get_optimal_move(self):
        #X player maximizes
        if self.player == Tris.X:
            return self.get_max_move()
        else:
            #O player minimizes
            return self.get_min_move()

    def get_worst_move(self):
        #X player would maximize, but...
        if self.player == Tris.X:
            return self.get_min_move()
        else:
            #O player would minimize, but...
            return self.get_max_move()
    
    # select a random move from the available ones (i.e. children)
    def get_random_move(self):
        return random.choice(self.children).move, 0

    def get_optimal_or_random_move(self, epsilon):
        if random.random() < epsilon:
            print "doing random move"
            return self.get_random_move()
        else:
            print "doing optimal move"
            return self.get_optimal_move()

    ##### Francesco's experimentation. Further test (by everyone) pending.
    # mercifulness score is: (max_depth/9) - !opponent_can_win     (guaranteed to be in [-1,1])
    # i.e. stall the game, but leave a way for the human to win
    # returns: (move, score, depth, opponent_can_win)
    def get_merciful_move(self):
        if len(self.children) == 0:
            opponent_won = self.score>0 if this.player==Tris.O else self.score<0
            mercy_score = (self.depth/9.0) - (1 if not opponent_won else 0)
            return None, mercy_score, self.depth, opponent_won
        best_child = None
        best_score = -1
        best_depth = None
        best_opp_can_win = None
        for child in self.children:
            move, minmax_score = child.get_optimal_move()   # assume the opponent is playing to win AND they expect Pepper to also be playing to win
            # fortunately the minmax score allows us to derive all info we need by construction
            if minmax_score == 0:
                mercy_depth = 9   # necessarily, a draw can only happen on a full board
            else:
                mercy_depth = round(1.0/abs(minmax_score))
            opponent_won = minmax_score>0 if child.player==Tris.X else minmax_score<0
            # the above is a worst-case estimate of opponent_can_win:
            # if the opponent can win under optimal Pepper plays, then there is certainly a way to win,
            # albeit it is possible that the opponent didn't win under optimal Pepper plays but could if Pepper was merciful some other time

            mercy_score = (mercy_depth/9.0) - (1 if not opponent_won else 0)
            if mercy_score >= best_score:
                best_child = child
                best_score = mercy_score
                best_depth = mercy_depth
                best_opp_can_win = opponent_won
        
        return best_child.move, best_score, best_depth, best_opp_can_win
    
    def get_optimal_or_merciful_move(self, epsilon):
        if random.random() < epsilon:
            print "doing merciful move"
            return self.get_merciful_move()
        else:
            print "doing optimal move"
            return self.get_optimal_move()
