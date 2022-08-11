#This file is in python 2.7
#class for tris architecture

class Tris:
    EMPTY = 0
    X = 1
    O = 2
    DRAW = 0

    def __init__(self):
        self.board = [
            [Tris.EMPTY, Tris.EMPTY, Tris.EMPTY,],
            [Tris.EMPTY, Tris.EMPTY, Tris.EMPTY,],
            [Tris.EMPTY, Tris.EMPTY, Tris.EMPTY,],
        ]
        #X starts first
        self.current_player = Tris.X
    
    def reset(self):
        self.board = [
            [Tris.EMPTY, Tris.EMPTY, Tris.EMPTY,],
            [Tris.EMPTY, Tris.EMPTY, Tris.EMPTY,],
            [Tris.EMPTY, Tris.EMPTY, Tris.EMPTY,],
        ]
        #X starts first
        self.current_player = Tris.X
        
    # get current player
    def get_current_player(self):
        return self.current_player
    
    # check if a space is empty
    def is_empty(self, row, col):
        return self.board[row][col] == Tris.EMPTY
    
    # get a copy of the board
    def get_board(self):
        return [row[:] for row in self.board]

    #make move
    def move(self, row, col):
        print row
        print col
        if self.board[row][col] != Tris.EMPTY:
            return False
        self.board[row][col] = self.current_player
        self.current_player = Tris.O if self.current_player == Tris.X else Tris.X
        return True

    #check if game is over
    def get_game_over_and_winner(self):
        return get_game_over_and_winner(self.board)    # w/o `self.` it refers to the global method outside
    
    #check if a player may win next move
    def player_is_threatening(self, player):
        return player_is_threatening(self.board, player)    # w/o `self.` it refers to the global method outside
    
    #print class in pretty way
    def __str__(self):
        s = ''
        for row in self.board:
            for cell in row:
                s += ' ' + ('X' if cell == Tris.X else 'O' if cell == Tris.O else ' ')
            s += '\n'
        return s
    
    def get_board_for_tablet(self):
        s = ''
        for row in self.board:
            for cell in row:
                s += ('X' if cell == Tris.X else 'O' if cell == Tris.O else '.')
        return s





#check if game is over
def get_game_over_and_winner(board):
    # check rows
    for row in board:
        if row[0] != Tris.EMPTY and row[0] == row[1] == row[2]:
            return True, row[0]
    # check columns
    for col in range(3):
        if board[0][col] != Tris.EMPTY and board[0][col] == board[1][col] == board[2][col]:
            return True, board[0][col]
    # check diagonals
    if board[0][0] != Tris.EMPTY and board[0][0] == board[1][1] == board[2][2]:
        return True, board[0][0]
    if board[0][2] != Tris.EMPTY and board[0][2] == board[1][1] == board[2][0]:
        return True, board[0][2]
    
    #no one wins yet
    for row in board:
        for cell in row:
            if cell == Tris.EMPTY:
                return False, None
                
    #there is a draw
    return True, Tris.DRAW

# a player threatens a win if there is a row, col or diag where two spaces have its symbol and the third is empty.
# first an aux
def set_is_threatened(tile1, tile2, tile3, player):
    return (tile1 == tile2 == player and tile3 == Tris.EMPTY) or \
           (tile2 == tile3 == player and tile1 == Tris.EMPTY) or \
           (tile3 == tile1 == player and tile2 == Tris.EMPTY)
# then the real thing
def player_is_threatening(board, player):
    # check rows
    for row in board:
        if set_is_threatened(row[0], row[1], row[2], player):
            return True
    # check columns
    for col in range(3):
        if set_is_threatened(board[0][col], board[1][col], board[2][col], player):
            return True
    # check diagonals
    if set_is_threatened(board[0][0], board[1][1], board[2][2], player):
        return True
    if set_is_threatened(board[0][2], board[1][1], board[2][0], player):
        return True, board[0][2]


#test
if __name__ == "__main__":
    tris = Tris()

    print "Playing a match"
    #play a match
    while True:
        print tris
        row = int(input('row: '))
        col = int(input('col: '))
        if not tris.move(row, col):
            print 'invalid move'
        game_over, winner = tris.get_game_over_and_winner()
        if game_over:
            if winner == Tris.DRAW:
                print 'draw'
            else:
                print 'winner: ' + ('X' if winner == Tris.X else 'O')
            break
    print tris
 
 