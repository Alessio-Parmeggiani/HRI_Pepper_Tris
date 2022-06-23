import os, sys
import math

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