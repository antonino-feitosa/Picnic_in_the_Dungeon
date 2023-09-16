
import random

from enum import Enum
from typing import Set
from typing import Dict
from typing import List
from typing import Tuple
from typing import TypeVar
from typing import Callable
from typing import NamedTuple


Point = NamedTuple('Point', [('x', int), ('y', int)])
Dimension = NamedTuple('Dimension', [('width', int), ('height', int)])


class ApplicationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Direction(Enum):
    UP = Point(0, -1)
    DOWN = Point(0, 1)
    LEFT = Point(-1, 0)
    RIGHT = Point(1, 0)
    UP_LEFT = Point(-1, -1)
    UP_RIGHT = Point(1, -1)
    DOWN_LEFT = Point(-1, 1)
    DOWN_RIGHT = Point(1, 1)

    def next(self, position: Point) -> Point:
        return Point(position.x + self.value.x, position.y + self.value.y)

    def opposite(self) -> 'Direction':
        return Direction((-self.value.x, -self.value.y))

    def __str__(self):
        return str(self.name)

    @classmethod
    def directions(cls) -> List['Direction']:
        return [
            cls.UP,
            cls.DOWN,
            cls.LEFT,
            cls.RIGHT,
            cls.UP_LEFT,
            cls.UP_RIGHT,
            cls.DOWN_LEFT,
            cls.DOWN_RIGHT]

    @classmethod
    def cardinals(cls) -> List['Direction']:
        return [cls.UP, cls.DOWN, cls.LEFT, cls.RIGHT]

    @classmethod
    def diagonals(cls) -> List['Direction']:
        return [cls.UP_LEFT, cls.UP_RIGHT, cls.DOWN_LEFT, cls.DOWN_RIGHT]


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

    def choice(self, elements: List[T]) -> T:
        index = self.choiceIndex(elements)
        return elements[index]

    def choiceIndex(self, elements: List) -> int:
        size = len(elements)
        if size <= 0:
            raise ApplicationError('The list can not be empty!')
        return self.rand.randint(0, size-1)


class RandomWalker:
    def __init__(self, iterations: int, length: int, rand: Random):
        self.iterations = iterations
        self.length = length
        self.rand = rand
        self.center: Point = Point(0, 0)
        self.restartAtCenter = True
        self.algorithm = self.randomAlgorithm

    def run(self) -> Set[Point]:
        positions = set()
        current = self.center
        for _ in range(self.iterations):
            current = self.algorithm(current, positions)
            if self.restartAtCenter:
                current = self.center
        return positions

    def makeTree(self, depth: int) -> Set[Point]:
        positions: Set[Point] = set()
        if depth > 0:
            if self.algorithm == self.starAlgorithm:
                directions = [
                    (Direction.UP, Direction.LEFT),
                    (Direction.UP, Direction.RIGHT),
                    (Direction.DOWN, Direction.LEFT),
                    (Direction.DOWN, Direction.RIGHT),
                ]
                self._makeStarTree(depth, self.center,
                                   directions, None, positions)
            else:
                directions = Direction.cardinals()
                self._makeTree(depth, self.center, directions, None, positions)

        return positions

    def _makeTree(self,
                  depth: int,
                  startPoint: Point,
                  directions: List[Direction],
                  lastDirection: Direction | None,
                  positions: Set[Point]
                  ) -> None:
        if depth > 0:
            for dir in directions:
                if dir != lastDirection:
                    lastPoint = self.algorithm(
                        startPoint, positions, dir)  # type: ignore
                    self._makeTree(depth - 1, lastPoint,
                                   directions, dir, positions)
        pass

    def _makeStarTree(self,
                      depth: int,
                      startPoint: Point,
                      directions: List[Tuple[Direction, Direction]],
                      lastDirection: Tuple[Direction, Direction] | None,
                      positions: Set[Point]
                      ) -> None:
        if depth > 0:
            for dir in directions:
                if dir != lastDirection:
                    lastPoint = self.algorithm(
                        startPoint, positions, dir)  # type: ignore
                    self._makeStarTree(depth - 1, lastPoint,
                                       directions, dir, positions)
        pass

    def randomAlgorithm(self,
                        startPoint: Point,
                        positions: Set[Point],
                        lastDirection: Direction | None = None
                        ) -> Point:

        current = startPoint
        cardinals = Direction.cardinals()
        for _ in range(self.length-1):
            positions.add(current)
            index = self.rand.choiceIndex(cardinals)
            dir = cardinals[index]
            if dir.opposite() == lastDirection:
                index = (index + 1) % len(cardinals)
                dir = cardinals[index]
            lastDirection = dir
            current = dir.next(current)
        positions.add(current)
        return current

    def forwardAlgorithm(self,
                         startPoint: Point,
                         positions: Set[Point],
                         lastDirection: Direction | None = None
                         ) -> Point:

        validDirections = Direction.cardinals()
        if lastDirection is not None:
            validDirections.remove(lastDirection.opposite())
        direction = self.rand.choice(validDirections)
        current = startPoint
        for _ in range(self.length-1):
            positions.add(current)
            current = direction.next(current)
        positions.add(current)
        return current

    def starAlgorithm(self,
                      startPoint: Point,
                      positions: Set[Point],
                      lastDirection: Tuple[Direction,
                                           Direction] | Direction | None = None
                      ) -> Point:

        validPair = [
            (Direction.UP, Direction.LEFT),
            (Direction.UP, Direction.RIGHT),
            (Direction.DOWN, Direction.LEFT),
            (Direction.DOWN, Direction.RIGHT),
        ]
        if lastDirection is not None and type(lastDirection) is Tuple[Direction, Direction]:
            validPair.remove(
                (lastDirection[0].opposite(), lastDirection[1].opposite()))

        index = self.rand.choiceIndex(validPair)
        directions = [validPair[index][0], validPair[index][1]]
        current = startPoint
        for _ in range(self.length-1):
            positions.add(current)
            dir = self.rand.choice(directions)
            current = dir.next(current)
        positions.add(current)
        return current


class BresenhamLineAlgorithm:
    '''https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm'''

    def __init__(self):
        pass

    def plotLine(self, start: Point, end: Point) -> List[Point]:
        return self._plotLine(start.x, start.y, end.x, end.y)

    def _plotLine(self, x0: int, y0: int, x1: int, y1: int) -> List[Point]:
        if abs(y1 - y0) < abs(x1 - x0):
            if x0 > x1:
                result = self._plotLineLow(x1, y1, x0, y0)
                result.reverse()
                return result
            else:
                return self._plotLineLow(x0, y0, x1, y1)
        else:
            if y0 > y1:
                result = self._plotLineHigh(x1, y1, x0, y0)
                result.reverse()
                return result
            else:
                return self._plotLineHigh(x0, y0, x1, y1)

    def _plotLineHigh(self, x0: int, y0: int, x1: int, y1: int) -> List[Point]:
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

    def _plotLineLow(self, x0: int, y0: int, x1: int, y1: int) -> List[Point]:
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


class FieldOfView:
    '''Ray Casting through BresenhamLineAlgorithm'''

    def __init__(self):
        self.line = BresenhamLineAlgorithm()

    def calculate(self, center: Point, radius:int, ground:Set[Point]) -> Set[Point]:
        visible: Set[Point] = set()
        for line in self._getRays(center, radius):
            i = 0
            size = min(len(line), radius)
            while i < size and line[i] in ground:
                visible.add(line[i])
                i += 1
        return visible

    def _getRays(self, center:Point, radius:int) -> List[List[Point]]:
        rays:List[List[Point]] = []
        line = BresenhamLineAlgorithm()
        for y in range(center.y - radius, center.y + radius):
            rays.append(line.plotLine(center, Point(center.x - radius, y)))
            rays.append(line.plotLine(center, Point(center.x + radius-1, y)))
        for x in range(center.x - radius, center.x + radius):
            rays.append(line.plotLine(center, Point(x, center.y - radius)))
            rays.append(line.plotLine(center, Point(x, center.y + radius-1)))
        return rays
