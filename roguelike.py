
from typing import Set
from typing import Tuple

from algorithms import ApplicationError
from algorithms import Random
from algorithms import Overlap
from algorithms import Direction

from device import Image
from device import Canvas
from device import Device
from device import Rectangle
from device import SpriteSheet
from device import KeyboardListener
from device import MouseDragListener


class RogueLike:
    def __init__(self, gridSize: int, device: Device, rand: Random):
        self.device = device
        self.rand = rand
        self.gridSize = gridSize
        self.pixelsUnit = 32
        self.minimap = MiniMap(self.gridSize, self)
        canvas = device.loadCanvas((gridSize * self.pixelsUnit, gridSize * self.pixelsUnit))
        self.ground = Ground(canvas, self.pixelsUnit, self)
    
    def randomMap(self) -> None:
        pass

    def redraw(self):
        self.device.clear()
        self.ground.canvas.draw((0, 0))
        if self.minimap.showing:
            self.minimap.canvas.drawAtScreen(self.minimap.position)
        self.device.reload()

    def registerListeners(self):
        listenSpace = KeyboardListener({'space'})
        listenSpace.onKeyUp = self.listenerResetCamera
        self.device.addListener(listenSpace)

        listenTab = KeyboardListener({'tab'})
        listenTab.onKeyUp = self.listenerShowMinimap
        self.device.addListener(listenTab)

        listenControls = KeyboardListener({'up', 'left', 'down', 'right'})
        listenControls.onKeyUp = self.listenerControlMinimap
        self.device.addListener(listenControls)

        listenDrag = MouseDragListener()
        listenDrag.onMouseDrag = self.listenerTranslateMap
        self.device.addListener(listenDrag)

    
    def listenerControlMinimap(self, key: str) -> None:
        if self.minimap.showing:
            if key == 'down':
                self.minimap.position = (self.minimap.position[0], self.minimap.position[1]+25)
            if key == 'up':
                self.minimap.position = (self.minimap.position[0], self.minimap.position[1]-25)
            if key == 'left':
                self.minimap.position = (self.minimap.position[0]-25, self.minimap.position[1])
            if key == 'right':
                self.minimap.position = (self.minimap.position[0]+25, self.minimap.position[1])
            self.redraw()

    def listenerShowMinimap(self, key: str) -> None:
        self.minimap.showing = not self.minimap.showing
        self.redraw()
    
    def listenerTranslateMap(self, source:Tuple[int,int], dest:Tuple[int,int]) -> None:
        pos = self.device.camera.position()
        diff = (dest[0] - source[0], dest[1] - source[1])
        self.device.camera.translate(pos[0] - diff[0], pos[1] - diff[1])
        self.redraw()
    
    def listenerResetCamera(self, key: str) -> None:
        self.device.camera.translate(0, 0)
        self.redraw()

class MiniMap:
    def __init__(self, gridSize: int, game: RogueLike):
        self.pixelsUnit = 4
        self.showing = False
        self.position:Tuple[int,int] = (100, 100)
        self.canvas = game.device.loadCanvas(
            (gridSize * self.pixelsUnit, gridSize * self.pixelsUnit))
        self.ground = Ground(self.canvas, self.pixelsUnit, game)
        self.ground.groundSheet = game.device.loadSpriteSheet(
            'Tileset - MiniMap - Ground.png', (self.pixelsUnit, self.pixelsUnit), 'resources')
        self.ground.wallSheet = game.device.loadSpriteSheet(
            'Tileset - MiniMap - Walls.png', (self.pixelsUnit, self.pixelsUnit), 'resources')

    def addGround(self, position: Tuple[int, int]) -> None:
        self.ground.addGround(position)

    def addWall(self, position: Tuple[int, int]) -> None:
        self.ground.addWall(position)


class Ground:
    def __init__(self, canvas: Canvas, pixelsUnit: int, game: RogueLike):
        self.rand = game.rand
        self.canvas = canvas
        self.pixelsUnit = pixelsUnit
        self.groundPositions: Set[Tuple[int, int]] = set()
        self.wallsPositions: Set[Tuple[int, int]] = set()
        dimension = self.canvas.dimension
        self.area = Rectangle(0, 0, dimension[0], dimension[1])
        self.groundSheet = game.device.loadSpriteSheet(
            'Tileset - Ground.png', (pixelsUnit, pixelsUnit), 'resources')
        self.wallSheet = game.device.loadSpriteSheet(
            'Tileset - Walls.png', (pixelsUnit, pixelsUnit), 'resources')

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
