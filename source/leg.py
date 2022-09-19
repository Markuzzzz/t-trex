'''
    This module contains all the leg related stuff.
'''
from movement import Movement
from position import Position
from servo import Servo
from constants import MOVE_SPEED

class Leg():
    '''
        This class describes the leg part. COXA/FEMUR/TIBIA plus LEG INDEX gives servo identification!

        Leg0 (Right_Front)    from inner right to outer left: coxa (servo  3), femur (servo  1) and tibia (servo 2)
        Leg1 (Right_Back)     from inner right to outer left: coxa (servo  6), femur (servo  4) and tibia (servo 5)
        Leg2 (Left_Front)     from inner left to outer right: coxa (servo  9), femur (servo  7) and tibia (servo 8)
        Leg3 (Left_Back)      from inner left to outer right: coxa (servo 12), femur (servo 10) and tibia (servo 11)
    '''
    COXA = 3
    FEMUR = 1
    TIBIA = 2

    @property
    def index(self):
        '''
            This property returns the index of the leg.
        '''
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    # initialize leg endpoint x,y,z
    def __init__(self, index, servo_controller, x, y, z):
        '''
            This function initializes this class.
        '''
        self.index = index

        # initialize servo for the leg parts
        self._servo_coxa = Servo(Leg.COXA + (self._index*3), servo_controller)
        self._servo_femur = Servo(Leg.FEMUR + (self._index*3), servo_controller)
        self._servo_tibia = Servo(Leg.TIBIA + (self._index*3), servo_controller)

        # set defaults
        self.current_position = Position(x, y, z)
        self.target_position = Position(62, 62, -28)
        self.movement = Movement(MOVE_SPEED, MOVE_SPEED, MOVE_SPEED)

        self.alpha_error = 0
        self.beta_error = 0
        self.gamma_error = 0

    def set_error(self, alpha_error, beta_error, gamma_error):
        self.alpha_error = alpha_error
        self.beta_error = beta_error
        self.gamma_error = gamma_error

    def polar_to_servo(self, alpha, beta, gamma):
        '''
            This function returns the angle values with respect to the leg position on the body.
        '''
        alpha += self.alpha_error
        beta += self.beta_error
        gamma += self.gamma_error

        if self._index == 0:
            alpha = 90 - alpha
            gamma += 90
        if self._index == 1:
            alpha += 90
            beta = 180 - beta
            gamma = 90 - gamma
        if self._index == 2:
            alpha += 90
            beta = 180 - beta
            gamma = 90 - gamma
        if self._index == 3:
            alpha = 90 - alpha
            gamma += 90

        return alpha, beta, gamma

    def set(self, alpha, beta, gamma):
        '''
            This function writes the actual angle data to the appropiate servo.
        '''
        #if(self._index == 0): logging.debug(f"leg index {self.index} Alpha: {alpha} Beta: {beta} Gamma: {gamma}")

        alpha_servo, beta_servo, gamma_servo = self.polar_to_servo(alpha, beta, gamma)

        self._servo_coxa.write(gamma_servo)
        self._servo_femur.write(alpha_servo)
        self._servo_tibia.write(beta_servo)
