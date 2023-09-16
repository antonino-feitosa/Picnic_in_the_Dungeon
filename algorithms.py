
from typing import NamedTuple


Dimension = NamedTuple('Dimension', [('width', int), ('height', int)])


Point = NamedTuple('Point', [('x', int), ('y', int)])

def _point__add__(self, other):
    if isinstance(other, Point):
        return Point(self.x + other.x, self.y + other.y)
    elif isinstance(other, Direction):
        return Point(self.x + other.x, self.y + other.y)
    else:
        raise TypeError('The operands must be Point')

def _point__mul__(self, scalar):
    if isinstance(scalar, int):
        return Point(self.x * scalar, self.y * scalar)
    else:
        raise TypeError('The operands must be Point and Scalar')

def _point__str__(self):
    return f'Point(x={self.x}, y={self.y})'

Point.__add__ = _point__add__
Point.__mul__ = _point__mul__
Point.__rmul__ = _point__mul__
Point.__str__ = _point__str__


Direction = NamedTuple('Direction', [('x', int), ('y', int)])

a = 2 * Point(0,0) * 6