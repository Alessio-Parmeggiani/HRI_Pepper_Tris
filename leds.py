
import qi
import argparse
import sys
import pepper_cmd
from pepper_cmd import *

class Leds:
    def __init__(self):
        
        print "init leds..."
        self.session=pepper_cmd.session
        '''
        #alternative connection
        pip = "127.0.0.1"
        pport = "41763"
        self.session = qi.Session()
        try:
            self.session.connect("tcp://" + pip + ":" + str(pport))
        except RuntimeError:
            print "Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
            sys.exit(1)
        '''
        self.group_name = "FaceLeds"
        self.leds_service = self.session.service("ALLeds")
        print "Led started"
    
    def setGroup(self,name):
        self.group_name=name

    def winning(self):

        name = self.group_name
        self.leds_service.fadeRGB(name,"green",1.0)
    
    def losing(self):

        name = self.group_name
        self.leds_service.fadeRGB(name,"red",1.0)
    
    def waiting(self,duration=5,colors=['white', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan']):
        name = self.group_name
        self.leds_service.fadeListRGB(name,colors+colors[0],[i for i in xrange(0,duration,duration/len(colors))])
    
    def thinking(self,total_duration=2,rotation_speed=1):
        n_turns=int(total_duration/rotation_speed)
        #rgb code: 0x00RRGGBB
        self.leds_service.rotateEyes("0x00FF0000",rotation_speed,total_duration)

    def leds_off(self):
        name=self.group_name
        self.leds_service.off(name)

    def default(self):
        name=self.group_name
        self.leds_service.fadeRGB(name,"white",0.5)

    def neutral(self):
        name=self.group_name
        self.leds_service.fadeRGB(name,"yellow",0.5)