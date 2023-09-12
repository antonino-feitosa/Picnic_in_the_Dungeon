
from typing import Set
from typing import Tuple

from algorithms import ApplicationError
from algorithms import Random
from algorithms import Overlap
from algorithms import Direction

from device import Image
from device import Canvas
from device import Rectangle
from device import SpriteSheet


class Ground:
    def __init__(self, canvas: Canvas, pixelsUnit: int, rand: Random):
        self.rand = rand
        self.canvas = canvas
        self.pixelsUnit = pixelsUnit
        self.groundPositions: Set[Tuple[int, int]] = set()
        self.wallsPositions: Set[Tuple[int, int]] = set()
        self.groundSheet: SpriteSheet
        self.wallSheet: SpriteSheet
        dimension = self.canvas.dimension
        self.area = Rectangle(0, 0, dimension[0], dimension[1])

    def addTile(self, position: Tuple[int, int], image: Image) -> None:
        dx = position[0] * self.pixelsUnit
        dy = position[1] * self.pixelsUnit
        dest = Rectangle(dx, dy, self.pixelsUnit, self.pixelsUnit)
        self.canvas.drawAtCanvas(image, dest)

    def addGround(self, position: Tuple[int, int]) -> None:
        if self.groundSheet is None:
            raise ApplicationError(
                'Assign a sprite sheet to the ground first!')
        if self.area.contains(position[0], position[1]):
            sheet = self.groundSheet
            image = self.rand.choice(sheet.images)
            self.addTile(position, image)
            self.groundPositions.add(position)

    def addWall(self, position: Tuple[int, int]) -> None:
        if self.wallSheet is None:
            raise ApplicationError('Assign a sprite sheet to the walls first!')
        sheet = self.wallSheet
        if self.area.contains(position[0], position[1]):
            sheet = self.wallSheet
            id = Ground.calculateWallIndexInSheet(
                position, self.wallsPositions)
            self.addTile(position, sheet.images[id])
            self.wallsPositions.add(position)

    def computeWalls(self) -> None:
        if self.wallSheet is None:
            raise ApplicationError('Assign a sprite sheet to the walls first!')
        sheet = self.wallSheet
        walls = Ground.calculateWalls(self.groundPositions)
        walls = set(
            filter(lambda pos: self.area.contains(pos[0], pos[1]), walls))
        for position in walls:
            id = Ground.calculateWallIndexInSheet(position, walls)
            self.addTile(position, sheet.images[id])
            self.wallsPositions.add(position)

    @staticmethod
    def calculateWallIndexInSheet(point: Tuple[int, int], walls: Set[Tuple[int, int]]) -> int:
        mask = 0
        for dir in Direction.cardinals():
            if dir.next(point) in walls:
                mask += Overlap.fromDirection(dir).value
        return mask

    @staticmethod
    def calculateWalls(ground: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        border: Set[Tuple[int, int]] = set()
        for pos in ground:
            for dir in Direction.directions():
                wall = dir.next(pos)
                if wall not in ground:
                    border.add(wall)
        return border
