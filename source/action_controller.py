'''
    This module contains all the action related stuff.
'''
import logging
import asyncio
from action import Action

logging.getLogger('asyncio').setLevel(logging.WARNING)

class ActionController():
    '''
        This class takes care of the action execution, registering and state.
    '''
    def __init__(self):
        self._actions = {}
        self._action_events = {}
        self._current_action = None
        self._proposed_action = None
        self._last_action = None
        self._released = True
        self._current_action_function = None
        self._event_handler = None
        self.last_event = None
        self._is_busy = False
        self._repeat_action = False

    def register_event_handler(self, function):
        '''
            This function registers the update function to get the event from the controller
            during a running action.
        '''
        self._event_handler = function

    def update(self) -> bool:
        '''
            This function catches the events during a running action
        '''
        pass

    def register(self, action:Action, function, event:int):
        '''
            This function registers the action to a external function and event maps

            : action - action type
            : function - the external function to which the action is registered and
              is called when an action occurs
            : event - event number or enum
        '''
        self._actions[action] = function
        self._action_events[event] = action

    def process_event(self, event) -> Action:
        '''
            This function processes the event based on an action.
        '''
        if event.name == "NO_EVENT":  # todo
            return None
        elif event.name == "RELEASED":
            self._released = True
            self._last_action = None
            return self._action_events[event]
        else:
            self._released = False
            return self._action_events[event]

    def execute(self):
        '''
            This function executes the action using the registered external function
        '''
        self._proposed_action = None

        self.last_event = self._event_handler()

        if(self.last_event != None):
            self._proposed_action = self.process_event(self.last_event)
        elif(self.last_event == None and self._repeat_action):
            self._proposed_action = self._last_action
    
        #logging.debug(f"proposed action: {self._proposed_action} repeat {self._repeat_action} last {self._last_action} busy {self._is_busy}")
        if self._proposed_action != None and not self._is_busy:               
            self._current_action_function = self._actions[self._proposed_action]           
            self._current_action = self._proposed_action  
            self._is_busy = True               
            logging.debug(f"Action started: {self._current_action}")
            self._current_action_function()    

    def is_repeating(self):
        '''
            This function checks whether the last action is equal to the current action, hence a repeating action.
        '''
        if self._current_action == self._last_action:
            return True

        return False   

    def end_action(self, repeat = False):
        '''
            This function ends an action that is running, or set it to an repeating action.
        '''
        self._last_action = self._current_action
        self._is_busy = False

        logging.debug(f"Action ended: {self._current_action}")
        
        self._current_action = None
        
        if not repeat:
            self._repeat_action = False
        else:
            self._repeat_action = True
