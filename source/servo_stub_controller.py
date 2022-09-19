# pylint: skip-file
class ServoStubController(object):
    """
    Servo class for controlling RC servos with the Servo PWM Pi Zero
    """
    __pwm = None
    __position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    __lowpos = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    __highpos = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    __useoffset = False
    __offset = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    __frequency = 50

    # local methods

    def __refresh_channels(self):
        """
        Internal method for refreshing the servo positions
        """
        pass

    def __calculate_offsets(self):
        """
        Internal method for calculating the start positions
        to stagger the servo position pulses
        """
        pass

    # public methods

    def __init__(self, address=0x40, low_limit=1.0,
                 high_limit=2.0, reset=True, bus=None):
        """
        Initialise the Servo object

        :param address: i2c address for the ServoPi board, defaults to 0x40
        :type address: int, optional
        :param low_limit: Pulse length in milliseconds for the
                          lower servo limit, defaults to 1.0
        :type low_limit: float, optional
        :param high_limit: Pulse length in milliseconds for the
                           upper servo limit, defaults to 2.0
        :type high_limit: float, optional
        :param reset: True = reset the controller and turn off all channels.
                      False = keep existing servo positions and frequency.
                      defaults to True
        :type reset: bool, optional
        :param bus: I2C bus number.  If no value is set the class will try to
                    find the i2c bus automatically using the device name
        :type bus: int, optional
        """

        pass

    def move(self, channel, position, steps=250):
        """
        Set the servo position

        :param channel: 1 to 16
        :type channel: int
        :param position:  value between 0 and the maximum number of steps.
        :type position: int
        :param steps: The number of steps between the the low and high limits.
                      This can be any number between 0 and 4095.
                      On a typical RC servo a step value of 250 is recommended.
                      defaults to 250
        :type steps: int, optional
        :raises ValueError: move: channel out of range
        :raises ValueError: move: steps out of range
        :raises ValueError: move: position out of range
        """
        pass

    def get_position(self, channel, steps=250):
        """
        Get the servo position

        :param channel: 1 to 16
        :type channel: int
        :param steps: The number of steps between the the low and high limits.
                      This can be any number between 0 and 4095.
                      On a typical RC servo a step value of 250 is recommended.
                      defaults to 250
        :type steps: int, optional
        :raises ValueError: get_position: channel out of range
        :return: position - value between 0 and the maximum number of steps.
                 Due to rounding errors when calculating the position, the
                 returned value may not be exactly the same as the set value.
        :rtype: int
        """
        pass

    def set_low_limit(self, low_limit, channel=0):
        """
        Set the pulse length for the lower servo limits. Typically around 1ms.
        Warning: Setting the pulse limit below 1ms may damage your servo.

        :param low_limit: Pulse length in milliseconds for the lower limit.
        :type low_limit: float
        :param channel: The channel for which the low limit will be set.
                        If this value is omitted the low limit will be
                        set for all channels., defaults to 0
        :type channel: int, optional
        :raises ValueError: set_low_limit: channel out of range
        :raises ValueError: set_low_limit: low limit out of range
        """

        pass

    def set_high_limit(self, high_limit, channel=0):
        """
        Set the pulse length for the upper servo limits. Typically around 2ms.
        Warning: Setting the pulse limit above 2ms may damage your servo.

        :param high_limit: Pulse length in milliseconds for the upper limit.
        :type high_limit: float
        :param channel: The channel for which the upper limit will be set.
                        If this value is omitted the upper limit will be
                        set for all channels., defaults to 0
        :type channel: int, optional
        :raises ValueError: set_high_limit: channel out of range
        :raises ValueError: set_high_limit: high limit out of range
        """

        pass

    def set_frequency(self, freq, calibration=0):
        """
        Set the PWM frequency

        :param freq: 40 to 1000
        :type freq: int
        :param calibration: optional integer value to offset oscillator errors.
                            defaults to 0
        :type calibration: int, optional
        """
        pass

    def output_disable(self):
        """
        Disable output via OE pin

        :raises IOError: Failed to write to GPIO pin
        """
        pass

    def output_enable(self):
        """
        Enable output via OE pin

        :raises IOError: Failed to write to GPIO pin
        """
        pass

    def offset_enable(self):
        """
        Enable pulse offsets.
        This will set servo pulses to be staggered across the channels
        to reduce surges in current draw
        """
        pass

    def offset_disable(self):
        """
        Disable pulse offsets.
        This will set all servo pulses to start at the same time.
        """
        pass

    def sleep(self):
        """
        Put the device into a sleep state
        """
        pass

    def wake(self):
        """
        Wake the device from its sleep state
        """
        pass

    def is_sleeping(self):
        pass