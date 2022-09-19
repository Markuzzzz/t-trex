'''
    This module implements the EVDEV based game controller.

    The EVDEV package provides bindings to the generic input event interface in Linux. The evdev interface
    serves the purpose of passing events generated in the kernel directly to userspace through character
    devices that are typically located in /dev/input/.

    Documentation: https://python-evdev.readthedocs.io/en/stable/index.html

'''
import logging
import time
from enum import Enum, unique
from evdev import InputDevice, categorize, ecodes, ff # pylint: disable=import-error, unused-import
from exceptions import NoJoystickConnectedException, JoystickDisconnectedException

@unique
class ControllerEvent(Enum):
    '''
        This class defines the unique Controller Events.
    '''
    LEFT_PRESSED = 0
    RIGHT_PRESSED = 1
    UP_PRESSED = 2
    DOWN_PRESSED = 3
    TRIANGLE_PRESSED = 4
    CROSS_PRESSED = 5
    SQUARE_PRESSED = 6
    CIRCLE_PRESSED = 7
    NO_EVENT = 8
    MENU_PRESSED = 9
    R2_PRESSED = 10 # change to R1/L1
    L2_PRESSED = 11    
    RELEASED = 12
    PS_HOME = 13
    PS_SHARE = 14

class Ps4GameController():
    '''
        This class is responsible for the joystick readings and updates for 1 joystick only. This class is easily changed 
        for use with another controller. Just add a new profile instead of read_ps4_profile for the button events.
    '''
    RETRIES = 30

    def __init__(self):
        self._connected = False
        self._event_profile = self.read_ps4_profile
        self._retries = 0
        self._device = None
        self._event = None 
        self._released = False

        self.connect()

    def read_ps4_profile(self, dpad, button_id):
        '''
            This function reads the report for the PS4 Controller Bluetooth

            dpad determines pressed and released button too!
        '''
        #logging.debug(f"dapd {dpad} button id {button_id}")
        self._released = False

        if dpad == (17, -1):
            return ControllerEvent.UP_PRESSED
        elif dpad == (16, 1):
            return ControllerEvent.RIGHT_PRESSED
        elif dpad == (17, 1):
            return ControllerEvent.DOWN_PRESSED
        elif dpad == (16, -1):
            return ControllerEvent.LEFT_PRESSED
        elif dpad == (17, 0):
            return ControllerEvent.RELEASED
        elif dpad == (16, 0):
            return ControllerEvent.RELEASED
        elif dpad == (17, 0):
            return ControllerEvent.RELEASED
        elif dpad == (16, 0):
            return ControllerEvent.RELEASED
        elif button_id == 304 and dpad == (304, 1):
            return ControllerEvent.CROSS_PRESSED
        elif button_id == 304 and dpad == (304, 0):
            return ControllerEvent.RELEASED
        elif button_id == 308 and dpad == (308, 1):
            return ControllerEvent.SQUARE_PRESSED
        elif button_id == 308 and dpad == (308, 0):
            return ControllerEvent.RELEASED
        elif button_id == 307 and dpad == (307, 1):
            return ControllerEvent.TRIANGLE_PRESSED
        elif button_id == 307 and dpad == (307, 0):
            return ControllerEvent.RELEASED
        elif button_id == 305 and dpad == (305, 1):
            return ControllerEvent.CIRCLE_PRESSED
        elif button_id == 305 and dpad == (305, 0):
            return ControllerEvent.RELEASED
        elif button_id == 315 and dpad == (315, 1):
            return ControllerEvent.MENU_PRESSED
        elif button_id == 315 and dpad == (315, 0):
            return ControllerEvent.RELEASED
        elif button_id == 312 and dpad == (312, 1):
            return ControllerEvent.L2_PRESSED    
        elif button_id == 312 and dpad == (312, 0):
            return ControllerEvent.RELEASED            
        elif button_id == 313 and dpad == (313, 1):
            return ControllerEvent.R2_PRESSED
        elif button_id == 313 and dpad == (313, 0):
            return ControllerEvent.RELEASED 
        elif button_id == 314 and dpad == (314, 1):
            return ControllerEvent.PS_SHARE   
        elif button_id == 314 and dpad == (314, 0):
            return ControllerEvent.RELEASED   
        elif button_id == 316 and dpad == (316, 1):
            return ControllerEvent.PS_HOME    
        elif button_id == 316 and dpad == (316, 0):
            return ControllerEvent.RELEASED          
        elif button_id == 6: # todo
            return ControllerEvent.NO_EVENT
        else:
            return ControllerEvent.NO_EVENT

    def connect(self):
        '''
            This function connects the controller first controller found. It should be a PS4 controller.

            supported_profiles:
        '''
        while(not self._connected and self._retries < Ps4GameController.RETRIES):
            try:
                self._device = InputDevice('/dev/input/event2')
                self._connected = True
                self._retries = 0
                self._device.grab()

                logging.info("Connected PS4 Controller Successfully!")
                logging.info("Use 'Options' to gracefully shutdown the robot!\n")
                logging.info(self._device)
            except OSError as exception:
                self._retries += 1
                logging.info(f"Connecting attempt[{self._retries}] to device failed... retrying in 5 sec!")
                time.sleep(5)

        if not self._connected:
            raise NoJoystickConnectedException("Cannot connect game controller!")

    def rumble(self):
        '''
            This function makes the controller rumble when its has the capability.
        '''
        rumble = ff.Rumble(strong_magnitude=0x0000, weak_magnitude=0xffff)
        ff.EffectType(ff_rumble_effect=rumble)
        duration_ms = 1000

        effect = ff.Effect(
            ecodes.FF_RUMBLE, -1, 0,  # pylint: disable=no-member
            ff.Trigger(0, 0),
            ff.Replay(duration_ms, 0),
            ff.EffectType(ff_rumble_effect=rumble)
        )

        repeat_count = 1
        effect_id = self._device.upload_effect(effect)
        self._device.write(ecodes.EV_FF, effect_id, repeat_count) # pylint: disable=no-member
        time.sleep(1)
        self._device.erase_effect(effect_id)

    def disconnect(self):
        '''
            This function correctly disconnects the controller
        '''
        if self._connected and self._device is not None:
            logging.info("Joystick disconnected")
            self._device.ungrab()
            self._connected = False
            self._device.close()

    def is_connected(self):
        '''
            This function returns the state of the connection.
        '''
        return self._connected

    def get_last_event(self):
        '''
            This function reads event last read from the game controller and resets it. This function is used by other 
            modules to get the last event fired.
        '''
        event = self._event
        self._event = None
        return event

    def get_event(self):
        '''
            This function reads event report from the controller. It is the event handled in a different thread 
            than the main thread
        '''
        try:
            for event in self._device.read_loop():
                if event.type == ecodes.EV_KEY: # pylint: disable=no-member
                    profile_event = self._event_profile((event.code,event.value), event.code)
                    if profile_event != ControllerEvent.NO_EVENT:
                        self._event = profile_event
                        logging.info(f"GC::Last event: {self._event}")
                        if self._event == ControllerEvent.MENU_PRESSED:
                            self.disconnect()
                            return
                        elif profile_event == ControllerEvent.RELEASED:
                            self._released = True

                elif event.type == ecodes.EV_ABS: # pylint: disable=no-member
                    profile_event = self._event_profile((event.code,event.value), event.code)
                    if profile_event != ControllerEvent.NO_EVENT:
                        self._event = profile_event
                        logging.info(f"GC::Last event: {self._event}")
                        if profile_event == ControllerEvent.RELEASED:
                            self._released = True

        except OSError as exception:
            logging.debug(exception)
            raise JoystickDisconnectedException("Game Controller disconnected!") from exception

        return None
