from typing import Dict, Set
from algorithms import Dimension, Direction, Position, Random, RandomWalk


class MapSystem:
    def __init__(self, dimension: Dimension, rand: Random):
        self.rand = rand
        self.dimension = dimension
        self.endPosition: Position = Position()
        self.startPosition: Position = Position()
        self.ground: Set[Position] = set()
        self.walls: Set[Position] = set()
        self._groundToWalls: Dict[Position, Set[Position]] = dict()
        self._wallToGround: Dict[Position, Set[Position]] = dict()

    def getWallsForGround(self, ground: Position) -> Set[Position]:
        return self._groundToWalls[ground]

    def getWallsForArea(self, ground: Set[Position]) -> Set[Position]:
        area = set()
        for pos in ground:
            area.update(self._groundToWalls[pos])
        border = set()
        for wall in area:
            neighborhood = self._neighborhood(wall, self.ground)
            if len(neighborhood) == len(self._wallToGround[wall]):
                border.add(wall)
        return border

    @staticmethod
    def _neighborhood(position: Position, ground: Set[Position]) -> Set[Position]:
        neigh = set()
        for dir in Direction.All:
            pos = dir + position
            if pos in ground:
                neigh.add(pos)
        return neigh

    def calculateWalls(self) -> None:
        for pos in self.ground:
            self._groundToWalls.setdefault(pos, set())
            for dir in Direction.All:
                wall = pos + dir
                self._wallToGround.setdefault(wall, set())
                if wall not in self.ground:
                    self.walls.add(wall)
                    self._groundToWalls[pos].add(wall)
                    self._wallToGround[wall].add(pos)

    def makeIsland(self, iterations: int = 20) -> None:
        width, height = self.dimension
        steps = min((width - 1) // 2, (height - 1) // 2)  # -1 walls to border
        center = Position(width // 2, height // 2)
        self.startPosition = center
        self.endPosition = center
        distanceToEnd = 0
        walker = RandomWalk(steps, Direction.Cardinals, self.rand)
        for _ in range(iterations):
            walk = walker.makeRandom(center)
            end = walker.lastPosition
            self.ground.update(walk)
            distance = center.distanceSquare(end)  # TODO make rand
            if distance > distanceToEnd:
                self.endPosition = end
                distance = distanceToEnd
        self.calculateWalls()

    def makeBlack(self) -> None:
        width, height = self.dimension
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                self.ground.add(Position(x, y))
        self.startPosition = Position(2, 2)
        self.endPosition = Position(width - 3, height - 3)
