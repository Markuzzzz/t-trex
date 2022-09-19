'''
    This module contains the movement class.
'''
class Movement():
    '''
        This class contains the movement information.
    '''
    @property
    def x_speed(self):
        ''' This is the speed value along the x-axis. '''
        return self._x_speed

    @x_speed.setter
    def x_speed(self, x_speed):
        self._x_speed = x_speed

    @property
    def y_speed(self):
        ''' This is the speed value along the y-axis. '''
        return self._y_speed

    @y_speed.setter
    def y_speed(self, y_speed):
        self._y_speed = y_speed

    @property
    def z_speed(self):
        ''' This is the speed value along the z-axis. '''
        return self._z_speed

    @z_speed.setter
    def z_speed(self, z_speed):
        self._z_speed = z_speed

    def __init__(self,x_speed, y_speed, z_speed):
        self._x_speed = x_speed
        self._y_speed = y_speed
        self._z_speed = z_speed
