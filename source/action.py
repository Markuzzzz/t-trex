'''
    This module holds the unique actions enumerations.
'''
from enum import Enum, unique

@unique
class Action(Enum):
    '''
        This class holds the unique actions enumerations .
    '''
    FORWARD = 1
    BACKWARD = 2
    TURN_LEFT = 3
    TURN_RIGHT = 4
    SIT = 5
    STAND = 6
    WAVE = 7
    DANCE = 8
    SHUTDOWN = 9
    MODE_1 = 10
    MODE_2 = 11
    SPEED_UP = 12
    SPEED_DOWN = 13
    RELEASED = 14
    REPORT = 15
    CALIBRATE = 16
