from tris import *
from planner_tris import *
from agent_tris import *

class GameManager:
    def __init__(self, pepper_player):
        self.game = Tris()
        self.pepper_player = pepper_player
        self.agent = Agent(self.game, pepper_player)
    
    def on_human_move(self, move):
        pass  # TODO

    def play_match(self):
        self.game.reset()
        self.agent = Agent(self.game, self.pepper_player)
        while not self.game.get_game_over_and_winner()[0]:
            #agent turn
            opponent_move=self.agent.on_my_turn()
            self.game.move(*opponent_move)

            print self.game

            if self.game.get_game_over_and_winner()[0]:
                break

            #player turn
            player_row = int(input("your row: "))
            player_col = int(input("your column: "))
            player_move = (player_row, player_col)

            print("your move is: ",player_move)
            self.game.move(*player_move)
            self.agent.on_opponent_move(player_move)

            print self.game
    
        print "WINNER IS:  " + str(self.game.get_game_over_and_winner()[1])
            
            
if __name__ == "__main__":
    game_manager = GameManager(Tris.X)
    game_manager.play_match()
