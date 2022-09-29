import os, sys
import math
import time
import random   # choice for responses

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

from behavior_waitable import BehaviorWaitable
from vow import Vow
from tris import *
from planner_tris import *
from agent_tris import *
from proxemics import *
from leds import *
from utils import UserLeavingException, vocabulary_yesno, DEBUG
from user_utils import interact_for_user_info, save_user

import threading
from webserver import go

game = None    # Blackboard needs this global, and Pepper can only play one game at a time regardless

pepper_leds=None


SIMULATION = False    # NOTE: set this depending on operation mode



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
                BehaviorWaitable("tris-behaviours-25/francesco/clicked")
                pepper_cmd.robot.asr_cancel()    # stop asr so we don't have to wait for the timeout to expire like a pesce lesso


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
    think_gestures = (
        "tris-behaviours-25/francesco/thinking",
        "tris-behaviours-25/francesco/thinking2",
        "tris-behaviours-25/francesco/thinking3",
    )
    think = BehaviorWaitable(random.choice(think_gestures), safety_proxemics=proxemics)
    think_leds = pepper_leds.thinking_parloop()
    pepper_cmd.robot.say(random.choice((
        "Thinking ...",
        "Let's see...",
        "What to do...?"
    )))
    think.wait()
    think_leds.request_stop()

    if proxemics.is_too_close():
        pepper_cmd.robot.normalPosture()    # avoid unintentional head drift when gestures are locked b/c proxemics

    pepper_move, pepper_did_optimal_move = agent.on_my_turn()
    game.move(*pepper_move)

    # pepper announces its own move. The type of message is simply dictated on
    # whether it picked the optimal move or it went for a more merciful choice.
    if pepper_did_optimal_move:
        pepper_cmd.robot.say(random.choice((
            "Then take this!",
            "Here's my move!"
        )))
    else:
        pepper_cmd.robot.say(random.choice((
            "Um, maybe here?",
            "I'll try this..."
        )))

    

### end pepper_turn()

def player_turn(agent, pepper_player, human_player):
    point_tablet = BehaviorWaitable("tris-behaviours-25/Alessio/point_tablet", safety_proxemics=proxemics)
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
    waiting_leds = pepper_leds.waiting_parloop()
    if DEBUG: print "REMINDER: What happens when the waiting leds are interrupted by the default leds? Use await_stop if necessary."

    while True:
        if proxemics.is_in_zone_for_delay(10,proxemics.AWAY_ZONE):
            #the user left, after 10 seconds the game is paused. Delay can be affected by the random delay below
            if not game_paused:
                print "user left"
                ws_handler.send("event pause-game")
                game_paused = True
                game_pause_countdown = 3 #countdown to go back to main screen
            
            if DEBUG: print "countdown: " + str(game_pause_countdown)
            if game_pause_countdown == 1:
                ws_handler.send("event pause-game-warning")
            if game_pause_countdown == 0:
                waiting_leds.request_stop()
                raise UserLeavingException("user_left_timeout")
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
                waiting_leds.request_stop()
                pepper_leds.default()
                player_move = the_bb.clicked_move
                the_bb.clicked_move = None
                break

            if response:
                waiting_leds.request_stop()
                pepper_leds.default()
                player_move = parse_move(response)
                valid = game.move(*player_move)
                if valid:
                    break
                else: # invalid move
                    gest = BehaviorWaitable("tris-behaviours-25/daniele/shake_head_gesture")
                    pepper_cmd.robot.say("You can't play there!")
                    print "invalid move"

            else: # ASR timed out
                gest = BehaviorWaitable(impatience_gestures[impatience_score], safety_proxemics=proxemics)
                pepper_cmd.robot.say(impatience_responses[impatience_score])
                
                impatience_score += 1

                if impatience_score >= len(impatience_responses):
                    impatience_score = 2    # loop the most impatient ones
    # end while True
    # i.e. human move selected correctly
        
    human_did_optimal_move = agent.on_opponent_move(player_move)

    # feedback
    # pepper uses its own reasoning to check if the human made the best possible move, and reacts accordingly.
    # otherwise, a fine rating of the move based on the minimax scores was deemed unnecessarily complex,
    # but we can still look at the board for obvious signs, namely win threats.

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

    game = Tris()
    agent = Agent(game, pepper_player, difficulty_bias)

    # send initial board to tablet
    ws_handler.send("event loading-complete")
    web_board=game.get_board_for_tablet()
    ws_handler.send(web_board)
    # reset highlighting
    ws_handler.send("highlight .........")
    
    #START MATCH
    while not game.get_game_over_and_winner()[0]:

        if game.get_current_player() == pepper_player:
            pepper_turn(agent)
        else:
            player_turn(agent, pepper_player, human_player)
        
        # update tablet
        web_board=game.get_board_for_tablet()
        ws_handler.send(web_board)
            
        if DEBUG: print game

        #check victory
        if game.get_game_over_and_winner()[0]:
            break
    #END MATCH

    
    # highlight the tris (if any) on the tablet
    hl_web_board = game.get_tris_highlights_for_tablet()
    ws_handler.send("highlight " + hl_web_board)
    
    return game.get_game_over_and_winner()[1]

### end play_game()


# This includes all the interaction with a new user
def interact():
    pepper_cmd.robot.say("Hello, I'm Pepper. I'm here to play Tic-Tac-Toe. Wanna play?")

    response = pepper_cmd.robot.asr(vocabulary_yesno, timeout=(30 if SIMULATION else 10), enableWordSpotting=True)

    if DEBUG:
        print "[debug]: FORCING YES"
        response = "yes!!!"
    
    if "yes" in response:
        welcome = BehaviorWaitable("tris-behaviours-25/francesco/welcome", safety_proxemics=proxemics)
        pepper_cmd.robot.say("Yeah, let's play!")
        welcome.wait()
        
        try:
            user_record = interact_for_user_info(the_bb, ws_handler, proxemics)
        except UserLeavingException as e:
            ws_handler.send("event interaction-end")
            return

        if user_record.user_age < 0.75: #0.5 and 0.25
            if DEBUG:
                print("[debug]: USING CHILD PROXEMICS CONFIG")
            proxemics.configuration = child_proxemics_config
        else:
            if DEBUG:
                print("[debug]: USING ADULT PROXEMICS CONFIG")
            proxemics.configuration = adult_proxemics_config

        #SET PARAMETERS FOR PLAY
        pepper_player = Tris.X
        human_player = Tris.O
        difficulty_bias = user_record.get_difficulty()
        print "difficulty is: ", difficulty_bias
        # read and write score to user_record.pepper_score and user_record.human_score


        play_again = True
        
        while play_again:
            #initialize board and play
            try:
                winner = play_game(difficulty_bias, pepper_player, human_player)
            except UserLeavingException as e:
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
                user_record.pepper_score += 1
                pepper_player = Tris.O
                human_player = Tris.X

                win = BehaviorWaitable("tris-behaviours-25/Alessio/victory", safety_proxemics=proxemics)
                pepper_cmd.robot.say('I win')
                pepper_leds.winning()
                win.wait()

            elif human_won:
                user_record.human_score += 1
                pepper_player = Tris.X
                human_player = Tris.O
    
                lose = BehaviorWaitable("tris-behaviours-25/Alessio/defeat", safety_proxemics=proxemics)
                pepper_cmd.robot.say('Oh no')
                pepper_leds.losing()
                lose.wait()

            else:
                # no score change
                # no player change

                draw = BehaviorWaitable("tris-behaviours-25/francesco/confused", safety_proxemics=proxemics)
                pepper_cmd.robot.say("Huh? It's a draw...")
                pepper_leds.neutral()
                draw.wait()

            pepper_cmd.robot.normalPosture()

            print ("score", "pepper", user_record.pepper_score, "human", user_record.human_score)
            
            # adjust difficulty for next game
            difficulty_bias = user_record.get_difficulty()
            print ("difficulty:", difficulty_bias)
            
            pepper_cmd.robot.say('Wanna play again?')
            response = pepper_cmd.robot.asr(vocabulary_yesno, timeout=(30 if SIMULATION else 10), enableWordSpotting=True)

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
        if user_record.pepper_score > user_record.human_score:
            pepper_cmd.robot.say("Okay. I won " + str(user_record.pepper_score) + " to " + str(user_record.human_score) + ". You'll do better next time!")
        elif user_record.human_score > user_record.pepper_score:
            pepper_cmd.robot.say("Okay. You won " + str(user_record.human_score) + " to " + str(user_record.pepper_score) + ". You're quite good at this!")
        else:  # draw
            pepper_cmd.robot.say("Okay. We ended up drawing at " + str(user_record.pepper_score) + " even. I had a lot of fun!")
        
        # SAVE USER
        pepper_cmd.robot.say("Your user number is... " + user_record.user_id + ". Remember it next time we play!")
        save_user(user_record)

        # final handshake if enough distance
        if not proxemics.is_too_close():
            handshake = BehaviorWaitable("tris-behaviours-25/francesco/offer_handshake")
            pepper_cmd.robot.say("We've had some good games. Let's shake hands!")
            handshake.wait()

             # wait for hand touching (with timeout)
            pepper_cmd.robot.startSensorMonitor()
            hand_touched = False
            TIMEOUT = 5    # in seconds
            wait_start_timestamp = time.clock()     # processor time in seconds. dont care about absolute value, just difference.
            while (not hand_touched) and (time.clock() - wait_start_timestamp < TIMEOUT):
                p = pepper_cmd.robot.sensorvalue("righthandtouch")    # give no arg to get all sensors in a list, see pepper_cmd.py
                hand_touched = p>0
            pepper_cmd.robot.stopSensorMonitor()
            # give time to the user to let go of the hand
            time.sleep(1)

        else:   # i.e., too close fo handshake
            pepper_cmd.robot.say("We've had some good games. See you next time!")
            hand_touched = True

        # return to normal posture
        pepper_cmd.robot.normalPosture()


        # bye bye
        if hand_touched:
            goodbye = BehaviorWaitable("tris-behaviours-25/francesco/goodbye2")
            pepper_cmd.robot.say('Come play again soon!')
            goodbye.wait()
        else:    # no respect for a probably gone user, but also don't reset silently either.
            pepper_cmd.robot.say('Aww... Resetting.')


    else:   # answered NO to "wanna play tris?"
        goodbye = BehaviorWaitable("tris-behaviours-25/francesco/goodbye2")
        pepper_cmd.robot.say('Oh, okay. Goodbye.')
        goodbye.wait()
    
    ws_handler.send("event interaction-end")

### end interact()




begin()

the_bb = Blackboard()

proxemics = ProxemicsInfo()
#proxemics configuration
adult_proxemics_config = ProxemicsClosenessConfiguration([0.5, 1.2, 2.0]) 
child_proxemics_config = ProxemicsClosenessConfiguration([1, 1.7, 2.5])

the_webserver_thread = WebServerThread(the_bb)
the_webserver_thread.start()

#wait for connection
print "Reminder: open browser at 127.0.0.1:8888/web/index.html"
while not the_bb.the_handler:
    pass

ws_handler = the_bb.the_handler

pepper_leds=Leds()
pepper_leds.default()

#DEBUG (and simulation video): forcing sonar to measure always the robot in the CASUAL_ZONE
if SIMULATION:
    proxemics.begin_forcing_zone(proxemics.CASUAL_ZONE)

while True:

    while not (proxemics.get_proximity_zone() < proxemics.AWAY_ZONE):
        pass     #wait for user to approach
    # when that happens...
    ws_handler.send("event user-approached")

    interact()

    time.sleep(2)


end()
