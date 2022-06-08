# use a game tree to play tris optimally

from tris import *

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
                self.score = 1/self.depth    # value early wins higher
            elif goaw[1] == Tris.O:
                self.score = -1/self.depth   # value early wins higher
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


