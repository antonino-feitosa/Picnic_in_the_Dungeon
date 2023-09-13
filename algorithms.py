
import random

from enum import Enum
from typing import Set
from typing import Dict
from typing import List
from typing import Tuple
from typing import TypeVar


class ApplicationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)

    def next(self, position: Tuple[int, int]) -> Tuple[int, int]:
        return (position[0] + self.value[0], position[1] + self.value[1])

    def opposite(self) -> 'Direction':
        return Direction((-self.value[0], -self.value[1]))

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
        self.center: Tuple[int, int] = (0, 0)
        self.restartAtCenter = True
        self.algorithm = self.randomAlgorithm

    def run(self) -> Set[Tuple[int, int]]:
        positions = set()
        current = self.center
        for _ in range(self.iterations):
            current = self.algorithm(current, positions)
            if self.restartAtCenter:
                current = self.center
        return positions

    def makeTree(self, depth: int) -> Set[Tuple[int, int]]:
        positions: Set[Tuple[int, int]] = set()
        if depth > 0:
            if self.algorithm == self.starAlgorithm:
                directions = [
                    (Direction.UP, Direction.LEFT),
                    (Direction.UP, Direction.RIGHT),
                    (Direction.DOWN, Direction.LEFT),
                    (Direction.DOWN, Direction.RIGHT),
                ]
                self._makeStarTree(depth, self.center, directions, None, positions)
            else:
                directions = Direction.cardinals()
                self._makeTree(depth, self.center, directions, None, positions)

        return positions

    def _makeTree(self,
                  depth: int,
                  startPoint: Tuple[int, int],
                  directions: List[Direction],
                  lastDirection: Direction | None,
                  positions: Set[Tuple[int, int]]
                  ) -> None:
        if depth > 0:
            for dir in directions:
                if dir != lastDirection:
                    lastPoint = self.algorithm(startPoint, positions, dir) # type: ignore
                    self._makeTree(depth - 1, lastPoint,
                                   directions, dir, positions)
        pass

    def _makeStarTree(self,
                  depth: int,
                  startPoint: Tuple[int, int],
                  directions: List[Tuple[Direction,Direction]],
                  lastDirection: Tuple[Direction,Direction] | None,
                  positions: Set[Tuple[int, int]]
                  ) -> None:
        if depth > 0:
            for dir in directions:
                if dir != lastDirection:
                    lastPoint = self.algorithm(startPoint, positions, dir) # type: ignore
                    self._makeStarTree(depth - 1, lastPoint,
                                   directions, dir, positions)
        pass

    def randomAlgorithm(self,
                        startPoint: Tuple[int, int],
                        positions: Set[Tuple[int, int]],
                        lastDirection: Direction | None = None
                        ) -> Tuple[int, int]:

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
                         startPoint: Tuple[int, int],
                         positions: Set[Tuple[int, int]],
                         lastDirection: Direction | None = None
                         ) -> Tuple[int, int]:

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
                      startPoint: Tuple[int, int],
                      positions: Set[Tuple[int, int]],
                      lastDirection: Tuple[Direction, Direction] | None = None
                      ) -> Tuple[int, int]:

        validPair = [
            (Direction.UP, Direction.LEFT),
            (Direction.UP, Direction.RIGHT),
            (Direction.DOWN, Direction.LEFT),
            (Direction.DOWN, Direction.RIGHT),
        ]
        if lastDirection is not None:
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
