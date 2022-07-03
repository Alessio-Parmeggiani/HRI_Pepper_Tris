#for further technical info
#http://doc.aldebaran.com/2-4/family/pepper_technical/sonar_pep.html

import os, sys
sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import robot

class ProxemicsInfo(object):
    '''
        This class uses Sonar front and back sensors in order to measure the area of proximity.
        Creating the class instance will start the sensors.
    '''
    #BASED ON proximity areas
    # https://classroom.google.com/c/NDU5NDAzMTA3MDcw/m/NDU5NDAzMTA3MTEw/details
    INTIMATE_ZONE = 0
    CASUAL_ZONE = 1
    SOCIO_CONSULTIVE_ZONE = 2
    AWAY_ZONE = 3

    def __init__(self, outliar_values = [0.0, None]):
        '''
            initialize the sensors.
            outliar_values is a list of values that will be ignored (useful for DEBUG).
        '''
        super(ProxemicsInfo, self).__init__()
        #start monitoring sensors
        pepper_cmd.robot.startSensorMonitor()
        #initialize measurements to long distances
        self.last_front_value = 5
        self.last_back_value = 5
        #initialize outliar values
        self.outliar_values = outliar_values

    def __del__(self):
        self.stop_sensors()

    def stop_sensors(self):
        '''
            stops the sensors updating.
        '''
        if pepper_cmd.robot.sensorThread != None:
            pepper_cmd.robot.stopSensorMonitor()
        

    ## GET CURRENT VALUES
    def frontValue(self):
        '''get current useful value from front sensor'''
        val = pepper_cmd.robot.sonar[0]
        return val if val not in self.outliar_values else self.last_front_value #filter out outliars measurements

    def backValue(self):
        '''get current useful value from back sensor'''
        val = pepper_cmd.robot.sonar[1]
        return val if val not in self.outliar_values else self.last_back_value #filter out outliars measurements

    ## GET DISTANCE IN TERMS OF AREA OF PROXIMITY
    def zoneFromDistance(self, distance):
        '''
            return the zone of proximity from a distance. 
            The zone is a number between 0 and 3, where 0 is the closest (< 0.5), and 3 is the furthest(>2).
        '''
        if distance < 0.5:
            return self.INTIMATE_ZONE
        elif distance < 1.2:
            return  self.CASUAL_ZONE
        elif distance < 2.0:
            return  self.SOCIO_CONSULTIVE_ZONE
        else:
            return self.AWAY_ZONE
    
    def update_measurements(self):
        '''update stored measurements'''
        self.last_front_value = self.frontValue()
        self.last_back_value = self.backValue()

    #EXTERNAL FUNCTIONS - every call may also updates the stored measurements
    def get_proximity_zone(self):
        '''returns the area of proximity from the front sensor.
            The zone is a number between 0 and 3, where 0 is the closest (< 0.5), and 3 is the furthest(>2).
            Calling this function updates measurements.
        '''
        self.update_measurements()
        return self.zoneFromDistance(self.last_front_value)

    def did_change_front_zone(self):
        ''' 
            returns True if the area of proximity has changed since the last update of measurements.
        '''
        return self.zoneFromDistance(self.frontValue()) != self.zoneFromDistance(self.last_front_value)

    def did_someone_enter_front_proximity(self):
        '''
            returns True if someone has come in (any zone < AWAY_ZONE) since the last update of measurements.
            Calling this function updates measurements.
        '''
        return  self.zoneFromDistance(self.last_front_value) == self.AWAY_ZONE and self.get_proximity_zone() < self.AWAY_ZONE  

    def did_someone_exit_front_proximity(self):
        '''
            returns True if someone has left (new measurement > self.AWAY_ZONE) since the last update of measurements.
            Calling this function updates measurements.
        '''
        return  self.zoneFromDistance(self.last_front_value) < self.AWAY_ZONE and self.get_proximity_zone() >= self.AWAY_ZONE
    