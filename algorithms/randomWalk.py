from typing import Set
from typing import Sequence, Set

from algorithms import Random
from algorithms import Position
from algorithms import Direction


class RandomWalk:
    def __init__(self, steps: int, directions: Sequence[Direction], rand: Random):
        self.rand = rand
        self.steps = steps
        self.directions = directions
        self._lastPosition: Position = Position()

    @property
    def lastPosition(self):
        return self._lastPosition

    def makeRandom(self, center: Position) -> Set[Position]:
        positions: Set[Position] = set()
        current = center
        lastDirection = None
        directions = self.directions
        for _ in range(self.steps - 1):
            positions.add(current)
            index = self.rand.choiceIndex(directions)
            dir = directions[index]
            if -dir == lastDirection:
                index = (index + 1) % len(directions)
                dir = directions[index]
            lastDirection = dir
            current += dir
        positions.add(current)
        self._lastPosition = current
        return positions

    def makeForward(self, center: Position) -> Set[Position]:
        positions: Set[Position] = set()
        directions = self.directions
        dir = self.rand.choice(directions)
        current = center
        for _ in range(self.steps - 1):
            positions.add(current)
            current += dir
        positions.add(current)
        self._lastPosition = current
        return positions

    def makeStart(self, center: Position) -> Set[Position]:
        positions: Set[Position] = set()
        validPair = [
            (Direction.Up, Direction.Left),
            (Direction.Up, Direction.Right),
            (Direction.Down, Direction.Left),
            (Direction.Down, Direction.Right),
        ]
        index = self.rand.choiceIndex(validPair)
        directions = [validPair[index][0], validPair[index][1]]
        current = center
        for _ in range(self.steps - 1):
            positions.add(current)
            dir = self.rand.choice(directions)
            current = dir + current
        positions.add(current)
        self._lastPosition = current
        return positions
