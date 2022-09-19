'''
    This module contains a simple timer class.
'''
import time
import logging

from exceptions import TimerError

class PyTimer():
    '''
        This is a simple timer class.
    '''
    def __init__(self):
        self._start_time = None
        self._tag = "default"

    def set_timer(self, timer_value):
        self._count_down_time = timer_value

    def start(self, tag = "default"):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")

        self._start_time = time.time()
        self._tag = tag

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError("Timer is not running. Use .start() to start it")

        elapsed_time = time.time() - self._start_time
        self._start_time = None
        logging.debug(f"{self._tag} Elapsed time: {elapsed_time:0.4f} seconds")

    def update(self):
        """Update the count down timer"""
        elapsed_time = time.time() - self._start_time
        #logging.info(f"{self._tag} Elapsed time: {elapsed_time:0.4f} seconds")

        if(elapsed_time > self._count_down_time):
            self._start_time = time.time()
            return True
        return False 
