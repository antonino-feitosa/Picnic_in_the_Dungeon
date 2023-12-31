
from core import Game

from device import Image
from device import SpriteSheet
from device import TiledCanvas

from algorithms import Random
from algorithms import Overlap
from algorithms import Point
from algorithms import Direction

from systems.map_system import MapSystem
from systems.view_system import ViewSystem


class MapViewComponent:
    def __init__(self, system:'MapViewSystem', canvas: TiledCanvas, ground: SpriteSheet, walls: SpriteSheet):
        self.system = system
        self.canvas = canvas
        self.wallSheet = walls
        self.groundSheet = ground
        self.wallsPositions: set[Point] = set()
        self.enabled = True
        system.components.append(self)

    def draw(self, position: Point = Point()):
        self.canvas.draw(position)

    def drawAtScreen(self, position: Point):
        self.canvas.drawAtScreen(position)

    def addGround(self, ground: set[Point], rand: Random) -> None:
        dimension = self.canvas.dimension
        sheet = self.groundSheet
        for position in ground:
            if position in dimension:
                image = rand.choice(sheet.images)
                self.clearPositions({position})
                self.canvas.drawAtCanvas(image, position)

    def addWall(self, wall: set[Point]) -> None:
        for position in wall:
            self.updateWall(position)
            for dir in Direction.All:
                neigh = position + dir
                if neigh in self.wallsPositions:
                    self.updateWall(neigh)

    def updateWall(self, position: Point) -> None:
        dimension = self.canvas.dimension
        if position in dimension:
            id = self.calculateWallIndexInSheet(position, self.wallsPositions)
            image = self.wallSheet.images[id]
            self.canvas.drawAtCanvas(image, position)
            self.wallsPositions.add(position)

    def clearPositions(self, positions: set[Point]) -> None:
        for position in positions:
            self.canvas.clear(position)

    def shadowPositions(self, positions: set[Point]) -> None:
        for position in positions:
            self.canvas.shadow(position)

    def paintPosition(self, position: Point, image: Image) -> None:
        self.canvas.drawAtCanvas(image, position)

    @staticmethod
    def calculateWallIndexInSheet(point: Point, walls: set[Point]) -> int:
        mask = 0
        for dir in Direction.Cardinals:
            if dir + point in walls:
                mask += Overlap.fromDirection(dir).mask
        return mask


class MapViewSystem:
    def __init__(self, game: Game):
        self.game = game
        game.drawSystems.append(self)
        game.updateSystems.append(self)
        self.wallsPositions: set[Point] = set()
        self._visible: set[Point] = set()
        self.components: list[MapViewComponent] = []
        self.enabled = True

    def update(self):
        rand = self.game.rand
        visible = self.game[ViewSystem].visible
        wallsForArea = self.game[MapSystem].getWallsForArea(visible)
        included = visible.difference(self._visible)
        removed = self._visible.difference(visible)
        for component in self.components:
            component.shadowPositions(removed)
            component.addGround(included, rand)
            component.addWall(wallsForArea)
        self._visible = visible

    def draw(self):
        for component in self.components:
            component.draw()
