#! /usr/bin/env python
# -*- encoding: UTF-8 -*-
#https://docs.google.com/presentation/d/1hFN2jngwD34IRCvwWYWGVWlHjiY3-_Z9iwkRc12ItR4/edit#slide=id.p
"""Example: Use fade Method"""

import qi
import argparse
import sys

def LED_winning(service):
    #leds_service.randomEyes(duration) #può essere carino
    name = 'FaceLeds'
    leds_service.fadeRGB(name,"green",5.0)

def LED_losing(service):
    name = 'FaceLeds'
    leds_service.fadeRGB(name,"red",5.0)

def LED_waiting(service,color):
    name = 'FaceLeds'
    leds_service.fadeRGB(name,color,0.5)

def LED_thinking(service):
    n_turns=4
    timeForRotation=1.0
    total_duration=n_turns*timeForRotation
    #rgb code: 0x00RRGGBB
    leds_service.rotateEyes("0x00FF0000",timeForRotation,total_duration)




#http://doc.aldebaran.com/2-5/naoqi/sensors/alleds-api.html#ALLedsProxy::on__ssCR
def main(session):
    """
    This example uses the fade method.
    """
    
    # Get the service ALLeds.
    tts_service = session.service("ALTextToSpeech")
    tts_service.setLanguage("English")
    #tts_service.setParameter("speed", 90)
    tts_service.say("Turning on ear led")
    
    rp_service = session.service("ALRobotPosture")
    posture = "Stand"
    speed = 0.7
    rp_service.goToPosture(posture,speed)

    print("using leds")
    leds_service = session.service("ALLeds")

    # Example showing how to fade the ears group to mid-intensity
    
    #thinking
    #LED_thinking(service)

    #winning
    #LED_winning(service)

    #losing
    #LED_losing(service)

    '''
    colors=[“white”, “red”, “green”, “blue”, “yellow”, “magenta”, “cyan”]
    #waiting
    color_idx=0
    while not humanMove:
        if color_idx>lenn(colors): colors_idx=0
        LED_waiting(service,colors[color_idx])
        color_idx+=1
    '''

    #print("available leds:",leds_service.listLEDs())
    #print("available groups:",leds_service.listGroups())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'")
    parser.add_argument("--port", type=int, default=41763,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    url="tcp://" + args.ip + ":" + str(args.port)
    try:
        app = qi.Application(["App", "--qi-url=" + url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    #main(session)
    
    
    app.start() # non blocking
    session = app.session
    main(session)
    app.run() # blocking

