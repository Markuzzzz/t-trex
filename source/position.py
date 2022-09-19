'''
    This module contains the Position class.
'''
class Position():
    ''' This class contains the x,y,z positions.'''
    @property
    def x(self):
        ''' This is the x position.'''
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        ''' This is the y position.'''
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    @property
    def z(self):
        ''' This is the z position.'''
        return self._z

    @z.setter
    def z(self, z):
        self._z = z

    def __init__(self,x, y, z):
        self._x = x
        self._y = y
        self._z = z
