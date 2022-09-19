'''
    This module contains the servo implementation.
'''
import logging

from constants import INIT_LEGS, LEG_INDEX

MIN_PULSE_WIDTH = 544        # the shortest pulse sent to a servo
MAX_PULSE_WIDTH = 2400       # the longest pulse sent to a servo
DEFAULT_PULSE_WIDTH =  1500  # default pulse width when servo is attached

class Servo():
    '''
        The servo class defines a part of a leg.
    '''
    def __init__(self, index, servo_controller):
        logging.debug(f"initialize servo leg part:{index} ")
        self._index = index
        self._servo_controller = servo_controller

        if INIT_LEGS > 0:
            logging.info(f"Warning: Fixed position! Angle {INIT_LEGS}")

    def write(self, angle):
        '''
            This functions writes the actual angle values to the servo for the given index.
        '''
        if INIT_LEGS > 0:
            self._servo_controller.move(self._index, INIT_LEGS, 180)
        else:
            self._servo_controller.move(self._index, angle, 180)

    def translate(self, value, left_min, left_max, right_min, right_max):
        '''
            This function translates the value to a scaled value in the given range
        '''
        # Figure out how 'wide' each range is
        left_span = left_max - left_min
        right_span = right_max - right_min

        # Convert the left range into a 0-1 range (float)
        value_scaled = float(value - left_min) / float(left_span)

        # Convert the 0-1 range into a value in the right range.
        return right_min + (value_scaled * right_span)
