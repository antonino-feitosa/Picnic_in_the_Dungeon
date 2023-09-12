
from typing import Set
from typing import Tuple

from algorithms import Random
from algorithms import Overlap
from algorithms import Direction

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

    def paintGround(self, positions: Set[Tuple[int, int]], sheet: SpriteSheet) -> None:
        dimension = self.canvas.dimension
        rect = Rectangle(0, 0, dimension[0], dimension[1])
        valid = filter(lambda pos: rect.contains(pos[0], pos[1]), positions)
        for x, y in valid:
            dx = x * self.pixelsUnit
            dy = y * self.pixelsUnit
            id = self.rand.choiceIndex(sheet.images)
            dest = Rectangle(dx, dy, self.pixelsUnit, self.pixelsUnit)
            self.canvas.drawAtCanvas(sheet.images[id], dest)
            self.groundPositions.add((x, y))

    def paintWalls(self, groundPositions: Set[Tuple[int, int]], sheet: SpriteSheet) -> None:
        dimension = self.canvas.dimension
        rect = Rectangle(0, 0, dimension[0], dimension[1])
        walls = Ground.calculateWalls(groundPositions)
        walls = set(filter(lambda pos: rect.contains(pos[0], pos[1]), walls))
        for x, y in walls:
            dx = x * self.pixelsUnit
            dy = y * self.pixelsUnit
            id = Ground.calculateWallIndexInSheet((x, y), walls)
            dest = Rectangle(dx, dy, self.pixelsUnit, self.pixelsUnit)
            self.canvas.drawAtCanvas(sheet.images[id], dest)
            self.wallsPositions.add((x, y))
    
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
