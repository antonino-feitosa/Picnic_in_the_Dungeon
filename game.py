
from typing import Set
from typing import cast
from typing import Type
from typing import Dict
from typing import List
from typing import Tuple
from typing import TypeVar
from typing import Generic
from typing import Callable

from core import Game
from core import Entity
from core import Subsystem

from device import Image
from device import Canvas
from device import Device
from device import Rectangle
from device import SpriteSheet
from device import UpdateListener
from device import KeyboardListener
from device import MouseDragListener

from systems import RenderSystem
from systems import RenderComponent
from systems import PositionSystem
from systems import PositionComponent

from algorithms import Point
from algorithms import Random
from algorithms import Overlap
from algorithms import Direction
from algorithms import Dimension
from algorithms import FieldOfView
from algorithms import ApplicationError


class MiniMap:
    def __init__(self, gridSize: int, game: 'RogueLike'):
        self.pixelsUnit = 4
        self.showing = False
        self.position: Point = Point(100, 100)
        self.canvas = game.device.loadCanvas(
            Dimension(gridSize * self.pixelsUnit, gridSize * self.pixelsUnit))
        self.ground = Ground(self.canvas, self.pixelsUnit, game)
        self.ground.groundSheet = game.device.loadSpriteSheet(
            'Tileset - MiniMap - Ground.png', Dimension(self.pixelsUnit, self.pixelsUnit), 'resources')
        self.ground.wallSheet = game.device.loadSpriteSheet(
            'Tileset - MiniMap - Walls.png', Dimension(self.pixelsUnit, self.pixelsUnit), 'resources')
        self.playerImage = game.device.loadImage(
            'Tileset - MiniMap - Avatar.png', 'resources')
        self.referenceImage = game.device.loadImage(
            'Tileset - MiniMap - Reference.png', 'resources')
        self.playerPosition: Point | None = None

    def addGround(self, position: Point) -> None:
        self.ground.addGround(position)

    def addWall(self, position: Point) -> None:
        self.ground.addWall(position)

    def addPlayer(self, position: Point) -> None:
        if self.playerPosition is not None:
            self.clearGround(self.playerPosition)
        self.playerPosition = position
        position = Point(position.x * self.pixelsUnit,
                         position.y * self.pixelsUnit)
        self.ground.canvas.drawAtCanvas(self.playerImage, position)

    def addReference(self, position: Point) -> None:
        position = Point(position.x * self.pixelsUnit,
                         position.y * self.pixelsUnit)
        self.ground.canvas.drawAtCanvas(self.referenceImage, position)

    def clearGround(self, position: Point) -> None:
        # TODO replace by clear position on ground
        oldPosition = Point(position.x * self.pixelsUnit,
                            position.y * self.pixelsUnit)
        self.ground.canvas.clearRegion(Rectangle(
            oldPosition.x, oldPosition.y, oldPosition.x+self.pixelsUnit, oldPosition.y+self.pixelsUnit))
        self.addGround(position)


class Ground:
    def __init__(self, canvas: Canvas, pixelsUnit: int, game: 'RogueLike'):
        self.rand = game.rand
        self.canvas = canvas
        self.pixelsUnit = pixelsUnit
        self.groundPositions: Set[Point] = set()
        self.wallsPositions: Set[Point] = set()
        dimension = self.canvas.dimension
        self.area = Rectangle(0, 0, dimension.width, dimension.height)
        self.groundSheet = game.device.loadSpriteSheet(
            'Tileset - Ground.png', Dimension(pixelsUnit, pixelsUnit), 'resources')
        self.wallSheet = game.device.loadSpriteSheet(
            'Tileset - Walls.png', Dimension(pixelsUnit, pixelsUnit), 'resources')

    def addTile(self, position: Point, image: Image) -> None:
        dx = position.x * self.pixelsUnit
        dy = position.y * self.pixelsUnit
        self.canvas.drawAtCanvas(image, Point(dx, dy))

    def addGround(self, position: Point) -> None:
        if self.groundSheet is None:
            raise ApplicationError(
                'Assign a sprite sheet to the ground first!')
        if self.area.contains(position.x, position.y):
            sheet = self.groundSheet
            image = self.rand.choice(sheet.images)
            self.addTile(position, image)
            self.groundPositions.add(position)

    def clearPositions(self, positions: Set[Point]) -> None:
        # TODO paint black
        pass

    def shadowPositions(self, positions: Set[Point]) -> None:
        # TODO paint grey alpha
        pass

    def addWall(self, position: Point) -> None:
        if self.wallSheet is None:
            raise ApplicationError('Assign a sprite sheet to the walls first!')
        sheet = self.wallSheet
        if self.area.contains(position.x, position.y):
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
            filter(lambda pos: self.area.contains(pos.x, pos.y), walls))
        for position in walls:
            id = Ground.calculateWallIndexInSheet(position, walls)
            self.addTile(position, sheet.images[id])
            self.wallsPositions.add(position)

    @staticmethod
    def calculateWallIndexInSheet(point: Point, walls: Set[Point]) -> int:
        mask = 0
        for dir in Direction.cardinals():
            if dir.next(point) in walls:
                mask += Overlap.fromDirection(dir).value
        return mask

    @staticmethod
    def calculateWalls(ground: Set[Point]) -> Set[Point]:
        border: Set[Point] = set()
        for pos in ground:
            for dir in Direction.directions():
                wall = dir.next(pos)
                if wall not in ground:
                    border.add(wall)
        return border


class RogueLike(Game):
    def __init__(self, gridSize: int, device: Device, rand: Random):
        super().__init__()
        self.device = device
        self.rand = rand
        self.gridSize = gridSize
        self.pixelsUnit = 32
        self.minimap = MiniMap(self.gridSize, self)
        canvas = device.loadCanvas(
            Dimension(gridSize * self.pixelsUnit, gridSize * self.pixelsUnit))
        self.ground = Ground(canvas, self.pixelsUnit, self)
        self.onlineSystems: List[Subsystem] = []

    def initializeSystems(self) -> None:
        self.systemPosition = PositionSystem(self.ground.groundPositions)
        dimension = self.device.dimension
        self.systemRender = RenderSystem(self.pixelsUnit, self.device)
        self.addSystem(self.systemPosition)

    def createPlayer(self, position: Point) -> Entity:
        self.player = Entity(self)
        avatar = self.device.loadImage('Avatar - White.png', 'resources')
        positionComponent = self.systemPosition.addEntity(
            self.player, position)
        positionComponent.onMove = self.updatePlayerPosition
        self.systemRender.addEntity(self.player, avatar, position)
        self.updatePlayerPosition(Point(0, 0), position)
        return self.player

    def updatePlayerPosition(self, source: Point, dest: Point) -> None:
        positionComponent = self.player.getComponent(PositionComponent)
        renderComponent = self.player.getComponent(RenderComponent)
        renderComponent.position = positionComponent.position
        self.minimap.addPlayer(dest)
        self.listenerResetCamera()
        # TODO Update field of view
        # TODO Update ground
        # TODO Update mini map

    def randomMap(self) -> None:
        pass

    def redraw(self):
        self.device.clear()
        self.ground.canvas.draw(Point(0, 0))
        self.systemRender.update()
        if self.minimap.showing:
            self.minimap.canvas.drawAtScreen(self.minimap.position)
        self.device.reload()

    def registerListeners(self):
        listenUpdate = UpdateListener()
        listenUpdate.onUpdate = self.listenerOnlineSystems
        self.device.addListener(listenUpdate)

        listenNumeric = KeyboardListener(
            {'[1]', '[2]', '[3]', '[4]', '[5]', '[6]', '[7]', '[8]', '[9]'})
        listenNumeric.onKeyUp = self.listenerControlPlayer
        self.device.addListener(listenNumeric)

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

    def listenerControlPlayer(self, key: str) -> None:
        direction = None
        match key:
            case '[1]': direction = Direction.DOWN_LEFT
            case '[2]': direction = Direction.DOWN
            case '[3]': direction = Direction.DOWN_RIGHT
            case '[4]': direction = Direction.LEFT
            case '[5]': pass
            case '[6]': direction = Direction.RIGHT
            case '[7]': direction = Direction.UP_LEFT
            case '[8]': direction = Direction.UP
            case '[9]': direction = Direction.UP_RIGHT
        if direction is not None:
            self.player.getComponent(PositionComponent).move(direction)
            self.update()

    def listenerControlMinimap(self, key: str) -> None:
        if self.minimap.showing:
            if key == 'down':
                self.minimap.position = Point(
                    self.minimap.position.x, self.minimap.position.y+25)
            if key == 'up':
                self.minimap.position = Point(
                    self.minimap.position.x, self.minimap.position.y-25)
            if key == 'left':
                self.minimap.position = Point(
                    self.minimap.position.x-25, self.minimap.position.y)
            if key == 'right':
                self.minimap.position = Point(
                    self.minimap.position.x+25, self.minimap.position.y)
            self.redraw()

    def listenerShowMinimap(self, key: str) -> None:
        self.minimap.showing = not self.minimap.showing
        self.redraw()

    def listenerTranslateMap(self, source: Point, dest: Point) -> None:
        position = self.device.camera.position()
        diff = Point(dest.x - source.x, dest.y - source.y)
        position = Point(position.x - diff.x, position.y - diff.y)
        self.device.camera.translate(Point(position.x, position.y))
        self.redraw()

    def listenerResetCamera(self, key: str | None = None) -> None:
        center = self.player.getComponent(PositionComponent).position
        center = Point(center.x * self.pixelsUnit, center.y * self.pixelsUnit)
        self.device.camera.centralize(center)
        self.redraw()

    def listenerOnlineSystems(self):
        for system in self.onlineSystems:
            system.update()
