
import qi
import argparse
import sys
import pepper_cmd
import threading

# does the rotateEyes potentially infinitely, performing one turn at a time,
# until it is requested to stop, then it will terminate at the end of the current cycle.
class _ThinkingStoppable(threading.Thread):
    def __init__(self, leds_service, rotation_period):
        threading.Thread.__init__(self)
        self.leds_service = leds_service
        self.rotation_period = rotation_period
        self.stop_flag = False
    
    def run(self):
        print "THINK LED START"
        while not self.stop_flag:
            self.leds_service.rotateEyes(0x00FF0000, self.rotation_period, self.rotation_period)
        print "THINK LED END"
    
    def request_stop(self):
        self.stop_flag = True
    
    def await_stop(self):
        self.request_stop()
        self.join()

# does a reimplementation of fadeListRGB potentially infinitely, performing one color at a time,
# until it is requested to stop, then it will terminate at the end of the current fade.
# Colrs must be either names or hex code (0x00RRGGBB). Mixed sequences might be allowed.
# Unlike fadeListRGB, all fades must have the same duration, for simplicity.
# Not that we wanted to do otherwise.
class _WaitingStoppable(threading.Thread):
    def __init__(self, leds_service, leds_name, colors, fade_time):
        threading.Thread.__init__(self)
        self.leds_service = leds_service
        self.leds_name = leds_name
        self.colors = colors
        self.fade_time = fade_time
        self.i = 0
        self.stop_flag = False
    
    def run(self):
        print "WAIT LED START"
        while not self.stop_flag:
            self.leds_service.fadeRGB(
                self.leds_name,
                self.colors[self.i],
                self.fade_time
            )
            self.i = (self.i + 1) % len(self.colors)
        print "WAIT LED END"
    
    def request_stop(self):
        self.stop_flag = True
    
    def await_stop(self):
        self.request_stop()
        self.join()

class Leds:
    def __init__(self):
        
        print "init leds..."
        self.session=pepper_cmd.robot.session
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
    
    def waiting(self, duration=5, colors=['white', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan']):
        print "LED START"
        name = self.group_name
        duration = int(duration)
        colors.append(colors[0])
        self.leds_service.fadeListRGB(name, colors, [duration * (i*1.0)/len(colors) for i in xrange(0, len(colors))])
        print "LED END"
    
    def waiting_parloop(self, fade_time=1, colors=['white', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan']):
        # "parallel loop"
        leds_thread = _WaitingStoppable(self.leds_service, self.group_name, colors, fade_time)
        leds_thread.start()
        return leds_thread
    
    def thinking(self, total_duration=2, rotation_speed=1):
        n_turns=int(total_duration/rotation_speed)
        #rgb code: 0x00RRGGBB
        self.leds_service.rotateEyes(0x00FF0000, rotation_speed, total_duration)
    
    def thinking_parloop(self, rotation_period=1):
        # "parallel loop"
        leds_thread = _ThinkingStoppable(self.leds_service, rotation_period)
        leds_thread.start()
        return leds_thread

    def leds_off(self):
        name=self.group_name
        self.leds_service.off(name)

    def default(self):
        name=self.group_name
        self.leds_service.fadeRGB(name,"white",0.5)

    def neutral(self):
        name=self.group_name
        self.leds_service.fadeRGB(name,"yellow",0.5)