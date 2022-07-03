import os, sys
import math
import time

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

from behavior_waitable import BehaviorWaitable
from tris import *
from planner_tris import *
from agent_tris import *

import threading
from webserver import go

vocabulary_yesno = ["yes", "no", "yes please", "no thank you"]
game = None    # Blackboard needs this global, and Pepper can only play one game at a time regardless

# classes for the webserver

class Blackboard():
    def __init__(self):
        self.the_handler = None
        self.clicked_move = None
        self.user_experience=None
        self.user_age=None
    
    def onclick(self, move):
        if not self.clicked_move:
            valid = game.move(*move)
            if valid:
                self.clicked_move = move
                web_board=game.get_board_for_tablet()
                ws_handler.send(web_board)
                # TODO suono e/o lucetta (no motion)


class WebServerThread(threading.Thread):
    def __init__(self, bb):
        threading.Thread.__init__(self)
        self.bb = bb

    def run(self):
        go(self.bb)

def parse_move(response):
    player_row=None
    player_col=None
    
    if "A" in response:
        player_row = 0
    if "B" in response:
        player_row = 1
    if "C" in response:
        player_row = 2
        
    if "1" in response:
        player_col = 0
    if "2" in response:
        player_col = 1
    if "3" in response:
        player_col = 2

    player_move = (player_row, player_col)
    
    return player_move


def pepper_turn(agent):
    pepper_move = agent.on_my_turn()
    game.move(*pepper_move)

    #TODO thinking led
    #TODO gesture

### end pepper_turn()

def player_turn(agent):
    point_tablet = BehaviorWaitable("tris-behaviours-25/Alessio/point_tablet")
    pepper_cmd.robot.say('Your move :)')
    #point_tablet.wait()     
    #human move
    #recognize move speech
    vocabulary_player_move = ["A 1", "A 2", "A 3", "B 1", "B 2", "B 3", "C 1", "C 2", "C 3",
                              "1 A", "2 A", "3 A", "1 B", "2 B", "3 B", "1 C", "2 C", "3 C",]
    response = ""  # the default response from pepper_cmd's ASR
    impatience_score = 0
    pepper_responses = ["your turn", "come on", "i'm sleeping", "uff..."]
    player_move = None
    #TODO led waiting
    while True:
        timeout = 7 + 6*random.random()
        response = pepper_cmd.robot.asr(vocabulary_player_move, timeout=timeout, enableWordSpotting=True)

        # don't do anything else if the move was done via click
        if the_bb.clicked_move:
            player_move = the_bb.clicked_move
            the_bb.clicked_move = None
            break

        if response:
            player_move = parse_move(response)
            valid = game.move(*player_move)
            if valid:
                break
            else: # invalid move
                # TODO invalid move gest
                pepper_cmd.robot.say("You can't play there!")
                print "invalid move"
        else: # ASR timed out
            gest = BehaviorWaitable("tris-behaviours-25/daniele/gesture_turn_1")  # TODO change gest w/ impatience
            pepper_cmd.robot.say(pepper_responses[impatience_score])

            if impatience_score+1 < len(pepper_responses):
                impatience_score += 1
        
    agent.on_opponent_move(player_move)

    #TODO feedback
    pepper_cmd.robot.say('Good move :)')

### end player_turn()


# In which Pepper plays ONE game
# returns the winner: Tris.X, Tris.O, Tris.DRAW
def play_game(difficulty_bias, pepper_player):

    global game

    print "initializing game...."
    pepper_cmd.robot.say("Please wait while I load the game...")
    #TODO placeholder for loading
    game = Tris()
    agent = Agent(game, pepper_player, difficulty_bias)
    
    #START MATCH
    while not game.get_game_over_and_winner()[0]:

        if game.get_current_player() == pepper_player:
            pepper_turn(agent)
        else:
            player_turn(agent)
        
        # update tablet
        web_board=game.get_board_for_tablet()
        ws_handler.send(web_board)
            
        print game

        #check victory
        if game.get_game_over_and_winner()[0]:
            break

    
    #END MATCH
    return game.get_game_over_and_winner()[1]

### end play_game()


# This includes all the interaction with a new user
def interact():

    pepper_cmd.robot.say('Hello')
    pepper_cmd.robot.say('Wanna play tris?')
    response = pepper_cmd.robot.asr(vocabulary_yesno, enableWordSpotting=True)


    print "FORCING YES"   # DEBUG ONLY; TODO remove
    response = "yes!!!"
    
    if "yes" in response:
        # TODO
        welcome = BehaviorWaitable("tris-behaviours-25/francesco/welcome")
        pepper_cmd.robot.say('yeah')
        welcome.wait()
        
        #SET PARAMETERS FOR PLAY
        pepper_player = Tris.X
        human_player = Tris.O

        point_tablet = BehaviorWaitable("tris-behaviours-25/Alessio/point_tablet")
        pepper_cmd.robot.say("Please select a difficulty level on my tablet")
        while not the_bb.user_age or not the_bb.user_experience: 
            #wait for difficulty input 
            pass


        #PROFILING
        user_age=the_bb.user_age
        user_experience=the_bb.user_experience
        #combine user age and user experience like in f1 score
        difficulty_bias=1-(2*(user_age * user_experience)/(user_age + user_experience))
        print "initial difficulty is: ", difficulty_bias

        play_again = True
        
        while play_again:
            #initialize board and play
            winner = play_game(difficulty_bias, pepper_player)

            print "^_^"
            print ""
            print "WINNER IS:  " + str(winner)
            print ""

            if winner == pepper_player:
                win = BehaviorWaitable("tris-behaviours-25/Alessio/victory")
                pepper_cmd.robot.say('I win')
                # TODO update difficulty somehow
                win.wait()
            else:
                lose = BehaviorWaitable("tris-behaviours-25/Alessio/defeat")
                pepper_cmd.robot.say('Oh no')
                # TODO update difficulty somehow
                lose.wait()
            
            pepper_cmd.robot.say('Wanna play again?')
            response = pepper_cmd.robot.asr(vocabulary_yesno, enableWordSpotting=True)
            play_again = "yes" in response
        ### end while

        # get here when user wants to stop playing
        # TODO Pepper ci dice il punteggio finale?
        goodbye = BehaviorWaitable("tris-behaviours-25/francesco/goodbye2")
        pepper_cmd.robot.say('Oh, okay. Goodbye.')
        goodbye.wait()


    else:   # answered NO to "wanna play tris?"
        goodbye = BehaviorWaitable("tris-behaviours-25/francesco/goodbye2")
        pepper_cmd.robot.say('Oh, okay. Goodbye.')
        goodbye.wait()

### end interact()




begin()

the_bb = Blackboard()

the_webserver_thread = WebServerThread(the_bb)
the_webserver_thread.start()

#wait for connection
while not the_bb.the_handler:
    pass

ws_handler = the_bb.the_handler

while True:

    # TODO wait for sonar

    interact()

    time.sleep(2)


end()