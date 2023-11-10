
from algorithms import Dimension, Direction, Point, Random, RandomWalk


class MapSystem:
    def __init__(self, dimension: Dimension, rand: Random):
        self.rand = rand
        self.dimension = dimension
        self.endPosition: Point = Point()
        self.startPosition: Point = Point()
        self.ground: set[Point] = set()
        self.walls: set[Point] = set()
        self._groundToWalls: dict[Point, set[Point]] = dict()
        self._wallToGround: dict[Point, set[Point]] = dict()

    def getWallsForGround(self, ground: Point) -> set[Point]:
        return self._groundToWalls[ground]

    def getWallsForArea(self, ground: set[Point]) -> set[Point]:
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
    def _neighborhood(position: Point, ground: set[Point]) -> set[Point]:
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
        center = Point(width // 2, height // 2)
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
                self.ground.add(Point(x, y))
        self.startPosition = Point(2, 2)
        self.endPosition = Point(width - 3, height - 3)
