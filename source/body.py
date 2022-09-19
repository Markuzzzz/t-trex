'''
    This module contains the body class and its parts.
'''
import logging
from leg import Leg
from exceptions import ServoControllerInitializeException
from calculations import cartesian_to_polar
from constants import z_ground

class Body():
    '''
        This class describes the body and its parts like legs.
    '''
    x_default = 62
    y_default = x_default
    z_default = z_ground

    def __init__(self, is_stubbed):
        '''
            This function initializes this class.
        '''
        self._is_stubbed = is_stubbed
        self._online = False
        self.initialize()
        self.default_stance()
        self.calculate_error()

    def calculate_error(self):
        '''
            This function calculates and sets the error per leg.
        '''
        alpha_expected, beta_expected, gamma_expected = cartesian_to_polar(100, 80, 28)

        # leg 1
        alpha_measured, beta_measured, gamma_measured = cartesian_to_polar(110,70,30)
        self.right_front_leg.set_error(alpha_expected - alpha_measured, beta_expected - beta_measured, gamma_expected - gamma_measured)
        
        # leg 2
        alpha_measured, beta_measured, gamma_measured = cartesian_to_polar(105,65,30)
        self.right_back_leg.set_error(alpha_expected - alpha_measured, beta_expected - beta_measured, gamma_expected - gamma_measured)
    
        # leg 3
        alpha_measured, beta_measured, gamma_measured = cartesian_to_polar(90,80,50)
        self.left_front_leg.set_error(alpha_expected - alpha_measured, beta_expected - beta_measured, gamma_expected - gamma_measured)

        # leg 4
        alpha_measured, beta_measured, gamma_measured = cartesian_to_polar(110,60,30)
        self.left_back_leg.set_error(alpha_expected - alpha_measured, beta_expected - beta_measured, gamma_expected - gamma_measured)        

    def default_stance(self):
        '''
            This function initializes the body in a default stance.
        '''
        self.right_front_leg = Leg(0, self._servo_controller, Body.x_default, Body.y_default, Body.z_default)
        self.right_back_leg = Leg(1, self._servo_controller, Body.x_default, Body.y_default, Body.z_default)
        self.left_front_leg = Leg(2, self._servo_controller, Body.x_default, Body.y_default, Body.z_default)
        self.left_back_leg = Leg(3, self._servo_controller, Body.x_default, Body.y_default, Body.z_default)

    def initialize(self):
        '''
            This function initializes additional the servo controller.
        '''
        try:
            if not self._is_stubbed:
                from servo_pi import ServoController # pylint: disable=import-outside-toplevel

                # create an instance of the servo class on I2C address 0x40
                self._servo_controller = ServoController(0x40)
                self._online = True
            else:
                from servo_stub_controller import ServoStubController # pylint: disable=import-outside-toplevel
                # create stub of the servo class for testing purposes
                self._servo_controller = ServoStubController(0x40)

            # set the servo minimum and maximum limits in milliseconds
            # the limits for a servo are typically between 1ms and 2ms.
            self._servo_controller.set_low_limit(0.8)
            self._servo_controller.set_high_limit(2.3)

            # Enable the outputs
            self._servo_controller.output_enable()
        except Exception as e:
            self._servo_controller = None
            raise ServoControllerInitializeException("Servo Controller cannot be initialized!")

    def sleep_mode(self):
        '''
            This function sets the sleep mode of the servo controller.
        '''
        self._servo_controller.output_disable()
        self._servo_controller.sleep()
        logging.info("ServoController sleeping!")

    def wake_up_mode(self):
        '''
            This function sets the wake mode of the servo controller.
        '''
        self._servo_controller.output_enable()
        self._servo_controller.wake()
        logging.info("ServoController awake!")

    def get_leg(self, index) -> Leg:
        '''
            This function returns the leg based on the index.
        '''
        if index == 0:
            return self.right_front_leg
        if index == 1:
            return self.right_back_leg
        if index == 2:
            return self.left_front_leg
        if index == 3:
            return self.left_back_leg
        return None
            