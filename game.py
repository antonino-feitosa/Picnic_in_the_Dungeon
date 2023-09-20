
import math

from typing import Set
from typing import Tuple

from device import Image
from device import Device
from device import SpriteSheet
from device import TiledCanvas
from device import UpdateListener
from device import KeyboardListener
from device import MouseDragListener

from algorithms import Set
from algorithms import Dict
from algorithms import List
from algorithms import Point
from algorithms import Random
from algorithms import Overlap
from algorithms import Dimension
from algorithms import Direction
from algorithms import RandomWalk
from algorithms import Composition

from algorithms import CARDINALS
from algorithms import DIRECTIONS
from algorithms import distanceManhattan
from algorithms import fieldOfViewRayCasting


class Loader:
    def __init__(
        self, device: Device, pixelsUnit: Dimension, pixelsUnitMinimap: Dimension
    ):
        self.device = device
        self.pixelsUnit = pixelsUnit
        self.pixelsUnitMinimap = pixelsUnitMinimap
        self.groundSheet: SpriteSheet
        self.wallSheet: SpriteSheet
        self.minimapGroundSheet: SpriteSheet
        self.minimapWallSheet: SpriteSheet
        self.minimapPlayer: Image
        self.minimapReference: Image
        self.avatar: Image
        self.avatarIdleRight: SpriteSheet

    def load(self) -> None:
        self.groundSheet = self.loadSheet("Tileset - Ground.png", self.pixelsUnit)
        self.wallSheet = self.loadSheet("Tileset - Walls.png", self.pixelsUnit)
        self.minimapGroundSheet = self.loadSheet(
            "Tileset - MiniMap - Ground.png", self.pixelsUnitMinimap
        )
        self.minimapWallSheet = self.loadSheet(
            "Tileset - MiniMap - Walls.png", self.pixelsUnitMinimap
        )
        self.minimapPlayer = self.loadImage("Tileset - MiniMap - Avatar.png")
        self.minimapReference = self.loadImage("Tileset - MiniMap - Reference.png")
        self.avatar = self.loadImage("Avatar - White.png")
        self.avatarIdleRight = self.loadSheet("Avatar - White - Idle - Right.png", self.pixelsUnit)

    def loadSheet(self, name: str, unit: Dimension) -> SpriteSheet:
        return self.device.loadSpriteSheet(name, unit, "resources")

    def loadImage(self, name: str) -> Image:
        return self.device.loadImage(name, "resources")

    def loadGroundCanvas(self, dimension: Dimension) -> TiledCanvas:
        return self.device.loadTiledCanvas(self.pixelsUnit, dimension)

    def loadMinimapCanvas(self, dimension: Dimension) -> TiledCanvas:
        return self.device.loadTiledCanvas(self.pixelsUnitMinimap, dimension)


class Map:
    def __init__(self, dimension: Dimension, rand: Random):
        self.rand = rand
        self.dimension = dimension
        self.endPoint: Point = Point(0, 0)
        self.startPoint: Point = Point(0, 0)
        self.groundPositions: Set[Point] = set()
        self.wallPositions: Set[Point] = set()
        self.groundToWalls: Dict[Point, Set[Point]] = dict()
        self.wallToGround: Dict[Point, Set[Point]] = dict()

    def getWallsForGround(self, ground: Point) -> Set[Point]:
        return self.groundToWalls[ground]

    def getWallsForArea(self, ground: Set[Point]) -> Set[Point]:
        area = set()
        for pos in ground:
            area.update(self.groundToWalls[pos])
        border = set()
        for wall in area:
            if len(self._neighborhood(wall, self.groundPositions)) == len(
                self.wallToGround[wall]
            ):
                border.add(wall)
        return border

    @staticmethod
    def _neighborhood(position: Point, ground: Set[Point]) -> Set[Point]:
        neigh = set()
        for dir in DIRECTIONS:
            pos = dir + position
            if pos in ground:
                neigh.add(pos)
        return neigh

    def calculateWalls(self) -> None:
        for pos in self.groundPositions:
            self.groundToWalls.setdefault(pos, set())
            for dir in DIRECTIONS:
                wall = pos + dir
                self.wallToGround.setdefault(wall, set())
                if wall not in self.groundPositions:
                    self.wallPositions.add(wall)
                    self.groundToWalls[pos].add(wall)
                    self.wallToGround[wall].add(pos)

    def makeIsland(self, iterations: int = 20) -> None:
        width, height = self.dimension
        steps = min((width - 1) // 2, (height - 1) // 2)  # -1 walls to border
        center = Point(width // 2, height // 2)
        self.startPoint = center
        self.endPoint = center
        distanceToEnd = 0
        walker = RandomWalk(steps, CARDINALS, self.rand)
        for _ in range(iterations):
            walk = walker.makeRandom(center)
            end = walker.lastPoint
            self.groundPositions.update(walk)
            distance = distanceManhattan(center, end)
            if distance > distanceToEnd:
                self.endPoint = end
                distance = distanceToEnd
        self.calculateWalls()

    def makeArchipelago(self, iterations: int = 20) -> None:
        pass

    def _removeDisconnectedParts(self) -> None:
        pass


class Background:
    def __init__(self, canvas: TiledCanvas, rand: Random):
        self.rand = rand
        self.canvas = canvas
        self.wallSheet: SpriteSheet
        self.groundSheet: SpriteSheet
        self.wallsPositions: Set[Point] = set()

    def draw(self, position: Point):
        self.canvas.draw(position)

    def drawAtScreen(self, position: Point):
        self.canvas.drawAtScreen(position)

    def addGround(self, ground: Set[Point]) -> None:
        dimension = self.canvas.dimension
        sheet = self.groundSheet
        for position in ground:
            if position in dimension:
                image = self.rand.choice(sheet.images)
                self.clearPositions({position})
                self.canvas.drawAtCanvas(image, position)

    def addWall(self, wall: Set[Point]) -> None:
        for position in wall:
            self.updateWall(position)
            for dir in DIRECTIONS:
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

    def clearPositions(self, positions: Set[Point]) -> None:
        for position in positions:
            self.canvas.clear(position)

    def shadowPositions(self, positions: Set[Point]) -> None:
        for position in positions:
            self.canvas.shadow(position)

    def paintPosition(self, position: Point, image: Image) -> None:
        self.canvas.drawAtCanvas(image, position)

    @staticmethod
    def calculateWallIndexInSheet(point: Point, walls: Set[Point]) -> int:
        mask = 0
        for dir in CARDINALS:
            if dir + point in walls:
                mask += Overlap.fromDirection(dir).value
        return mask


class PositionSystem:
    def __init__(self, ground: Set[Point]):
        self.ground: Set[Point] = ground
        self.positionToComponent: Dict[Point, PositionComponent] = dict()
        self.toMove: Set[Tuple[PositionComponent, Direction]] = set()

    def update(self):  # TODO resolve dependencies
        for component, direction in self.toMove:
            destination = component.position + direction
            if destination not in self.ground:
                component.collided.append((None, destination))
            elif destination in self.positionToComponent:
                other = self.positionToComponent[destination].entity
                component.collided.append((other, destination))
            else:
                position = component.position
                self.positionToComponent.pop(position, None)
                self.positionToComponent[destination] = component
                component.position = destination
        self.toMove.clear()


class RenderSystem:
    def __init__(self, rand: Random, loader: Loader):
        self.map: Map
        self.ground: Background
        self.minimap: Background
        self.rand = rand
        self.loader = loader
        self.minimapPlayerImage: Image = loader.minimapPlayer
        self._center: Point = Point(0, 0)
        self._visible: Set[Point] = set()
        self.components: Set[RenderComponent] = set()
        self.minimapVisible: bool = False
        self.minimapPosition: Point = Point(0, 0)

    def draw(self):
        self.ground.draw(Point(0, 0))
        for comp in self.components:
            position = comp.entity[PositionComponent].position
            if position in self._visible:
                comp.draw()
        if self.minimapVisible:
            self.minimap.drawAtScreen(self.minimapPosition)

    def setMap(self, map: Map) -> None:
        self.map = map
        rand = self.rand
        loader = self.loader

        groundCanvas = loader.loadGroundCanvas(map.dimension)
        self.ground = Background(groundCanvas, rand)
        self.ground.groundSheet = loader.groundSheet
        self.ground.wallSheet = loader.wallSheet

        minimapCanvas = loader.loadMinimapCanvas(map.dimension)
        self.minimap = Background(minimapCanvas, rand)
        self.minimap.groundSheet = loader.minimapGroundSheet
        self.minimap.wallSheet = loader.minimapWallSheet

    def setView(self, center: Point, visible: Set[Point]) -> None:
        self.ground.addGround(visible)
        self.minimap.addGround(visible)
        walls = self.map.getWallsForArea(visible)
        self.ground.addWall(walls)
        self.minimap.addWall(walls)
        self.minimap.paintPosition(center, self.minimapPlayerImage)
        self._visible = visible
        self._center = center
        self.resetMinimapPosition()

    def update(self, center: Point, visible: Set[Point]) -> None:
        included = visible.difference(self._visible)
        removed = self._visible.difference(visible)
        walls = self.map.getWallsForArea(visible)
        self.ground.shadowPositions(removed)
        self.ground.addGround(included)
        self.ground.addWall(walls)
        self.minimap.addGround(included)
        self.minimap.addWall(walls)
        self.minimap.clearPositions({self._center})
        self.minimap.addGround({self._center})
        self.minimap.paintPosition(center, self.minimapPlayerImage)
        self._visible = visible
        self._center = center
        self.resetMinimapPosition()

    def resetMinimapPosition(self) -> None:
        w, h = self.minimap.canvas.pixelsUnit
        x, y = self._center
        self.minimapPosition = Point(100 - x * w, 100 - y * h)


class AnimationSystem:
    def __init__(self):
        self.visible: Set[Point] = set()
        self.components: Set[AnimationComponent] = set()
    
    def update(self):
        for component in self.components:
            position = component.entity[PositionComponent].position
            if position in self.visible:
                component.update()
    

class FieldOfViewSystem:
    def __init__(self, game: 'RogueLike', enableFOV: bool):
        self.enableFOV = enableFOV
        self.game = game

    def update(self, component: 'FieldOfViewComponent') -> None:
        if self.enableFOV:
            radius = component.radius
            center = component.entity[PositionComponent].position
            ground = self.game.map.groundPositions
            component.visible = fieldOfViewRayCasting(center, radius, ground)
        else:
            component.visible = self.game.map.groundPositions

class CameraSystem:
    def __init__(self, game: 'RogueLike'):
        self.game = game
        self.offset: Point = Point(0,0)
        self.countShake = 0
        self.magnitude = 0
        self.active:CameraComponent
    
    def focus(self, component: 'CameraComponent') -> None:
        self.active = component
        self.centralize()
    
    def centralize(self):
        x, y = self.active.entity[PositionComponent].position
        ux, uy = self.game.pixelsUnit
        offx, offy = self.offset
        self.game.device.camera.centralize(Point(x * ux + offx, y * uy + offy))
    
    def shake(self, ticks:int, magnitude = 3) -> None:
        self.countShake = ticks
        self.magnitude = magnitude
        self._applyShake()
    
    def _applyShake(self) -> None:
        dx = self.game.rand.nextNormal(0, self.magnitude)
        dy = self.game.rand.nextNormal(0, self.magnitude)
        self.offset = Point(math.ceil(dx), math.ceil(dy))
    
    def update(self) -> None:
        if self.countShake > 0:
            self._applyShake()
            self.centralize()
            self.countShake -= 1
        else:
            self.offset = Point(0,0)
            self.centralize()


class ControlSystem:
    def __init__(self, game: 'RogueLike'):
        self.game = game
        self.minimapOffset = 25
        device = self.game.device

        listenNumeric = KeyboardListener(
            {"[1]", "[2]", "[3]", "[4]", "[5]", "[6]", "[7]", "[8]", "[9]"}
        )
        listenNumeric.onKeyUp = self.listenerControlPlayer
        device.addListener(listenNumeric)

        listenSpace = KeyboardListener({"space"})
        listenSpace.onKeyUp = self.listenerResetCamera
        device.addListener(listenSpace)

        listenTab = KeyboardListener({"tab"})
        listenTab.onKeyUp = self.listenerShowMinimap
        device.addListener(listenTab)

        listenControls = KeyboardListener({"up", "left", "down", "right"})
        listenControls.onKeyUp = self.listenerControlMinimap
        device.addListener(listenControls)

        listenDrag = MouseDragListener()
        listenDrag.onMouseDrag = self.listenerTranslateMap
        device.addListener(listenDrag)

    def listenerControlPlayer(self, key: str) -> None:
        direction = None
        match key:
            case "[1]":
                direction = Direction.DOWN_LEFT
            case "[2]":
                direction = Direction.DOWN
            case "[3]":
                direction = Direction.DOWN_RIGHT
            case "[4]":
                direction = Direction.LEFT
            case "[5]":
                pass
            case "[6]":
                direction = Direction.RIGHT
            case "[7]":
                direction = Direction.UP_LEFT
            case "[8]":
                direction = Direction.UP
            case "[9]":
                direction = Direction.UP_RIGHT
        if direction is not None:
            self.game.player[PositionComponent].move(direction)
            self.game.update()

    def listenerControlMinimap(self, key: str) -> None:
        visible = self.game.renderSystem.minimapVisible
        if visible:
            off = self.minimapOffset
            position = self.game.renderSystem.minimapPosition
            if key == "down":
                position = Point(position.x, position.y + off)
            if key == "up":
                position = Point(position.x, position.y - off)
            if key == "left":
                position = Point(position.x - off, position.y)
            if key == "right":
                position = Point(position.x + off, position.y)
            self.game.renderSystem.minimapPosition = position
            self.game.draw()

    def listenerShowMinimap(self, key: str) -> None:
        visible = self.game.renderSystem.minimapVisible
        self.game.renderSystem.minimapVisible = not visible
        self.game.renderSystem.resetMinimapPosition()
        self.game.draw()

    def listenerTranslateMap(self, source: Point, dest: Point) -> None:
        position = self.game.device.camera.translate
        diff = Point(dest.x - source.x, dest.y - source.y)
        position = Point(position.x - diff.x, position.y - diff.y)
        self.game.device.camera.translate = position
        self.game.draw()

    def listenerResetCamera(self, key: str | None = None) -> None:
        self.game.cameraSystem.centralize()
        self.game.renderSystem.resetMinimapPosition()
        self.game.draw()


class RogueLike:
    def __init__(self, seed: int = 0, enableFOV = True):
        self.rand = Random(seed)
        self.device = Device("Picnic in the Dungeon", tick = 16)
        self.pixelsUnit = Dimension(32, 32)
        self.pixelsUnitMinimap = Dimension(4, 4)
        self.loader = Loader(self.device, self.pixelsUnit, self.pixelsUnitMinimap)
        self.loader.load()
        self.map = self.createStartMap()

        self.renderSystem = RenderSystem(self.rand, self.loader)
        self.positionSystem = PositionSystem(self.map.groundPositions)
        self.fieldOfViewSystem = FieldOfViewSystem(self, enableFOV)
        self.controlSystem = ControlSystem(self)
        self.animationSystem = AnimationSystem()
        self.cameraSystem = CameraSystem(self)

        self.player: Composition = self.createPlayer()
        self.player[CameraComponent].focus()
        self.player[FieldOfViewComponent].update()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self.renderSystem.setMap(self.map)
        self.renderSystem.setView(position, visible)
        self.animationSystem.visible = visible

    def createStartMap(self) -> Map:
        dimension = Dimension(200, 200)
        startMap = Map(dimension, self.rand)
        startMap.makeIsland()
        return startMap

    def createPlayer(self) -> Composition:
        player = Composition()
        player.add(RenderComponent(self, player, self.loader.avatar))
        player.add(PositionComponent(self, player, self.map.startPoint))
        player.add(FieldOfViewComponent(self, player, 6))
        player.add(AnimationComponent(player[RenderComponent], self.loader.avatarIdleRight, 1))
        player.add(CameraComponent(self, player))
        return player

    def update(self) -> None:
        self.positionSystem.update()
        self.player[FieldOfViewComponent].update()
        self.player[CameraComponent].focus()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self.animationSystem.visible = visible
        self.renderSystem.update(position, visible)
        self.draw()

    def draw(self) -> None:
        self.device.clear()
        self.cameraSystem.update()
        self.renderSystem.draw()
        self.device.reload()
    
    def isRunning(self) -> bool:
        return self.device.running

    def loop(self) -> None:
        self.animationSystem.update()
        self.device.update()
        self.draw()


class RenderComponent:
    def __init__(self, game: RogueLike, entity: Composition, image: Image):
        self.game = game
        self.image = image
        self.entity = entity
        self.offset:Point = Point(0,0)
        game.renderSystem.components.add(self)

    def draw(self):
        width, height = self.entity[PositionComponent].position
        uw, uh = self.game.pixelsUnit
        dx, dy = self.offset
        position = Point(width * uw + dx, height * uh + dy)
        self.image.draw(position)

    def destroy(self):
        self.game.renderSystem.components.remove(self)


class PositionComponent:
    def __init__(self, game: RogueLike, entity: Composition, position: Point):
        self.game = game
        self.entity = entity
        self.position: Point = position
        self.collided: List[Tuple[Composition | None, Point]] = []
        self.game.positionSystem.positionToComponent[position] = self

    def move(self, direction: Direction) -> None:
        self.game.positionSystem.toMove.add((self, direction))


class FieldOfViewComponent:
    def __init__(self, game: RogueLike, entity: Composition, radius: int):
        self.game = game
        self.radius = radius
        self.entity = entity
        self.visible: Set[Point] = set()

    def update(self):
        self.game.fieldOfViewSystem.update(self)


class AnimationComponent:
    def __init__(self, render:RenderComponent, animation: SpriteSheet, tick:int):
        self.tick = tick
        self.loop = True
        self._tickCount = 0
        self._frameIndex = 0
        self.render = render
        self.game = render.game
        self.animation = animation
        self.entity = render.entity
        self.game.animationSystem.components.add(self)
    
    def reload(self):
        self._tickCount = 0
        self._frameIndex = 0
    
    def update(self):
        if self._tickCount >= self.tick:
            self._tickCount = 0
            self.render.image = self.animation.images[self._frameIndex]
            length = len(self.animation.images)
            if self._frameIndex + 1 < length:
                self._frameIndex += 1
            else:
                if self.loop:
                    self._frameIndex = 0
        else:
            self._tickCount += 1


class CameraComponent:
    def __init__(self, game: RogueLike, entity: Composition):
        self.game = game
        self.entity = entity
        self.delay = 0
    
    def focus(self) -> None:
        self.game.cameraSystem.focus(self)

    def shake(self, ticks:int, magnitude = 3) -> None:
        self.game.cameraSystem.shake(ticks, magnitude)
