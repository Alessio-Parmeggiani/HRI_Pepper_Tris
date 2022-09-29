import os, sys
import math

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

class BehaviorWaitable:
    def __init__(self, behaviorName, safety_proxemics = None):
        self.theBehaviorName = behaviorName
        self.finished = False
        self.listenerID = pepper_cmd.robot.beh_service.behaviorStopped.connect(self.onstop)

        # safety check: some gestures cannot be performed if the user is too close
        if safety_proxemics is not None:
            if safety_proxemics.is_too_close():
                self.finished = True
                return
        # if either condition fails, continue

        try:
            pepper_cmd.robot.beh_service.startBehavior(self.theBehaviorName)
            # NON-BLOCKING (which is why I made this simple waitable)
        except RuntimeError:   # behavior already running
            self.finished = True
        except Exception:
            print "Unknown error in BehaviorWaitable"
            self.finished = True
    
    def onstop(self, behaviorName):
        if self.theBehaviorName == behaviorName:
            self.finished = True
            pepper_cmd.robot.beh_service.behaviorStopped.disconnect(self.listenerID)
    
    def wait(self):
        while not self.finished:
            pass