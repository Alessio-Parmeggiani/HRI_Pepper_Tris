import os, sys
import inspect    # getsourcefile
import math
import random

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

class BehaviorWaitable:
    def __init__(self, behaviorName):
        self.theBehaviorName = behaviorName
        self.finished = False
        self.listenerID = pepper_cmd.robot.beh_service.behaviorStopped.connect(self.onstop)
        pepper_cmd.robot.beh_service.startBehavior(self.theBehaviorName)
        # NON-BLOCKING (which is why I made this simple waitable)
    
    def onstop(self, behaviorName):
        if self.theBehaviorName == behaviorName:
            self.finished = True
            pepper_cmd.robot.beh_service.behaviorStopped.disconnect(self.listenerID)
    
    def wait(self):
        while not self.finished:
            pass


# ------------------------------------------------------------------------------

class Record:
    def __init__(self, user_id, base_difficulty, pepper_score, human_score):
        self.user_id = user_id
        self.base_difficulty = base_difficulty
        self.pepper_score = pepper_score
        self.human_score = human_score
    
    def __str__(self):
        return "ID " + str(self.user_id) + " : " + str(self.base_difficulty) + " " + str(self.pepper_score) + "-" + str(self.human_score)

def gen_user_id(i):
    int_id = (0 + i*1111) % 10000
    # this format specification should do the "force a 4-digit number by adding zeroes to the left if necessary" trick.
    # in the following order, this says:
    # - fill with zeroes
    # - align the number to the right
    # - I want a 4-character string
    # - format as a decimal number (not another base, not a floating point)
    str_id = "{:0>4d}".format(int_id)
    return str_id

# take "STRING", return "S-T-R-I-N-G".
# (hopefully, real test pending) useful to make Pepper spell the user ID,
# rather than saying it as a number.
def spell(user_id):
    s = ""
    for c in user_id:
        s += c + "-"
    return s[:-1]   # delete the final "-"

def save_users(diz):
    # not the first time I do this 
    source_path = os.path.abspath(inspect.getsourcefile(lambda:14383421))
    source_dir = os.path.split(source_path)[0]    # that would be dirpath in python3
    users_path = os.path.join(source_dir, "data", "users.txt")
    with open(users_path, "w") as f:
        for key in diz:
            record = diz[key]
            f.write(key+" "+str(record.base_difficulty)+" "+str(record.pepper_score)+" "+str(record.human_score)+"\n")

def load_users():
    diz = dict()
    # not the first time I do this 
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
            diz[key] = Record(key, basediff, pepperscore, humanscore)
    return diz


begin()

users = load_users()
print(users)

pepper_cmd.robot.say('Hello')
pepper_cmd.robot.say('Wanna play tris?')
pepper_cmd.robot.say('Ah, who am I kidding? Of course you wanna!')

pepper_cmd.robot.say('But, say... You look familiar. Do I know you?')
vocabulary = ["yes", "no", "please", "hello", "goodbye", "hi, there", "go to the kitchen"]
word = pepper_cmd.robot.asr(vocabulary)

if word=="yes":
    pepper_cmd.robot.say('Ah, I knew it! My tablet is malfunctioning today, can you type your user ID in the terminal please?')
    while True:
        user_id = raw_input("Insert ID: ")
        if user_id in users:
            user_record = users[user_id]
            pepper_cmd.robot.say('Yeah, we were ' + str(user_record.pepper_score) + ' to ' + str(user_record.human_score))
            break
        elif user_id == "":
            pepper_cmd.robot.say('Oh, youd like to go back? Too bad, this is just a test and I dont have that function. Maybe in the real version.')
        else:
            pepper_cmd.robot.say('Ummm, I dont know that ID. Try again maybe?')
else:
    pepper_cmd.robot.say("I always like meeting someone new! I'm Pepper.")
    user_id = gen_user_id(len(users))
    user_record = Record(user_id, 0.5, 0, 0)
    users[user_id] = user_record

pepper_score = user_record.pepper_score
human_score = user_record.human_score

pepper_cmd.robot.say('Lets get to it right away!')

BehaviorWaitable("hri_prova/last_surprise").wait()

if random.random() < 0.5:
    pepper_score += 1
else:
    human_score += 1

pepper_cmd.robot.say('Okay, the game is over now.')
pepper_cmd.robot.say('I dont feel like playing another.')

pepper_cmd.robot.say("Your user ID is " + spell(user_id) + ". Remember it if you come again!")

user_record.pepper_score = pepper_score
user_record.human_score = human_score
users[user_id] = user_record
save_users(users)

end()

