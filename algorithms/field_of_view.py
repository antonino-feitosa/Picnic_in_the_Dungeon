
from typing import Callable

from algorithms import plotLine
from algorithms import Point
from algorithms import Direction


def _getRaysOctant(center: Point, radius: int, octant: int) -> list[list[Point]]:
    rays: list[list[Point]] = []
    up = center.y - radius
    down = center.y + radius
    left = center.x - radius
    right = center.x + radius
    upToCenter = range(center.y - radius, center.y + 1)
    downToCenter = range(center.y, center.y + radius + 1)
    leftToCenter = range(center.x - radius, center.x + 1)
    rightToCenter = range(center.x, center.x + radius + 1)
    centerToUp = range(center.y - radius, center.y + 1)
    centerToLeft = range(center.y - radius, center.y + 1)
    centerToDown = range(center.y, center.y + radius + 1)
    centerToRight = range(center.x, center.x + radius + 1)
    match octant:
        case 1:  # up right
            for x in centerToRight:
                rays.append(plotLine(center, Point(x, up)))
        case 2:  # right up
            for y in upToCenter:
                rays.append(plotLine(center, Point(right, y)))
        case 3:  # right down
            for y in centerToDown:
                rays.append(plotLine(center, Point(right, y)))
        case 4:  # down right
            for x in rightToCenter:
                rays.append(plotLine(center, Point(x, down)))
        case 5:  # down left
            for x in centerToLeft:
                rays.append(plotLine(center, Point(x, down)))
        case 6:  # left down
            for y in downToCenter:
                rays.append(plotLine(center, Point(left, y)))
        case 7:  # left up
            for y in centerToUp:
                rays.append(plotLine(center, Point(left, y)))
        case 8:  # up left
            for x in leftToCenter:
                rays.append(plotLine(center, Point(x, up)))
    return rays


def _getRaysSquare(
    center: Point, radius: int, direction: Direction
) -> list[list[Point]]:
    rays: list[list[Point]] = []
    for y in range(center.y - radius, center.y + radius + 1):
        rays.append(plotLine(center, Point(center.x - radius, y)))
        rays.append(plotLine(center, Point(center.x + radius, y)))
    for x in range(center.x - radius, center.x + radius + 1):
        rays.append(plotLine(center, Point(x, center.y - radius)))
        rays.append(plotLine(center, Point(x, center.y + radius)))
    return rays


def _getRaysCone(
    center: Point, radius: int, direction: Direction
) -> list[list[Point]]:
    octants = (0, 0)
    match direction:
        case Direction.Up:
            octants = (8, 1)
        case Direction.Down:
            octants = (4, 5)
        case Direction.Left:
            octants = (6, 7)
        case Direction.Right:
            octants = (2, 3)
        case Direction.UpLeft:
            octants = (8, 7)
        case Direction.UpRight:
            octants = (1, 2)
        case Direction.DownLeft:
            octants = (5, 6)
        case Direction.DownRight:
            octants = (3, 4)
    rays: list[list[Point]] = []
    rays = [
        *_getRaysOctant(center, radius, octants[0]),
        *_getRaysOctant(center, radius, octants[1]),
    ]
    return rays


def _getRaysPeripheral(
    center: Point, radius: int, direction: Direction
) -> list[list[Point]]:
    octants = []
    match direction:
        case Direction.Up:
            octants = [1, 2, 7, 8]
        case Direction.Down:
            octants = [3, 4, 5, 6]
        case Direction.Left:
            octants = [5, 6, 7, 8]
        case Direction.Right:
            octants = [1, 2, 3, 4]
        case Direction.UpLeft:
            octants = [1, 6, 7, 8]
        case Direction.UpRight:
            octants = [1, 2, 3, 8]
        case Direction.DownLeft:
            octants = [4, 5, 6, 7]
        case Direction.DownRight:
            octants = [2, 3, 4, 5]
    rays: list[list[Point]] = []
    for oct in octants:
        rays += _getRaysOctant(center, radius, oct)
    return rays


class FieldOfView:
    AngleCone = "cone"
    AngleRadial = "radial"
    AnglePeripheral = "peripheral"

    FormatOctal = "octal"
    FormatCircle = "circle"
    FormatSquare = "square"
    FormatDiamond = "diamond"

    def __init__(self, radius: int, isOpaque: Callable[[int,int], bool]):
        self.radius = radius
        self.isOpaque = isOpaque
        self.focalDistance: int = 0
        self._formatFunction: Callable[[Point, Point], float]
        self._angleFunction: Callable[[Point, int, Direction], list[list[Point]]]
        self.angleOfView = FieldOfView.AngleRadial
        self.formatOfView = FieldOfView.FormatSquare

    @property
    def angleOfView(self):
        return self._angleFunction

    @angleOfView.setter  # radial, peripheral, con
    def angleOfView(self, value: str) -> None:
        match value:
            case FieldOfView.AngleCone:
                self._angleFunction = _getRaysCone
            case FieldOfView.AnglePeripheral:
                self._angleFunction = _getRaysPeripheral
            case FieldOfView.AngleRadial:
                self._angleFunction = _getRaysSquare
            case _:
                raise ValueError("Expected: cone, radial or peripheral")

    @property
    def formatOfView(self):
        return self._formatFunction

    @formatOfView.setter  # octal, square, circle, diamond
    def formatOfView(self, value: str) -> None:
        match value:
            case FieldOfView.FormatOctal:
                self._formatFunction = self._octalDistance
            case FieldOfView.FormatCircle:
                self._formatFunction = lambda p1, p2: p1.distanceCircle(p2)
            case FieldOfView.FormatDiamond:
                self._formatFunction = lambda p1, p2: p1.distanceDiamond(p2)
            case FieldOfView.FormatSquare:
                self._formatFunction = lambda p1, p2: p1.distanceSquare(p2)
            case _:
                raise ValueError("Expected: octal, square, circle or diamond")

    def rayCasting(self, center: Point, direction: Direction = Direction.Up) -> set[Point]:
        visible: set[Point] = set()
        for line in self._angleFunction(center, self.radius, direction):
            i = 0
            while i < len(line) and not self.isOpaque(line[i].x, line[i].y):
                dist = self._formatFunction(center, line[i])
                if dist >= self.focalDistance and dist <= self.radius + 0.5:
                    visible.add(line[i])
                i += 1
            if i < len(line):
                dist = self._formatFunction(center, line[i])
                if dist >= self.focalDistance and dist <= self.radius + 0.5:
                    visible.add(line[i])
        return visible

    def _octalDistance(self, center: Point, other: Point) -> float:
        dx = abs(center.x - other.x)
        dy = abs(center.y - other.y)
        dist = dx + dy
        if center.x != other.x and center.y != other.y and dist > self.radius:
            if dist > self.radius + 1:
                dist -= 2
            else:
                dist -= 1
        return dist
