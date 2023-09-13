
from typing import Set
from typing import Dict
from typing import List
from typing import Tuple
from typing import Callable

from game import Game
from game import Entity
from game import Component
from game import Subsystem

from device import Image
from device import Canvas
from device import Device
from device import Rectangle
from device import SpriteSheet
from device import UpdateListener
from device import KeyboardListener
from device import MouseDragListener

from algorithms import Random
from algorithms import Overlap
from algorithms import Direction
from algorithms import ApplicationError


class RenderComponent(Component):
    def __init__(self, system: 'RenderSystem', entity: 'Entity', image: Image):
        super().__init__(system, entity)
        self.image = image
        self.position: Tuple[int, int] = (0, 0)


class RenderSystem(Subsystem[RenderComponent]):
    def __init__(self, viewPort: Rectangle, game: 'RogueLike'):
        super().__init__()
        self.game = game
        self.viewPort = viewPort

    def addEntity(self, entity: Entity, image: Image, position: Tuple[int, int]) -> 'RenderComponent':
        component = RenderComponent(self, entity, image)
        component.position = position
        entity.addComponent(component)
        self.addComponent(component)
        return component

    def moveViewport(self, direction: Direction) -> None:
        origin = direction.next(self.viewPort.position)
        dimension = direction.next(self.viewPort.endPosition)
        self.viewPort = Rectangle(
            origin[0], origin[1], dimension[0], dimension[1])

    def update(self):
        pixelsUnit = self.game.pixelsUnit
        for render in self.components:
            position = (render.position[0] * pixelsUnit,
                        render.position[1] * pixelsUnit)
            if self.viewPort.contains(position[0], position[1]):
                render.image.draw(position)


class PositionComponent(Component['PositionSystem']):
    def __init__(self, system: 'PositionSystem', entity: 'Entity', position: Tuple[int, int]):
        super().__init__(system, entity)
        self.position = position
        self.onCollision: Callable[[
            Tuple[int, int], Entity | None], None] = lambda position, entity: None
        self.onMove: Callable[[Tuple[int, int],
                               Tuple[int, int]], None] = lambda source, dest: None

    def move(self, direction: Direction) -> None:
        self.system.move(self, direction)


class PositionSystem(Subsystem[PositionComponent]):
    def __init__(self, ground: Set[Tuple[int, int]]):
        super().__init__()
        self.ground = ground
        self.positionToEntity: Dict[Tuple[int, int],
                                    PositionComponent] = dict()
        self.componentsToMove: List[Tuple[PositionComponent, Direction]] = []

    def addEntity(self, entity: Entity, position: Tuple[int, int]) -> PositionComponent:
        component = PositionComponent(self, entity, position)
        entity.addComponent(component)
        self.positionToEntity[position] = component
        self.addComponent(component)
        return component

    def move(self, component: PositionComponent, direction: Direction) -> None:
        self.componentsToMove.append((component, direction))

    def update(self):
        # TODO resolve dependencies
        for (component, direction) in self.componentsToMove:
            nextPosition = direction.next(component.position)
            if nextPosition not in self.ground:
                component.onCollision(nextPosition, None)
            elif nextPosition in self.positionToEntity:
                other = self.positionToEntity[nextPosition]
                component.onCollision(nextPosition, other.entity)
            else:
                oldPosition = component.position
                component.position = nextPosition
                self.positionToEntity.pop(oldPosition)
                self.positionToEntity[nextPosition] = component
                component.onMove(oldPosition, nextPosition)
        self.componentsToMove.clear()


class RogueLike(Game):
    def __init__(self, gridSize: int, device: Device, rand: Random):
        super().__init__()
        self.device = device
        self.rand = rand
        self.gridSize = gridSize
        self.pixelsUnit = 32
        self.minimap = MiniMap(self.gridSize, self)
        canvas = device.loadCanvas(
            (gridSize * self.pixelsUnit, gridSize * self.pixelsUnit))
        self.ground = Ground(canvas, self.pixelsUnit, self)
        self.onlineSystems: List[Subsystem] = []

    def initializeSystems(self) -> None:
        self.systemPosition = PositionSystem(self.ground.groundPositions)
        dimension = self.device.dimension
        self.systemRender = RenderSystem(
            Rectangle(0, 0, dimension[0], dimension[1]), self)
        self.addSystem(self.systemPosition)

    def createPlayer(self, position: Tuple[int, int]) -> Entity:
        self.player = Entity(self)
        avatar = self.device.loadImage('Avatar - White.png', 'resources')
        positionComponent = self.systemPosition.addEntity(
            self.player, position)
        positionComponent.onMove = self.updatePlayerPosition
        self.systemRender.addEntity(self.player, avatar, position)
        self.minimap.addPlayer(position)
        return self.player

    def updatePlayerPosition(self, source: Tuple[int, int], dest: Tuple[int, int]) -> None:
        positionComponent = self.player.getComponent(PositionComponent)
        renderComponent = self.player.getComponent(RenderComponent)
        renderComponent.position = positionComponent.position
        self.minimap.addPlayer(dest)
        position = self.device.camera.translateVector
        offset = (dest[0] - source[0], dest[1] - source[1])
        offset = (position[0] + offset[0]*self.pixelsUnit , position[1] + offset[1]*self.pixelsUnit)
        self.device.camera.translate(offset[0], offset[1])
        self.redraw()

    def randomMap(self) -> None:
        pass

    def redraw(self):
        self.device.clear()
        self.ground.canvas.draw((0, 0))
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
                self.minimap.position = (
                    self.minimap.position[0], self.minimap.position[1]+25)
            if key == 'up':
                self.minimap.position = (
                    self.minimap.position[0], self.minimap.position[1]-25)
            if key == 'left':
                self.minimap.position = (
                    self.minimap.position[0]-25, self.minimap.position[1])
            if key == 'right':
                self.minimap.position = (
                    self.minimap.position[0]+25, self.minimap.position[1])
            self.redraw()

    def listenerShowMinimap(self, key: str) -> None:
        self.minimap.showing = not self.minimap.showing
        self.redraw()

    def listenerTranslateMap(self, source: Tuple[int, int], dest: Tuple[int, int]) -> None:
        position = self.device.camera.position()
        diff = (dest[0] - source[0], dest[1] - source[1])
        position = (position[0] - diff[0], position[1] - diff[1])
        self.device.camera.translate(position[0], position[1])
        dimension = self.device.dimension
        self.systemRender.viewPort = Rectangle(
            position[0], position[1], position[0] + dimension[0], position[1] + dimension[1])
        self.redraw()

    def listenerResetCamera(self, key: str) -> None:
        self.device.camera.translate(0, 0)
        self.redraw()

    def listenerOnlineSystems(self):
        for system in self.onlineSystems:
            system.update()


class MiniMap:
    def __init__(self, gridSize: int, game: RogueLike):
        self.pixelsUnit = 4
        self.showing = False
        self.position: Tuple[int, int] = (100, 100)
        self.canvas = game.device.loadCanvas(
            (gridSize * self.pixelsUnit, gridSize * self.pixelsUnit))
        self.ground = Ground(self.canvas, self.pixelsUnit, game)
        self.ground.groundSheet = game.device.loadSpriteSheet(
            'Tileset - MiniMap - Ground.png', (self.pixelsUnit, self.pixelsUnit), 'resources')
        self.ground.wallSheet = game.device.loadSpriteSheet(
            'Tileset - MiniMap - Walls.png', (self.pixelsUnit, self.pixelsUnit), 'resources')
        self.playerImage = game.device.loadImage(
            'Tileset - MiniMap - Avatar.png', 'resources')
        self.referenceImage = game.device.loadImage(
            'Tileset - MiniMap - Reference.png', 'resources')
        self.playerPosition: Tuple[int, int] | None = None

    def addGround(self, position: Tuple[int, int]) -> None:
        self.ground.addGround(position)

    def addWall(self, position: Tuple[int, int]) -> None:
        self.ground.addWall(position)

    def addPlayer(self, position: Tuple[int, int]) -> None:
        if self.playerPosition is not None:
            self.clearGround(self.playerPosition)
        self.playerPosition = position
        position = (position[0] * self.pixelsUnit,
                    position[1] * self.pixelsUnit)
        self.ground.canvas.drawAtCanvas(self.playerImage, position)
    
    def addReference(self, position: Tuple[int, int]) -> None:
        position = (position[0] * self.pixelsUnit,
                    position[1] * self.pixelsUnit)
        self.ground.canvas.drawAtCanvas(self.referenceImage, position)

    def clearGround(self, position: Tuple[int, int]) -> None:
        oldPosition = (position[0] * self.pixelsUnit,
                       position[1] * self.pixelsUnit)
        self.ground.canvas.clearRegion(Rectangle(
            oldPosition[0], oldPosition[1], oldPosition[0]+self.pixelsUnit, oldPosition[1]+self.pixelsUnit))
        self.addGround(position)


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
        self.canvas.drawAtCanvas(image, (dx, dy))

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
