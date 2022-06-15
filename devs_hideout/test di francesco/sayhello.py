import os, sys
import math

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

def deg2rad(alpha):
    return alpha * math.pi / 180.0

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

# let's also try a non-behavior
def extendHand():
    jointNames = ["RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RWristYaw"]
    angles     = [0               , 0              , 0           , deg2rad(16)]
    times      = [2.0             , 2.0            , 2.0         , 2.0        ]
    isAbsolute = True
    pepper_cmd.robot.motion_service.angleInterpolation(jointNames, angles, times, isAbsolute)
    # BLOCKING


begin()

pepper_cmd.robot.say('Hello')
pepper_cmd.robot.say('Wanna play tris?')

#establishing test vocabulary
vocabulary = ["yes", "no", "please", "hello", "goodbye", "hi, there", "go to the kitchen"]

word = pepper_cmd.robot.asr(vocabulary)

if word=="yes":
    pepper_cmd.robot.say('Yaaay')
    # trying an "animated say"
    pepper_cmd.robot.asay('I hear tris is a very good game. There are countless strategies and no two games are the same. Let us face off in this ultimate battle of wits!!')

    # trying a behavior, also w/ sound (gotta manually define it and upload to the robot. Not even the sax is there in Choregraphe.)
    # pepper_cmd.robot.beh_service.startBehavior("hri_prova/last_surprise")
    BehaviorWaitable("hri_prova/last_surprise").wait()
    # pepper_cmd.robot.animation_player_service.run("hri_prova/last_surprise")     # also BLOCKING

    pepper_cmd.robot.say('Okay, the game is over now.')
    pepper_cmd.robot.say("That was a good game. Let's shake hands!")

    # trying a non-behavior motion
    extendHand()

    # wait for handshake (or actually, hand-tapping)
    pepper_cmd.robot.startSensorMonitor()
    handTouched = False
    while not handTouched:
        p = pepper_cmd.robot.sensorvalue("righthandtouch")    # give no arg to get all sensors in a list, see pepper_cmd.py
        handTouched = p>0
    pepper_cmd.robot.stopSensorMonitor()

    # now hand has been shaken
    pepper_cmd.robot.asay('Thank you so much for playing my game!')
    pepper_cmd.robot.normalPosture()   # useful to tidy up the pose

else:
    pepper_cmd.robot.say('Awww')
    pepper_cmd.robot.asay("Then I shall punish you by doing the most unoriginal thing imaginable")
    pepper_cmd.robot.sax()

end()

