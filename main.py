import os, sys
import math
import time
import random   # choice for responses

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

from behavior_waitable import BehaviorWaitable
from tris import *
from planner_tris import *
from agent_tris import *
from proxemics import *

import threading
from webserver import go

vocabulary_yesno = ["yes", "no", "yes please", "no thank you"]
game = None    # Blackboard needs this global, and Pepper can only play one game at a time regardless

# classes for the webserver

class Blackboard():
    def __init__(self):
        self.the_handler = None
        self.clicked_move = None
        self.user_experience = None
        self.user_age = None
    
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

def player_turn(agent, pepper_player, human_player):
    point_tablet = BehaviorWaitable("tris-behaviours-25/Alessio/point_tablet")
    pepper_cmd.robot.say(random.choice(('Your move :)', 'Your turn', 'Go', "What will you do?")))
    #point_tablet.wait()     
    #human move
    #recognize move speech
    vocabulary_player_move = ["A 1", "A 2", "A 3", "B 1", "B 2", "B 3", "C 1", "C 2", "C 3",
                              "1 A", "2 A", "3 A", "1 B", "2 B", "3 B", "1 C", "2 C", "3 C",]
    response = ""  # the default response from pepper_cmd's ASR
    impatience_score = 0
    impatience_responses = [
        "Hey, it's your turn",
        "Please, make a move",
        "Come on",
        "Don't think too hard",
        "Just pick a tile",
        "Entering sleep mode... Just kidding."
    ]
    impatience_gestures =  [
        "tris-behaviours-25/daniele/gesture_turn_1",
        "tris-behaviours-25/daniele/gesture_turn_1",
        "tris-behaviours-25/francesco/gesture_turn_3",
        "tris-behaviours-25/daniele/gesture_turn_1",
        "tris-behaviours-25/francesco/gesture_turn_3",
        "tris-behaviours-25/daniele/sleeping_gesture",
    ]
    player_move = None
    game_paused = False
    game_pause_countdown = 0
    #TODO led waiting
    while True:
        if proxemics.is_in_zone_for_delay(10,proxemics.AWAY_ZONE):
            #the user left, after 10 seconds the game is paused. Delay can be affected by the random delay below
            if not game_paused:
                print "user left"
                ws_handler.send("event pause-game")
                game_paused = True
                game_pause_countdown = 3 #countdown to go back to main screen
            
            print "countdown: " + str(game_pause_countdown)
            if game_pause_countdown == 1:
                ws_handler.send("event pause-game-warning")
            if game_pause_countdown == 0:
                raise Exception("user_left_timeout")
            game_pause_countdown -= 1
            
        elif game_paused:
            if proxemics.get_proximity_zone() < proxemics.AWAY_ZONE:
                #the user came back, the game is resumed
                print "user came back"
                ws_handler.send("event resume-game")
                pepper_cmd.robot.say("Glad to see you back! It's your turn now.")
                game_paused = False
        else:
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
                    gest = BehaviorWaitable("tris-behaviours-25/daniele/shake_head_gesture")
                    pepper_cmd.robot.say("You can't play there!")
                    print "invalid move"
            else: # ASR timed out
                gest = BehaviorWaitable(impatience_gestures[impatience_score])
                pepper_cmd.robot.say(impatience_responses[impatience_score])

                impatience_score += 1

                if impatience_score >= len(impatience_responses):
                    impatience_score = 2    # loop the most impatient ones
        
    human_did_optimal_move = agent.on_opponent_move(player_move)

    # feedback
    # pepper uses its own reasoning to check if the human made the best possible move, and reacts accordingly.
    # otherwise, a fine rating of the move based on the minimax scores was deemed unnecessarily complex,
    # but we can still look at the board for obvious signs, namely win threats.
    #TODO pepper should comment its own moves too.
    #     should make it so that pepper will either comment the human's move or its own, never both (don't wanna overload the "say" queue).
    optimal_responses = ["Wow, great move!", "You're so good"]    # human did optimal move
    good_responses = ["Ah, so that's your move", "Nice move"]     # human threatens win
    neutral_responses = ["I see", "Okay"]                         # everything else
    bad_responses = ["Are you sure about that?", "Mhh..."]        # human leaves Pepper win open
    if human_did_optimal_move:
        pepper_cmd.robot.say(random.choice(optimal_responses))
    elif game.player_is_threatening(pepper_player):
        pepper_cmd.robot.say(random.choice(bad_responses))
    elif game.player_is_threatening(human_player):
        pepper_cmd.robot.say(random.choice(good_responses))
    else:
        pepper_cmd.robot.say(random.choice(neutral_responses))


### end player_turn()


# In which Pepper plays ONE game
# returns the winner: Tris.X, Tris.O, Tris.DRAW
def play_game(difficulty_bias, pepper_player, human_player):

    global game

    ws_handler.send("event loading-start")
    print "initializing game...."
    pepper_cmd.robot.say("Please wait while I load the game...")
    #TODO placeholder for loading (done now?)
    game = Tris()
    agent = Agent(game, pepper_player, difficulty_bias)
    # send initial board to tablet
    ws_handler.send("event loading-complete")
    web_board=game.get_board_for_tablet()
    ws_handler.send(web_board)
    
    #START MATCH
    while not game.get_game_over_and_winner()[0]:

        if game.get_current_player() == pepper_player:
            pepper_turn(agent)
        else:
            player_turn(agent, pepper_player, human_player)
        
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
def interact(debug = False):
    pepper_cmd.robot.say("Hello, I'm Pepper. I'm here to play Tris. Wanna play?")

    #pepper_cmd.robot.say('Hello')
    #pepper_cmd.robot.say('Wanna play tris?')
    response = pepper_cmd.robot.asr(vocabulary_yesno, enableWordSpotting=True)

    if debug:
        print "[debug]: FORCING YES"
        response = "yes!!!"
    
    if "yes" in response:
        # TODO
        welcome = BehaviorWaitable("tris-behaviours-25/francesco/welcome")
        pepper_cmd.robot.say('yeah')
        welcome.wait()
        
        #SET PARAMETERS FOR PLAY
        pepper_player = Tris.X
        human_player = Tris.O
        the_bb.user_experience = None
        the_bb.user_age = None

        ws_handler.send("event interaction-begin")

        point_tablet = BehaviorWaitable("tris-behaviours-25/Alessio/point_tablet")
        pepper_cmd.robot.say("Please select a difficulty level on my tablet")
        while not the_bb.user_age or not the_bb.user_experience: 
            #if 10 seconds are passed without any proximity signal, nor any interaction, go back to the main screen
            if proxemics.is_in_zone_for_delay(10, proxemics.AWAY_ZONE):
                #TODO ? gesture or speak to go back
                print "you were away for too long, going back to main screen"
                ws_handler.send("event interaction-end")
                return
            pass


        #PROFILING
        user_age=the_bb.user_age
        user_experience=the_bb.user_experience
        #combine user age and user experience like in f1 score
        base_difficulty = 1-(2*(user_age * user_experience)/(user_age + user_experience))
        difficulty_bias = base_difficulty
        print "initial difficulty is: ", difficulty_bias

        # init score
        pepper_score = 0
        human_score = 0

        play_again = True
        
        while play_again:
            #initialize board and play
            try:
                winner = play_game(difficulty_bias, pepper_player, human_player)
            except Exception as e:
                print "exception: ", e
                ws_handler.send("event interaction-end")
                return

            print "^_^"
            print ""
            print "WINNER IS:  " + str(winner)
            print ""

            pepper_won = winner == pepper_player
            human_won = winner == human_player
    
            if pepper_won:
                pepper_score += 1
                pepper_player = Tris.O
                human_player = Tris.X

                win = BehaviorWaitable("tris-behaviours-25/Alessio/victory")
                pepper_cmd.robot.say('I win')
                win.wait()

            elif human_won:
                human_score += 1
                pepper_player = Tris.X
                human_player = Tris.O
    
                lose = BehaviorWaitable("tris-behaviours-25/Alessio/defeat")
                pepper_cmd.robot.say('Oh no')
                lose.wait()

            else:
                # no score change
                # no player change

                draw = BehaviorWaitable("tris-behaviours-25/francesco/confused")
                pepper_cmd.robot.say("Huh? It's a draw...")
                draw.wait()

            print ("score", "pepper", pepper_score, "human", human_score)
            
            # adjust difficulty for next game
            ratio = (pepper_score+2.0)/(human_score+2.0)    # gotta add at least +1 to avoid division by 0, add more to dampen the difficulty swing during the first games
            if ratio <= 1:    # human is winning, Pepper plays harder
                difficulty_bias = ratio * base_difficulty
            if ratio > 1:    # Pepper is winning and plays easier
                ratio = 1.0/ratio
                difficulty_bias = base_difficulty + ratio * (1-base_difficulty)
            print ("difficulty:", difficulty_bias)
            
            pepper_cmd.robot.say('Wanna play again?')
            response = pepper_cmd.robot.asr(vocabulary_yesno, enableWordSpotting=True)

            if debug:
                print "[debug]: FORCING NO"
                response = "no thanks"

            play_again = "yes" in response

            if play_again:
                if pepper_won:
                    pepper_cmd.robot.say("Alright, I'll go easy on you. Take CROSS.")
                elif human_won:
                    pepper_cmd.robot.say("I have to try harder... Take CIRCLE.")
                else:
                    pepper_cmd.robot.say("Very well, let's break the tie!")

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
    
    ws_handler.send("event interaction-end")

### end interact()




begin()

the_bb = Blackboard()

proxemics = ProxemicsInfo()
the_webserver_thread = WebServerThread(the_bb)
the_webserver_thread.start()

#wait for connection
print "Reminder: open browser at 127.0.0.1:8888/web/index.html"
while not the_bb.the_handler:
    pass

ws_handler = the_bb.the_handler

#DEBUG: forcing sonar to measure always the robot in the CASUAL_ZONE
proxemics.begin_forcing_zone(proxemics.CASUAL_ZONE) # TODO remove

while True:

    if proxemics.get_proximity_zone() < proxemics.AWAY_ZONE:
        ws_handler.send("event user-approached")
        interact(debug=True) #TODO remove debug flag
    time.sleep(2)


end()