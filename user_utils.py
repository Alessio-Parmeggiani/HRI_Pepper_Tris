"""
Saving and loading the user database, and the interactions to access that.

User IDs are *strings* of 1 digit.
For each user we save: base_difficulty, pepper_score, human_score.
"""

import os, inspect
import pepper_cmd
from behavior_waitable import BehaviorWaitable
from utils import UserLeavingException, vocabulary_yesno

class Record:
    def __init__(self, user_id, base_difficulty, pepper_score, human_score):
        self.user_id = user_id
        self.base_difficulty = base_difficulty
        self.pepper_score = pepper_score
        self.human_score = human_score
    
    def get_difficulty(self):
        ratio = (self.pepper_score+2.0)/(self.human_score+2.0)    # gotta add at least +1 to avoid division by 0, add more to dampen the difficulty swing during the first games
        if ratio <= 1:    # human is winning, Pepper plays harder
            difficulty_bias = ratio * self.base_difficulty
        if ratio > 1:    # Pepper is winning and plays easier
            ratio = 1.0/ratio
            difficulty_bias = self.base_difficulty + ratio * (1-self.base_difficulty)
        return difficulty_bias
    
    def __str__(self):
        return "ID " + str(self.user_id) + " : " + str(self.base_difficulty) + " " + str(self.pepper_score) + "-" + str(self.human_score)

# for internal use
# a class named ...Class is a bit weird, but I like the instance be called simply "users"
class UsersClass:
    def __init__(self):
        self.load()
    
    def __getitem__(self, key):
        return self.the_dict[key]
    
    def __setitem__(self, key, value):
        self.the_dict[key] = value
    
    def __len__(self):
        return len(self.the_dict)
    
    def __contains__(self, item):
        return item in self.the_dict

    def save(self):
        # not the first time I do this, see webserver 
        source_path = os.path.abspath(inspect.getsourcefile(lambda:14383421))
        source_dir = os.path.split(source_path)[0]    # that would be dirpath in python3
        users_path = os.path.join(source_dir, "data", "users.txt")
        with open(users_path, "w") as f:
            for key in self.the_dict:
                record = self.the_dict[key]
                f.write(key+" "+str(record.base_difficulty)+" "+str(record.pepper_score)+" "+str(record.human_score)+"\n")

    def load(self):
        self.the_dict = dict()
        # not the first time I do this, see webserver 
        source_path = os.path.abspath(inspect.getsourcefile(lambda:14383421))
        source_dir = os.path.split(source_path)[0]    # that would be dirpath in python3
        users_path = os.path.join(source_dir, "data", "users.txt")
        with open(users_path, "r") as f:
            for line in f:
                tokens = line.split(" ")
                key = tokens[0]
                basediff = float(tokens[1])
                pepperscore = int(tokens[2])
                humanscore = int(tokens[3])
                self.the_dict[key] = Record(key, basediff, pepperscore, humanscore)

# global users object, created lazily. don't like them being created upon import.
users = None

def gen_user_id(i):
    int_id = i
    str_id = str(i)
    return str_id





def handle_new_user(the_bb, ws_handler, the_proxemics):

    pepper_cmd.robot.say("Oh, great! I always like meeting someone new! I'm Pepper. Nice to meet you!")

    the_bb.user_experience = None
    the_bb.user_age = None

    ws_handler.send("event enter-profiling")

    point_tablet = BehaviorWaitable("tris-behaviours-25/Alessio/point_tablet")
    pepper_cmd.robot.say("Please select a difficulty level on my tablet")
    while not the_bb.user_age or not the_bb.user_experience: 
        #if 10 seconds are passed without any proximity signal, nor any interaction, go back to the main screen
        if the_proxemics.is_in_zone_for_delay(10, the_proxemics.AWAY_ZONE):
            print "user went away during profiling, going back to main screen"
            raise UserLeavingException("new user profiling")


    #PROFILING
    user_age=the_bb.user_age
    user_experience=the_bb.user_experience
    #combine user age and user experience like in f1 score
    base_difficulty = 1-(2*(user_age * user_experience)/(user_age + user_experience))

    user_id = gen_user_id(len(users))
    user_record = Record(user_id, base_difficulty, 0, 0)
    users[user_id] = user_record

    return user_record


def handle_returning_user(the_bb, ws_handler, the_proxemics):

    pepper_cmd.robot.say("Welcome back then! Can you remind me your user number?")

    vocabulary_existing_ids = [key for key in users.the_dict]

    # try to get user's ID, while checking if they left every once in a while.
    # spend a LONG time on this, since if the user fails to answer
    # we'll assume they mis-responded earlier, or forgot, or w/e
    # and send them to the new user's path instead.
    for _ in range(3):
        # listen
        user_id = pepper_cmd.robot.asr(vocabulary_existing_ids, enableWordSpotting=True, timeout=10)
        # if answered, ok
        if user_id != "":
            break
        # check if left
        if the_proxemics.is_in_zone_for_delay(10, the_proxemics.AWAY_ZONE):
            print "user went away during ID checking, going back to main screen"
            raise UserLeavingException("asking user ID")

    if user_id == "":     # as I just said
        pepper_cmd.robot.say("You don't know...? Then I'll create a new profile for you")
        return handle_new_user(the_bb, ws_handler, the_proxemics)
        # and stop
    
    user_record = users[user_id]
    pepper_cmd.robot.say('Yeah, we were ' + str(user_record.pepper_score) + ' to ' + str(user_record.human_score))

    if user_record.pepper_score > user_record.human_score:
        pepper_cmd.robot.say("Here for a rematch? :)")
    elif user_record.human_score > user_record.pepper_score:
        pepper_cmd.robot.say("I'll beat you this time!")
    else:
        pepper_cmd.robot.say("Let's play again!")

    return user_record


# An entry point of this module.
# Ask if this user is a new or returning player,
# if new profile them and create a record,
# if returning fetch the record.
# Either way, return a record.
def interact_for_user_info(the_bb, ws_handler, the_proxemics):

    # lazy users
    global users
    if users == None:
        users = UsersClass()

    pepper_cmd.robot.say("Is this the first time you play with me?")
    response = pepper_cmd.robot.asr(vocabulary_yesno, enableWordSpotting=True)

    # if user didn't respond, there's the chance they left
    if response == "" and the_proxemics.is_in_zone_for_delay(10, the_proxemics.AWAY_ZONE):
        print "user went away when asked if new, going back to main screen"
        raise UserLeavingException("asked if new")

    if "no" in response:
        # RETURNING USER
        user_record = handle_returning_user(the_bb, ws_handler, the_proxemics)
    else:
        # NEW USER
        user_record = handle_new_user(the_bb, ws_handler, the_proxemics)
    
    return user_record

# Another entry point.
# Makes sure the updated record gets into the big dict, then saves everything.
def save_user(user_record):
    users[user_record.user_id] = user_record
    users.save()
