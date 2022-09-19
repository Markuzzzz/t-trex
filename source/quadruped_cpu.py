'''
    This module contains the central processing class for the quadruped.
'''
import logging, time
import math
import os
from constants import x_range, z_range, z_ground, BODY_MOVE_SPEED, MOVE_SPEED, LEG_INDEX, x_offset
from constants import TURN_SPEED, z_up, LEG_MOVE_SPEED, y_start, y_step
from calculations import cartesian_to_polar, turn_x1, turn_y1, turn_x0, turn_y0
from leg import Leg
from body import Body
from action_controller import Action, ActionController
from game_controller import ControllerEvent
from exceptions import ProgramKilled, PiJuiceInitializeException
from pijuice import PiJuice 

class QuadrupedCpu():
    '''
        This class acts as the central processing unit related to the body actions.
    '''
    # class attributes
    STAY = 255

    def __init__(self) -> None:
        '''
            This function initializes the class construction.
        '''
        self._body = None
        self._action_controller = None
        self._reached = False
        self._move_speed = MOVE_SPEED
        self._custom_move_speed = MOVE_SPEED
        self._current_leg = 0
        self._is_sleeping = False
        self._game_controller = None
        self._mode_1 = False
        self._mode_2 = False 
        self._calibrate_mode = False     

        try:
            self._pijuice = PiJuice(1, 0x14) # Instantiate PiJuice interface object          
        except:
            raise PiJuiceInitializeException("PiJuice initialization failed!")

    def set_mode_1(self):
        '''
            This function sets the mode to set secondary action active
        '''        
        self._mode_1 = True

        self._action_controller.end_action() 

        logging.debug(f"mode 1: {self._mode_1}")

    def set_mode_2(self):
        '''
            This function sets the mode to set secondary action active
        '''        
        self._mode_2 = True

        self._action_controller.end_action()   

        logging.debug(f"mode 2: {self._mode_2}")

    def set_status_led(self, red, green, blue):
        '''
            This function set the led status of the PiJuice
            rgb_color - example [r,g,b] -> green = [0,200,100]
        '''
        self._pijuice.status.SetLedState('D2', [red, green, blue])
    
    def set_error_state(self):
        '''
            This function sets the error state
        '''
        self._pijuice.status.SetLedState('D2', [200, 0, 0])

    def check_value(self, value):
        '''
            This function checks the returned value of pijuice communication.
        '''  
        value = value['data'] if value['error'] == 'NO_ERROR' else value['error']
        return value

    def get_system_report(self):   
        '''
            This function returns a full system report.
        '''   
        status = self.check_value(self._pijuice.status.GetStatus())
        fault =  self.check_value(self._pijuice.status.GetFaultStatus())
        charge = self.check_value(self._pijuice.status.GetChargeLevel())
        temp = self.check_value(self._pijuice.status.GetBatteryTemperature())
        vbat = self.check_value(self._pijuice.status.GetBatteryVoltage())
        ibat = self.check_value(self._pijuice.status.GetBatteryCurrent())
        vio =  self.check_value(self._pijuice.status.GetIoVoltage())
        iio = self.check_value(self._pijuice.status.GetIoCurrent())
        pjaddr = self.check_value(self._pijuice.config.GetAddress(1))
        eepromwrprot = self.check_value(self._pijuice.config.GetIdEepromWriteProtect())
        eepromaddr = self.check_value(self._pijuice.config.GetIdEepromAddress())
        fwver = self.check_value(self._pijuice.config.GetFirmwareVersion())

        logging.info("---------- Pi-Juice Report --------------------")
        logging.info(f"Status: {status}")
        logging.info(f"Fault State: {fault}")
        logging.info(f'PiJuice I2C address = {pjaddr} (hex)')
        logging.info(f'HAT eeprom write protect = {eepromwrprot}')
        logging.info(f'HAT eeprom address = {eepromaddr} (hex)')
        logging.info(f'Firmware Version = {fwver}')
        logging.info(f'Charge ={charge} %, T = {temp} Celsius')
        logging.info(f'Vbat = {vbat} mV, Ibat = {ibat} mA, Vio = {vio} mV, Iio ={iio} mA')
        logging.info("---------- Pi-Juice Report --------------------")         
        logging.info("---------- States Report --------------------")      
        logging.info(f"Mode 1         :{self._mode_1}      Mode 2      :{self._mode_2}")             
        logging.info(f"Calibrate mode :{self._calibrate_mode}")         
        logging.info(f"Sleeping mode  :{self._is_sleeping}      Body Online :{self._body._online}")                    
        logging.info("---------- States Report --------------------")             

    def register_movements(self): # todo add status report
        '''
            This function registers all wanted action to a function in relations to
            controller events
        '''
        self._action_controller.register(Action.MODE_1,
                                         self.set_mode_1, ControllerEvent.L2_PRESSED) 
        self._action_controller.register(Action.MODE_2,
                                         self.set_mode_2, ControllerEvent.R2_PRESSED)                                                 
        self._action_controller.register(Action.SIT,
                                         self.sit, ControllerEvent.CROSS_PRESSED)
        self._action_controller.register(Action.SPEED_UP,
                                         self.speed_up, ControllerEvent.CIRCLE_PRESSED)
        self._action_controller.register(Action.SPEED_DOWN,
                                         self.speed_down, ControllerEvent.SQUARE_PRESSED)
        self._action_controller.register(Action.STAND,
                                         self.stand, ControllerEvent.TRIANGLE_PRESSED)
        self._action_controller.register(Action.FORWARD,
                                         self.step_forward, ControllerEvent.UP_PRESSED)
        self._action_controller.register(Action.BACKWARD,
                                         self.step_backward, ControllerEvent.DOWN_PRESSED)
        self._action_controller.register(Action.TURN_RIGHT,
                                         self.turn_right, ControllerEvent.RIGHT_PRESSED)
        self._action_controller.register(Action.TURN_LEFT,
                                         self.turn_left, ControllerEvent.LEFT_PRESSED)
        self._action_controller.register(Action.SHUTDOWN,
                                         self.shutdown, ControllerEvent.MENU_PRESSED)                                        
        self._action_controller.register(Action.CALIBRATE,
                                         self.calibrate, ControllerEvent.PS_SHARE)   
        self._action_controller.register(Action.REPORT,
                                         self.print_system_report, ControllerEvent.PS_HOME)
        self._action_controller.register(Action.RELEASED,
                                         self.reset_modes, ControllerEvent.RELEASED) 

    def idle(self):
        '''
            This function executes nothing at all.
        '''

    def reset_modes(self):
        '''
            This function resets the modes
        '''
        self._mode_1 = False
        self._mode_2 = False
    
        self._action_controller.end_action()

    def print_system_report(self): 
        '''
            This function prints a report or set to default stance
        '''
        if not self._action_controller.is_repeating():
            self.get_system_report()   
            self._action_controller.end_action()

    def speed_up(self):
        '''
            This function executes the action to speed up the movement.
        '''
        if self._custom_move_speed <= MOVE_SPEED*3:
            self._custom_move_speed += 0.1
        self._action_controller.end_action()
        logging.debug(f"Speed {self._custom_move_speed}")

    def speed_down(self):
        '''
            This function executes the action to slow down the movement.
        '''
        if self._custom_move_speed > 0.1:
            self._custom_move_speed -= 0.1
        else:
            self._custom_move_speed = 0.1

        self._action_controller.end_action()
        logging.debug(f"Speed {self._custom_move_speed}")

    def calibrate(self):
        if not self._action_controller.is_repeating():
            if not self._mode_1:
                if self._calibrate_mode == False:
                    self._calibrate_mode = True
                else:
                    self._calibrate_mode = False
            else:
                self._body.default_stance()

            self._action_controller.end_action()
            logging.debug(f"Calibrate mode {self._calibrate_mode}")

    def set_legs(self, leg_index, x, y, z):
        '''
           This function sets the target position of one leg endpoint x,y,x!
        '''

        leg = self._body.get_leg(leg_index)

        length_x = 0
        length_y = 0
        length_z = 0

        if x != QuadrupedCpu.STAY:
            length_x = x - leg.current_position.x
        if y != QuadrupedCpu.STAY:
            length_y = y - leg.current_position.y
        if z != QuadrupedCpu.STAY:
            length_z = z - leg.current_position.z

        # WARNING: if x,y,z equals x,y,z-current length is ZERO!!!
        length = math.sqrt(pow(length_x, 2) + pow(length_y, 2) + pow(length_z, 2))

        if length != 0: # ignore if already in position
            leg.movement.x_speed = length_x / length * self._custom_move_speed
            leg.movement.y_speed = length_y / length * self._custom_move_speed
            leg.movement.z_speed = length_z / length * self._custom_move_speed

        if x != QuadrupedCpu.STAY:
            leg.target_position.x = x
        else:
            leg.target_position.x = leg.current_position.x

        if y != QuadrupedCpu.STAY:
            leg.target_position.y = y
        else:
            leg.target_position.y = leg.current_position.y

        if z != QuadrupedCpu.STAY:
            leg.target_position.z = z
        else:
            leg.target_position.z = leg.current_position.z

    def wait_reach(self, leg_index):
        '''
            This function wait for a leg to reach its final position.
        '''
        leg = self._body.get_leg(leg_index)
        while True:
            if (leg.current_position.x == leg.target_position.x) and (leg.current_position.y == leg.target_position.y) and (leg.current_position.z == leg.target_position.z):
                #if(leg.index == LEG_INDEX): logging.info("Leg {} reached position!".format(leg.index))
                #logging.debug("Leg {} reached position!".format(leg.index))
                self._reached = True
                break

    def wait_all_reach(self):
        '''
            This function checks all leg to reach their end position.
        '''
        for leg in range(0, 4):
            self.wait_reach(leg)

        self._action_controller.update()

    def turn_right(self):
        '''
            This function executes the action to turn right sequence.
        '''
        n_step = 1 # not necessary
        while n_step > 0:
            n_step -= 1
            if self._body.left_front_leg.target_position.y == y_start:
                # leg 2 & 0 move
                self.set_legs(2, x_range, y_start, z_up)
                self.wait_all_reach()

                self.set_legs(0, turn_x0, turn_y0, z_range)
                self.set_legs(1, turn_x1, turn_y1, z_range)
                self.set_legs(2, turn_x0, turn_y0, z_up)
                self.set_legs(3, turn_x1, turn_y1, z_range)
                self.wait_all_reach()

                self.set_legs(2, turn_x0, turn_y0, z_range)
                self.wait_all_reach()

                self.set_legs(0, turn_x0, turn_y0, z_range)
                self.set_legs(1, turn_x1, turn_y1, z_range)
                self.set_legs(2, turn_x0, turn_y0, z_range)
                self.set_legs(3, turn_x1, turn_y1, z_range)
                self.wait_all_reach()

                self.set_legs(0, turn_x0, turn_y0, z_up)
                self.wait_all_reach()

                self.set_legs(0, x_range, y_start, z_up)
                self.set_legs(1, x_range, y_start, z_range)
                self.set_legs(2, x_range, y_start + y_step, z_range)
                self.set_legs(3, x_range, y_start + y_step, z_range)
                self.wait_all_reach()

                self.set_legs(0, x_range, y_start, z_range)
                self.wait_all_reach()
            else:
                # leg 1 & 3 move
                self.set_legs(1, x_range, y_start, z_up)
                self.wait_all_reach()

                self.set_legs(0, turn_x1, turn_y1, z_range)
                self.set_legs(1, turn_x0, turn_y0, z_up)
                self.set_legs(2, turn_x1, turn_y1, z_range)
                self.set_legs(3, turn_x0, turn_y0, z_range)
                self.wait_all_reach()

                self.set_legs(1, turn_x0, turn_y0, z_range)
                self.wait_all_reach()

                self.set_legs(0, turn_x1, turn_y1, z_range)
                self.set_legs(1, turn_x0, turn_y0, z_range)
                self.set_legs(2, turn_x1, turn_y1, z_range)
                self.set_legs(3, turn_x0, turn_y0, z_range)
                self.wait_all_reach()

                self.set_legs(3, turn_x0, turn_y0, z_up)
                self.wait_all_reach()

                self.set_legs(0, x_range, y_start + y_step, z_range)
                self.set_legs(1, x_range, y_start + y_step, z_range)
                self.set_legs(2, x_range, y_start, z_range)
                self.set_legs(3, x_range, y_start, z_up)
                self.wait_all_reach()

                self.set_legs(3, x_range, y_start, z_range)
                self.wait_all_reach()
        self._action_controller.end_action(True)

    def turn_left(self):
        '''
            This function executes the action to turn left sequence.
        '''
        n_step = 1 # not necessary
        while n_step > 0:
            n_step -= 1
            if self._body.left_back_leg.target_position.y == y_start:
                # leg 3&1 move
                self.set_legs(3, x_range, y_start, z_up)
                self.wait_all_reach()

                self.set_legs(0, turn_x1, turn_y1, z_range)
                self.set_legs(1, turn_x0, turn_y0, z_range)
                self.set_legs(2, turn_x1, turn_y1, z_range)
                self.set_legs(3, turn_x0, turn_y0, z_up)
                self.wait_all_reach()

                self.set_legs(3, turn_x0, turn_y0, z_range)
                self.wait_all_reach()

                self.set_legs(0, turn_x1, turn_y1, z_range)
                self.set_legs(1, turn_x0, turn_y0, z_range)
                self.set_legs(2, turn_x1, turn_y1, z_range)
                self.set_legs(3, turn_x0, turn_y0, z_range)
                self.wait_all_reach()

                self.set_legs(1, turn_x0, turn_y0, z_up)
                self.wait_all_reach()

                self.set_legs(0, x_range, y_start, z_range)
                self.set_legs(1, x_range, y_start, z_up)
                self.set_legs(2, x_range, y_start + y_step, z_range)
                self.set_legs(3, x_range, y_start + y_step, z_range)
                self.wait_all_reach()

                self.set_legs(1, x_range, y_start, z_range)
                self.wait_all_reach()
            else:
                # // leg 0 & 2 move
                self.set_legs(0, x_range, y_start, z_up)
                self.wait_all_reach()

                self.set_legs(0, turn_x0, turn_y0, z_up)
                self.set_legs(1, turn_x1, turn_y1, z_range)
                self.set_legs(2, turn_x0, turn_y0, z_range)
                self.set_legs(3, turn_x1, turn_y1, z_range)
                self.wait_all_reach()

                self.set_legs(0, turn_x0, turn_y0, z_range)
                self.wait_all_reach()

                self.set_legs(0, turn_x0, turn_y0, z_range)
                self.set_legs(1, turn_x1, turn_y1, z_range)
                self.set_legs(2, turn_x0, turn_y0, z_range)
                self.set_legs(3, turn_x1, turn_y1, z_range)
                self.wait_all_reach()

                self.set_legs(2, turn_x0, turn_y0, z_up)
                self.wait_all_reach()

                self.set_legs(0, x_range, y_start + y_step, z_range)
                self.set_legs(1, x_range, y_start + y_step, z_range)
                self.set_legs(2, x_range, y_start, z_up)
                self.set_legs(3, x_range, y_start, z_range)
                self.wait_all_reach()

                self.set_legs(2, x_range, y_start, z_range)
                self.wait_all_reach()
        self._action_controller.end_action(True)

    def sit(self):
        '''
            This function executes the action for the sit sequence.
        '''
        if not self._mode_1:
            for leg in range(0, 4):
                self.set_legs(leg, QuadrupedCpu.STAY, QuadrupedCpu.STAY, z_ground)
            self.wait_all_reach()
        else:
            self.head_down()
            self._mode_1 = False

        self._action_controller.end_action()    

    def stand(self):
        '''
            This function executes the action for the stand sequence.
        '''
        if not self._mode_1:        
            for leg in range(0, 4):
                self.set_legs(leg, QuadrupedCpu.STAY, QuadrupedCpu.STAY, z_range)
            self.wait_all_reach()
        else:
            self.head_up()
            self._mode_1 = False

        self._action_controller.end_action()

    def head_up(self):
        '''
            This function executes the action for the head up sequence.
        '''
        self.set_legs(0, QuadrupedCpu.STAY, QuadrupedCpu.STAY, self._body.get_leg(0).target_position.z - 10)
        self.set_legs(1, QuadrupedCpu.STAY, QuadrupedCpu.STAY, self._body.get_leg(1).target_position.z + 10)
        self.set_legs(2, QuadrupedCpu.STAY, QuadrupedCpu.STAY, self._body.get_leg(2).target_position.z - 10)
        self.set_legs(3, QuadrupedCpu.STAY, QuadrupedCpu.STAY, self._body.get_leg(3).target_position.z + 10)
        self.wait_all_reach()
        #self._action_controller.end_action()

    def head_down(self):
        '''
            This function executes the action for the head down sequence.
        '''
        self.set_legs(0, QuadrupedCpu.STAY, QuadrupedCpu.STAY, self._body.get_leg(0).target_position.z + 10)
        self.set_legs(1, QuadrupedCpu.STAY, QuadrupedCpu.STAY, self._body.get_leg(1).target_position.z - 10)
        self.set_legs(2, QuadrupedCpu.STAY, QuadrupedCpu.STAY, self._body.get_leg(2).target_position.z + 10)
        self.set_legs(3, QuadrupedCpu.STAY, QuadrupedCpu.STAY, self._body.get_leg(3).target_position.z - 10)
        self.wait_all_reach()
        #self._action_controller.end_action()

    def step_forward(self):
        '''
            This function executes the action for the forward sequence.
        '''
       # self._fstep = 5
        self._move_speed = LEG_MOVE_SPEED
        #while self._fstep > 0:
            #self._fstep -= 1
        if self._body.left_front_leg.target_position.y == y_start:
            # // leg 2 & 1 move
            self.set_legs(2, x_range + x_offset, y_start, z_up)
            self.wait_all_reach()
            self.set_legs(2, x_range + x_offset, y_start + 2 * y_step, z_up)
            self.wait_all_reach()
            self.set_legs(2, x_range + x_offset, y_start + 2 * y_step, z_range)
            self.wait_all_reach()

            self._move_speed = BODY_MOVE_SPEED
            self.set_legs(0, x_range + x_offset, y_start, z_range)
            self.set_legs(1, x_range + x_offset, y_start + 2 * y_step, z_range)
            self.set_legs(2, x_range - x_offset, y_start + y_step, z_range)
            self.set_legs(3, x_range - x_offset, y_start + y_step, z_range)
            self.wait_all_reach()

            self._move_speed = LEG_MOVE_SPEED
            self.set_legs(1, x_range + x_offset, y_start + 2 * y_step, z_up)
            self.wait_all_reach()
            self.set_legs(1, x_range + x_offset, y_start, z_up)
            self.wait_all_reach()
            self.set_legs(1, x_range + x_offset, y_start, z_range)
            self.wait_all_reach()
        else:
            # // leg 0 & 3 move
            self.set_legs(0, x_range + x_offset, y_start, z_up)
            self.wait_all_reach()
            self.set_legs(0, x_range + x_offset, y_start + 2 * y_step, z_up)
            self.wait_all_reach()
            self.set_legs(0, x_range + x_offset, y_start + 2 * y_step, z_range)
            self.wait_all_reach()

            self._move_speed = BODY_MOVE_SPEED
            self.set_legs(0, x_range - x_offset, y_start + y_step, z_range)
            self.set_legs(1, x_range - x_offset, y_start + y_step, z_range)
            self.set_legs(2, x_range + x_offset, y_start, z_range)
            self.set_legs(3, x_range + x_offset, y_start + 2 * y_step, z_range)
            self.wait_all_reach()

            self._move_speed = LEG_MOVE_SPEED

            self.set_legs(3, x_range + x_offset, y_start + 2 * y_step, z_up)
            self.wait_all_reach()
            self.set_legs(3, x_range + x_offset, y_start, z_up)
            self.wait_all_reach()
            self.set_legs(3, x_range + x_offset, y_start, z_range)
            self.wait_all_reach()
        
        self._action_controller.end_action(True)

    def step_backward(self):
        '''
            This function executes the action for the backward sequence.
        '''
        #step = 5
        self._move_speed = LEG_MOVE_SPEED
        #while step > 0:
        #    step -= 1
        if self._body.left_back_leg.target_position.y == y_start:
            # // leg 3 & 0 move
            self.set_legs(3, x_range + x_offset, y_start, z_up)
            self.wait_all_reach()
            self.set_legs(3, x_range + x_offset, y_start + 2 * y_step, z_up)
            self.wait_all_reach()
            self.set_legs(3, x_range + x_offset, y_start + 2 * y_step, z_range)
            self.wait_all_reach()

            self._move_speed = BODY_MOVE_SPEED
            self.set_legs(0, x_range + x_offset, y_start + 2 * y_step, z_range)
            self.set_legs(1, x_range + x_offset, y_start, z_range)
            self.set_legs(2, x_range - x_offset, y_start + y_step, z_range)
            self.set_legs(3, x_range - x_offset, y_start + y_step, z_range)
            self.wait_all_reach()

            self._move_speed = LEG_MOVE_SPEED
            self.set_legs(0, x_range + x_offset, y_start + 2 * y_step, z_up)
            self.wait_all_reach()
            self.set_legs(0, x_range + x_offset, y_start, z_up)
            self.wait_all_reach()
            self.set_legs(0, x_range + x_offset, y_start, z_range)
            self.wait_all_reach()
        else:
            # // leg 1 & 2 move
            self.set_legs(1, x_range + x_offset, y_start, z_up)
            self.wait_all_reach()
            self.set_legs(1, x_range + x_offset, y_start + 2 * y_step, z_up)
            self.wait_all_reach()
            self.set_legs(1, x_range + x_offset, y_start + 2 * y_step, z_range)
            self.wait_all_reach()

            self._move_speed = BODY_MOVE_SPEED
            self.set_legs(0, x_range - x_offset, y_start + y_step, z_range)
            self.set_legs(1, x_range - x_offset, y_start + y_step, z_range)
            self.set_legs(2, x_range + x_offset, y_start + 2 * y_step, z_range)
            self.set_legs(3, x_range + x_offset, y_start, z_range)
            self.wait_all_reach()

            self._move_speed = LEG_MOVE_SPEED

            self.set_legs(2, x_range + x_offset, y_start + 2 * y_step, z_up)
            self.wait_all_reach()
            self.set_legs(2, x_range + x_offset, y_start, z_up)
            self.wait_all_reach()
            self.set_legs(2, x_range + x_offset, y_start, z_range)
            self.wait_all_reach()

        self._action_controller.end_action(True)

    def initialize(self, action_controller:ActionController, game_controller, is_stubbed):
        '''
            This function additionally initializes this class.
        '''
        self._body = Body(is_stubbed)
        self._action_controller = action_controller
        self.register_movements()
        self._reached = False
        self._game_controller = game_controller

        if self._body._online and not self._calibrate_mode:
            self._game_controller.rumble()

    def sleep(self):
        '''
            This function initiates the action for the sleep sequence.
        '''
        if self._body is not None:
            self._body.sleep_mode()
            self._is_sleeping = True

    def shutdown(self):
        '''
            This function executes the shutdown sequence.
        '''
        if self._mode_1 and self._mode_2:
            logging.info("Hard shutdown initiated...")
            os.system("sudo shutdown -h now")
        else:
            logging.info("Soft shutdown initiated...")

        raise ProgramKilled

    def release(self):
        '''
            This function releases resources for the shutdown sequence.
        '''
        self.sleep()
        
        if self._game_controller is not None:
            self._game_controller.disconnect()

        if self._action_controller is not None:
            self._action_controller.end_action()

    def awake(self):
        '''
            This function executes the wake up sequence.
        '''
        self._body.wake_up_mode()
        self._is_sleeping = False

        if self._game_controller is not None:
            self._game_controller.rumble()

    def run(self):
        '''
            This function starts the event loop.
        '''
        self._action_controller.execute()

    def servo_service(self):
        '''
            This function is used to validate the x,y,z leg positions and update the legs. This function should be called
            in a steady (interrupt like) interval with high priority. Returns false if in sleeping state.
        '''
        #logging.info(f"update servo positions")

        if self._current_leg == self._body.right_front_leg.index:
            self.validate(self._body.right_front_leg)
        elif self._current_leg == self._body.right_back_leg.index:
            self.validate(self._body.right_back_leg)
        elif self._current_leg == self._body.left_front_leg.index:
            self.validate(self._body.left_front_leg)
        elif self._current_leg == self._body.left_back_leg.index:
            self.validate(self._body.left_back_leg)

        if self._current_leg < 4:
            self._current_leg += 1
        else:
            self._current_leg = 0

        return not self._is_sleeping


    def validate(self, leg: Leg): # todo only validate, create new servo write
        '''
            This function checks whether the position x,y,z is reached.
        '''
        if abs(leg.current_position.x - leg.target_position.x) >= abs(leg.movement.x_speed):
            leg.current_position.x = leg.current_position.x + leg.movement.x_speed
            #logging.debug("Target X leg: {} current {}".format(leg.index, leg.current_position.x))
        else:
            leg.current_position.x = leg.target_position.x
            #if(leg.index == LEG_INDEX): logging.debug("Target X leg: {} reached: {}".format(leg.index, leg.target_position.x))

        if abs(leg.current_position.y - leg.target_position.y) >= abs(leg.movement.y_speed):
            leg.current_position.y = leg.current_position.y + leg.movement.y_speed
            #logging.debug("Target Y leg: {} current {}".format(leg.index, leg.current_position.y))
        else:
            leg.current_position.y = leg.target_position.y
            #if(leg.index == LEG_INDEX): logging.debug("Target Y leg: {} reached: {}".format(leg.index, leg.target_position.y))

        if abs(leg.current_position.z - leg.target_position.z) >= abs(leg.movement.z_speed):
            leg.current_position.z = leg.current_position.z + leg.movement.z_speed
            #logging.debug("Target Z leg: {} current {}".format(leg.index, leg.current_position.z))
        else:
            leg.current_position.z = leg.target_position.z
            #if(leg.index == LEG_INDEX): logging.debug("Target Z leg: {} reached: {}".format(leg.index, leg.target_position.z))

        if self._calibrate_mode:
            alpha, beta, gamma = cartesian_to_polar(100, 80, 28)
        else:
            alpha, beta, gamma = cartesian_to_polar(leg.current_position.x, leg.current_position.y, leg.current_position.z)
        
        self._body.get_leg(leg.index).set(alpha, beta, gamma)

        
