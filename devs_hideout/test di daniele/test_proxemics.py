import os, sys

sys.path.append(os.environ["PEPPER_TOOLS_HOME"] + '/cmd_server')
root_lib = os.path.abspath(os.path.join(__file__ ,"../../../"))
sys.path.append(root_lib)
import time
import numpy as np
import pepper_cmd
from pepper_cmd import *
from proxemics import *

begin()

robot = pepper_cmd.robot

proxemics = ProxemicsInfo()

while True:
    if proxemics.did_someone_enter_front_proximity():
        print("someone entered proximity")
        robot.asay("Hello")
        print("front value: " + str(proxemics.frontValue()))

    if proxemics.did_someone_exit_front_proximity():
        print("someone exited proximity")
        robot.asay("Goodbye")
        print("front value: " + str(proxemics.frontValue()))

    time.sleep(2)

#robot.asr(["ciao"], False)

#robot.normalPosture()
#print(robot.getState())
robot.say("ciaone")
end()