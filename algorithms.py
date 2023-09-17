
import random

from enum import Enum
from typing import Any
from typing import Set
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Sequence
from typing import NamedTuple


class ApplicationError(Exception):
    def __init__(self, message):
        super().__init__(message)


Dimension = NamedTuple('Dimension', [('width', int), ('height', int)])

def _dimension__contains__(self, element):
    if isinstance(element,Point):
        return element.x < self.width and element.y < self.height and element.x >=0 and element.y >= 0
    else:
        raise TypeError('The operands must be Point')

Dimension.__contains__ = _dimension__contains__


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

def distanceManhattan(first:Point, second:Point) -> int:
    return abs(first.x - second.x) + abs(first.y - second.y)

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
        return self.value[0]

    @property
    def y(self):
        return self.value[1]
    
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



class Overlap(Enum):
    EMPTY = 0b0000
    UP = 0b0001
    DOWN = 0b0010
    LEFT = 0b0100
    RIGHT = 0b1000
    UP_DONW = 0b0001 | 0b0010
    UP_LEFT = 0b0001 | 0b0100
    UP_RIGHT = 0b0001 | 0b1000
    DOWN_LEFT = 0b0010 | 0b0100
    DOWN_RIGHT = 0b0010 | 0b1000
    LEFT_RIGHT = 0b0100 | 0b1000
    UP_DOWN_LEFT = 0b0001 | 0b0010 | 0b0100
    UP_DOWN_RIGHT = 0b0001 | 0b0010 | 0b1000
    UP_LEFT_RIGHT = 0b0001 | 0b0100 | 0b1000
    DOWN_LEFT_RIGHT = 0b0010 | 0b0100 | 0b1000
    UP__DOWN_LEFT_RIGHT = 0b0001 | 0b0010 | 0b0100 | 0b1000

    def cardinals(self) -> List['Overlap']:
        return [Overlap.UP, Overlap.DOWN, Overlap.LEFT, Overlap.RIGHT]

    def inter(self, other: 'Overlap') -> 'Overlap':
        return Overlap(self.value & other.value)

    def union(self, other: 'Overlap') -> 'Overlap':
        return Overlap(self.value | other.value)

    def __contains__(self, other: 'Overlap') -> 'Overlap':
        return Overlap((self.value & other.value) == self.value)

    def __len__(self) -> int:
        sum = 0
        for other in [Overlap.UP, Overlap.DOWN, Overlap.LEFT, Overlap.RIGHT]:
            sum += ((self.value & other.value) > 0)
        return sum

    def __add__(self, other: 'Overlap') -> 'Overlap':
        return Overlap(self.value | other.value)

    def __sub__(self, other: 'Overlap') -> 'Overlap':
        return Overlap(self.value & ~other.value)

    @classmethod
    def fromDirection(cls, direction: Direction) -> 'Overlap':
        match direction:
            case Direction.UP: return Overlap.UP
            case Direction.DOWN: return Overlap.DOWN
            case Direction.LEFT: return Overlap.LEFT
            case Direction.RIGHT: return Overlap.RIGHT
            case Direction.UP_LEFT: return Overlap.UP_LEFT
            case Direction.UP_RIGHT: return Overlap.UP_RIGHT
            case Direction.DOWN_LEFT: return Overlap.DOWN_LEFT
            case Direction.DOWN_RIGHT: return Overlap.DOWN_RIGHT

    def __str__(self):
        str = ''
        str += 'U' if Overlap.UP in self else '_'
        str += 'D' if Overlap.UP in self else '_'
        str += 'L' if Overlap.UP in self else '_'
        str += 'R' if Overlap.UP in self else '_'
        return str


class Random:
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.rand = random.Random(seed)

    def nextInt(self, max: int) -> int:
        return self.rand.randint(0, max-1)

    def nextRange(self, min: int, max: int) -> int:
        return self.rand.randint(min, max-1)

    T = TypeVar("T")

    def choice(self, elements: Sequence[T]) -> T:
        index = self.choiceIndex(elements)
        return elements[index]    

    def choiceIndex(self, elements: Sequence[Any]) -> int:
        size = len(elements)
        if size <= 0:
            raise ApplicationError('The list can not be empty!')
        return self.rand.randint(0, size-1)


class Composition:
    countId = 0

    def __init__(self):
        Composition.countId += 1
        self.id = Composition.countId
        self.typeToComponent: Dict[Type, Any] = dict()

    def add(self, component) -> 'Composition':
        self.typeToComponent[type(component)] = component
        return self

    T = TypeVar('T')
    def get(self, typeOfComponent: Type[T]) -> T:
        return self.typeToComponent[typeOfComponent]
    
    def remove(self, typeOfComponent: Type) -> None:
        self.typeToComponent.pop(typeOfComponent, None)
    
    def __getitem__(self, typeOfComponent: Type[T]) -> T:
        return self.typeToComponent[typeOfComponent]
    
    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return self.id == other.id
        return NotImplemented
    
    def __ne__(self, other):
        if other.__class__ is self.__class__:
            return self.id != other.id
        return NotImplemented

class RandomWalk:
    def __init__(self, steps:int, directions:Sequence[Direction], rand: Random):
        self.rand = rand
        self.steps = steps
        self.directions = directions
        self.restartAtCenter:bool = True
        self._lastPoint: Point = Point(0,0)
    
    @property
    def lastPoint(self):
        return self._lastPoint
    
    def makeRandom(self, center:Point) -> Set[Point]:
        positions:Set[Point] = set()
        current = center
        lastDirection = None
        directions = self.directions
        for _ in range(self.steps-2):
            positions.add(current)
            index = self.rand.choiceIndex(directions)
            dir = directions[index]
            if -dir == lastDirection:
                index = (index + 1) % len(directions)
                dir = directions[index]
            lastDirection = dir
            current += dir
        positions.add(current)
        self._lastPoint = current
        return positions
    
    def makeForward(self, center:Point) -> Set[Point]:
        positions:Set[Point] = set()
        directions = self.directions
        dir = self.rand.choice(directions)
        current = center
        for _ in range(self.steps-1):
            positions.add(current)
            current += dir
        positions.add(current)
        self._lastPoint = current
        return positions
    
    def makeStart(self, center:Point) -> Set[Point]:
        positions:Set[Point] = set()
        validPair = [
            (Direction.UP, Direction.LEFT),
            (Direction.UP, Direction.RIGHT),
            (Direction.DOWN, Direction.LEFT),
            (Direction.DOWN, Direction.RIGHT),
        ]
        index = self.rand.choiceIndex(validPair)
        directions = [validPair[index][0], validPair[index][1]]
        current = center
        for _ in range(self.steps-1):
            positions.add(current)
            dir = self.rand.choice(directions)
            current = dir.next(current)
        positions.add(current)
        self._lastPoint = current
        return positions




'''Bresenham Line Algorithm'''
def plotLine(start: Point, end: Point) -> List[Point]:
    return _plotLine(start.x, start.y, end.x, end.y)

def _plotLine(x0: int, y0: int, x1: int, y1: int) -> List[Point]:
    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            result = _plotLineLow(x1, y1, x0, y0)
            result.reverse()
            return result
        else:
            return _plotLineLow(x0, y0, x1, y1)
    else:
        if y0 > y1:
            result = _plotLineHigh(x1, y1, x0, y0)
            result.reverse()
            return result
        else:
            return _plotLineHigh(x0, y0, x1, y1)

def _plotLineHigh(x0: int, y0: int, x1: int, y1: int) -> List[Point]:
    dx = x1 - x0
    dy = y1 - y0
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    D = (2 * dx) - dy
    x = x0
    points: List[Point] = []
    for y in range(y0, y1):
        points.append(Point(x, y))
        if D > 0:
            x = x + xi
            D = D + (2 * (dx - dy))
        else:
            D = D + 2*dx
    return points

def _plotLineLow(x0: int, y0: int, x1: int, y1: int) -> List[Point]:
    dx = x1 - x0
    dy = y1 - y0
    yi = 1
    if dy < 0:
        yi = -1
        dy = -dy
    D = (2 * dy) - dx
    y = y0

    points: List[Point] = []
    for x in range(x0, x1):
        points.append(Point(x, y))
        if D > 0:
            y = y + yi
            D = D + (2 * (dy - dx))
        else:
            D = D + 2*dy
    return points



def fieldOfViewRayCasting(center: Point, radius:int, ground:Set[Point]) -> Set[Point]:
    visible: Set[Point] = set()
    for line in _getRays(center, radius):
        i = 0
        size = min(len(line), radius)
        while i < size and line[i] in ground:
            visible.add(line[i])
            i += 1
    return visible

def _getRays(center:Point, radius:int) -> List[List[Point]]:
    rays:List[List[Point]] = []
    for y in range(center.y - radius, center.y + radius):
        rays.append(plotLine(center, Point(center.x - radius, y)))
        rays.append(plotLine(center, Point(center.x + radius-1, y)))
    for x in range(center.x - radius, center.x + radius):
        rays.append(plotLine(center, Point(x, center.y - radius)))
        rays.append(plotLine(center, Point(x, center.y + radius-1)))
    return rays
