'''
    This module is the main entry point of the program of the t-trex robot.
'''
#!/usr/bin/env python3

# default modules
import sys
import logging
import signal
from exceptions import NoJoystickConnectedException, JoystickDisconnectedException, ProgramKilled, ServoControllerInitializeException
from exceptions import PiJuiceInitializeException
from threading import Thread

# user modules
from quadruped_cpu import QuadrupedCpu
from game_controller import Ps4GameController
from action_controller import ActionController

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Log to console
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

# Log to file
#logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# command line arguments
#   usage: python3 t-trex.py STUB
STUB = False
CONTROLLER = True

if len(sys.argv) > 1:
    for argument in sys.argv:
        if argument == "STUB":
            STUB = True
        elif argument == "NO_CONTROLLER":
            CONTROLLER = False

quadruped = QuadrupedCpu()

# Signal Handlers
# Each signal may have a signal handler, which is a function that gets called when the process receives that signal. The function is called in
# "asynchronous mode", meaning that no where in your program you have code that calls this function directly. Instead, when the signal is sent to the process,
# the operating system stops the execution of the process, and "forces" it to call the signal handler function. When that signal handler function returns,
# the process continues execution from wherever it happened to be before the signal was received, as if this interruption never occurred.
def kill_program_handler(signum, frame):
    ''' This handler is called when the kill signal is received'''
    raise ProgramKilled

# When a signal arrives during an I/O operation, it is possible that the I/O operation raises an exception after the signal handler returns.
# This is dependent on the underlying Unix system’s semantics regarding interrupted system calls.
def heart_beat(signum, frame): # pylint: disable=unused-argument
    '''
        This function is the heart beat for updating the I/O service. It may not interrupt other I/O operations. All I/O should be handled from this handler,
        which will be executed in the main thread.
    '''
    #time_started = time.time()
    if quadruped.servo_service(): # timing on RPi Zero W 2: 0.03 seconds @ alarm 0.02 seconds @ 100kHz i2c
        #logging.debug(f"Elapsed: {time.time() - time_started} seconds")
        signal.setitimer(signal.ITIMER_REAL, 0.002) #correct time by substracting the time in this handler from the default alarm time interval. @200 kHz i2c

def shut_down():
    '''
        This function is meant for gracefully shutting down the system.
    '''
    quadruped.release()
    logging.shutdown()    
    sys.exit(0)

def main():
    '''
        Main entry point of the t-trex program.
    '''
    try:
        quadruped.set_status_led(0,255,255)       
        action_controller = ActionController()

        if CONTROLLER:
            controller = Ps4GameController()
            action_controller.register_event_handler(controller.get_last_event)
            event_thread = Thread(target=controller.get_event, name='event_handler', daemon=True)
            event_thread.start()            

        quadruped.initialize(action_controller, controller, STUB)
        quadruped.get_system_report()
        
        signal.signal(signal.SIGTERM, kill_program_handler)
        signal.signal(signal.SIGINT, kill_program_handler)
        signal.signal(signal.SIGALRM, heart_beat)

        signal.setitimer(signal.ITIMER_REAL, 0.02)

        quadruped.set_status_led(0,50,25)

        while True:
            quadruped.run()
    except PiJuiceInitializeException as exception:
        quadruped.set_error_state()
        logging.info(f"Program killed due to initialization exception: running cleanup code...\n Exception Message: {exception}")
    except ProgramKilled as exception:
        quadruped.set_status_led(0,0,0)
        logging.info(f"Program killed due to program killed signal: running cleanup code...")
    except (Exception, JoystickDisconnectedException, NoJoystickConnectedException, ServoControllerInitializeException) as exception:
        quadruped.set_error_state()
        logging.info(f"Program killed due to exception: running cleanup code...\n Exception Message: {exception}")
    finally:
        shut_down()

if __name__ == "__main__":
    main()
