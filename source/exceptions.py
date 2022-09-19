'''
    Custom Exception Module
'''
class NoJoystickConnectedException(Exception):
    """A custom exception used to report when no joysticks found."""
    pass

class JoystickDisconnectedException(Exception):
    """A custom exception used to report when joystick is disconnected."""
    pass

class ProgramKilled(Exception):
    """A custom exception used to signal that the progam will be killed."""
    pass

class ServoControllerInitializeException(Exception):
    """A custom exception used to report that the initialization of the servo controller failed!"""
    pass

class PiJuiceInitializeException(Exception):
    """A custom exception used to report that the initialization of the servo controller failed!"""
    pass

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""
    pass
