
import random

from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import NamedTuple


class ApplicationError(Exception):
    def __init__(self, message):
        super().__init__(message)


Dimension = NamedTuple('Dimension', [('width', int), ('height', int)])


Point = NamedTuple('Point', [('x', int), ('y', int)])

def _point__add__(self, other):
    if isinstance(other, Point):
        return Point(self.x + other.x, self.y + other.y)
    elif isinstance(other, Direction):
        return Point(self.x + other.x, self.y + other.y)
    else:
        raise TypeError('The operands must be Point')

def _point__mul__(self, other):
    if isinstance(other, int):
        return Point(self.x * other, self.y * other)
    else:
        raise TypeError('The operands must be Point and Scalar')

def _point__str__(self):
    return f'({self.x},{self.y})'

Point.__add__ = _point__add__
Point.__mul__ = _point__mul__
Point.__rmul__ = _point__mul__
Point.__str__ = _point__str__



class Direction(Enum):
    UP = Point(0, -1)
    DOWN = Point(0, 1)
    LEFT = Point(-1, 0)
    RIGHT = Point(1, 0)
    UP_LEFT = Point(-1, -1)
    UP_RIGHT = Point(1, -1)
    DOWN_LEFT = Point(-1, 1)
    DOWN_RIGHT = Point(1, 1)

    @property
    def x(self):
        return self.value.x

    @property
    def y(self):
        return self.value.y
    
    def __neg__(self):
        return Direction(Point(-self.x, -self.y))
    
    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            raise TypeError('The operand must be Point')
    
    def __radd__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            raise TypeError('The operand must be Point')

    def __str__(self):
        return str(self.name)

DIRECTIONS = (Direction.UP,Direction.DOWN,Direction.LEFT,Direction.RIGHT,Direction.UP_LEFT,Direction.UP_RIGHT,Direction.DOWN_LEFT,Direction.DOWN_RIGHT)
CARDINALS = (Direction.UP,Direction.DOWN,Direction.LEFT,Direction.RIGHT)
DIAGONALS = (Direction.UP_LEFT,Direction.UP_RIGHT,Direction.DOWN_LEFT,Direction.DOWN_RIGHT)




class Random:
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.rand = random.Random(seed)

    def nextInt(self, max: int) -> int:
        return self.rand.randint(0, max-1)

    def nextRange(self, min: int, max: int) -> int:
        return self.rand.randint(min, max-1)

    T = TypeVar("T")

    def choice(self, elements: List[T]) -> T:
        index = self.choiceIndex(elements)
        return elements[index]

    def choiceIndex(self, elements: List) -> int:
        size = len(elements)
        if size <= 0:
            raise ApplicationError('The list can not be empty!')
        return self.rand.randint(0, size-1)


class Composition:
    def __init__(self):
        self.typeToComponent: Dict[Type, Any] = dict()

    def add(self, component) -> 'Composition':
        self.typeToComponent[type(component)] = component
        return self

    T = TypeVar('T')
    def get(self, typeOfComponent: Type[T]) -> T:
        return self.typeToComponent[typeOfComponent]

    def remove(self, typeOfComponent: Type) -> None:
        self.typeToComponent.pop(typeOfComponent, None)
