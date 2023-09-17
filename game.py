
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
    def __init__(self, device:Device, pixelsUnit: Dimension, pixelsUnitMinimap: Dimension):
        self.device = device
        self.pixelsUnit = pixelsUnit
        self.pixelsUnitMinimap = pixelsUnitMinimap
        self.groundSheet:SpriteSheet
        self.wallSheet:SpriteSheet
        self.minimapGroundSheet: SpriteSheet
        self.minimapWallSheet: SpriteSheet
        self.minimapPlayer: Image
        self.minimapReference: Image
        self.avatar: Image

    def load(self) -> None:
        self.groundSheet = self.loadSheet('Tileset - Ground.png', self.pixelsUnit)
        self.wallSheet = self.loadSheet('Tileset - Walls.png', self.pixelsUnit)
        self.minimapGroundSheet = self.loadSheet('Tileset - MiniMap - Ground.png', self.pixelsUnitMinimap)
        self.minimapWallSheet = self.loadSheet('Tileset - MiniMap - Walls.png', self.pixelsUnitMinimap)
        self.minimapPlayer = self.loadImage('Tileset - MiniMap - Avatar.png')
        self.minimapReference = self.loadImage('Tileset - MiniMap - Reference.png')
        self.avatar = self.loadImage('Avatar - White.png')
    
    def loadSheet(self, name:str, unit:Dimension) -> SpriteSheet:
        return self.device.loadSpriteSheet(name, unit, 'resources')
    
    def loadImage(self, name:str) -> Image:
        return self.device.loadImage(name,'resources')

    def loadGroundCanvas(self, dimension:Dimension) -> TiledCanvas:
        return self.device.loadTiledCanvas(self.pixelsUnit, dimension)

    def loadMinimapCanvas(self, dimension:Dimension) -> TiledCanvas:
        return self.device.loadTiledCanvas(self.pixelsUnitMinimap, dimension)


class Map:
    def __init__ (self, dimension:Dimension, rand:Random):
        self.rand = rand
        self.dimension = dimension
        self.endPoint:Point = Point(0,0)
        self.startPoint:Point = Point(0,0)
        self.groundPositions:Set[Point] = set()
        self.wallPositions:Set[Point] = set()
        self.groundToWalls:Dict[Point,Set[Point]] = dict()
        self.wallToGround:Dict[Point,Set[Point]] = dict()
    
    def getWallsForGround(self, ground:Point) -> Set[Point]:
        return self.groundToWalls[ground]

    def getWallsForArea(self, ground:Set[Point]) -> Set[Point]:
        area = set()
        for pos in ground:
            area.update(self.groundToWalls[pos])
        border = set()
        for wall in area:
            if len(self._neighborhood(wall, self.groundPositions)) == len(self.wallToGround[wall]):
                border.add(wall)
        return border
    
    @staticmethod
    def _neighborhood(position:Point, ground:Set[Point]) -> Set[Point]:
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
    
    def makeIsland(self, iterations:int = 20) -> None:
        width, height = self.dimension
        steps = min(width - 1, height - 1) # -1 border to walls
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
    def __init__(self, canvas: TiledCanvas, rand:Random):
        self.rand = rand
        self.canvas = canvas
        self.wallSheet: SpriteSheet
        self.groundSheet: SpriteSheet
        self.wallsPositions: Set[Point] = set()
    
    def draw(self, position:Point):
        self.canvas.draw(position)

    def drawAtScreen(self, position:Point):
        self.canvas.drawAtScreen(position)

    def addGround(self, ground : Set[Point]) -> None:
        dimension = self.canvas.dimension
        sheet = self.groundSheet
        for position in ground:
            if position in dimension:
                image = self.rand.choice(sheet.images)
                self.clearPositions({position})
                self.canvas.drawAtCanvas(image, position)

    def addWall(self, wall : Set[Point]) -> None:
        for position in wall:
            self.updateWall(position)
            for dir in DIRECTIONS:
                neigh = position + dir
                if neigh in self.wallsPositions:
                    self.updateWall(neigh)
    
    def updateWall(self, position : Point) -> None:
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
    
    def paintPosition(self, position:Point, image: Image) -> None:
        self.canvas.drawAtCanvas(image, position)

    @staticmethod
    def calculateWallIndexInSheet(point: Point, walls: Set[Point]) -> int:
        mask = 0
        for dir in CARDINALS:
            if dir + point in walls:
                mask += Overlap.fromDirection(dir).value
        return mask


class PositionSystem:
    def __init__(self, ground:Set[Point]):
        self.ground:Set[Point] = ground
        self.positionToComponent: Dict[Point,PositionComponent] = dict()
        self.toMove: Set[Tuple[PositionComponent,Direction]] = set()
    
    def update(self): # TODO resolve dependencies
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
    def __init__(self, rand:Random, loader:Loader):
        self.map:Map
        self.ground: Background
        self.minimap: Background
        self.rand = rand
        self.loader = loader
        self.minimapPlayerImage:Image = loader.minimapPlayer
        self._center:Point = Point(0,0)
        self._visible: Set[Point] = set()
        self.components: Set[RenderComponent] = set()
        self.minimapVisible:bool = False
        self.minimapPosition:Point = Point(0,0)
    
    def draw(self):
        self.ground.draw(Point(0,0))
        for comp in self.components:
            comp.draw()
        if self.minimapVisible:
            self.minimap.drawAtScreen(self.minimapPosition)

    def setMap(self, map:Map) -> None:
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


    def setView(self, center:Point, visible:Set[Point]) -> None:
        self.ground.addGround(visible)
        self.minimap.addGround(visible)
        walls = self.map.getWallsForArea(visible)
        self.ground.addWall(walls)
        self.minimap.addWall(walls)
        self.minimap.paintPosition(center, self.minimapPlayerImage)
        self._visible = visible
        self._center = center
        self.resetMinimapPosition()

    def update(self, center:Point, visible:Set[Point]) -> None:
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
    
    def resetMinimapPosition(self)->None:
        w, h = self.minimap.canvas.pixelsUnit
        x, y = self._center
        self.minimapPosition = Point(100 - x * w, 100 - y * h)

class FieldOfViewSystem:
    def __init__(self, game:'RogueLike', visible:bool):
        self.visible = visible
        self.game = game
    
    def update(self, component:'FieldOfViewComponent') -> None:
        if self.visible:
            component.visible = self.game.map.groundPositions
        else:
            radius = component.radius
            center = component.entity[PositionComponent].position
            ground = self.game.map.groundPositions
            component.visible = fieldOfViewRayCasting(center, radius, ground)


class ControlSystem:
    def __init__(self, game:'RogueLike'):
        self.game = game
        self.minimapOffset = 25
        device = self.game.device

        listenNumeric = KeyboardListener({'[1]', '[2]', '[3]', '[4]', '[5]', '[6]', '[7]', '[8]', '[9]'})
        listenNumeric.onKeyUp = self.listenerControlPlayer
        device.addListener(listenNumeric)

        listenSpace = KeyboardListener({'space'})
        listenSpace.onKeyUp = self.listenerResetCamera
        device.addListener(listenSpace)

        listenTab = KeyboardListener({'tab'})
        listenTab.onKeyUp = self.listenerShowMinimap
        device.addListener(listenTab)

        listenControls = KeyboardListener({'up', 'left', 'down', 'right'})
        listenControls.onKeyUp = self.listenerControlMinimap
        device.addListener(listenControls)

        listenDrag = MouseDragListener()
        listenDrag.onMouseDrag = self.listenerTranslateMap
        device.addListener(listenDrag)

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
            self.game.player[PositionComponent].move(direction)
            self.game.update()

    def listenerControlMinimap(self, key: str) -> None:
        visible = self.game.renderSystem.minimapVisible
        if visible:
            off = self.minimapOffset
            position = self.game.renderSystem.minimapPosition
            if key == 'down': position = Point(position.x, position.y+off)
            if key == 'up': position = Point(position.x, position.y-off)
            if key == 'left': position = Point(position.x-off, position.y)
            if key == 'right': position = Point(position.x+off, position.y)
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
        self.game.centralizeCamera()
        self.game.renderSystem.resetMinimapPosition()
        self.game.draw()


class RogueLike:
    def __init__(self):
        self.rand = Random(0)
        self.device = Device('Picnic in the Dungeon')
        self.pixelsUnit = Dimension(32,32)
        self.pixelsUnitMinimap = Dimension(4,4)
        self.loader = Loader(self.device, self.pixelsUnit, self.pixelsUnitMinimap)
        self.loader.load()
        self.map = self.createStartMap()
        
        self.renderSystem: RenderSystem = RenderSystem(self.rand, self.loader)
        self.positionSystem: PositionSystem = PositionSystem(self.map.groundPositions)
        self.fieldOfViewSystem: FieldOfViewSystem = FieldOfViewSystem(self, False)
        self.controlSystem = ControlSystem(self)

        self.player: Composition = self.createPlayer()
        self.player[FieldOfViewComponent].update()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self.renderSystem.setMap(self.map)
        self.renderSystem.setView(position, visible)
        self.centralizeCamera()

    def createStartMap(self) -> Map:
        dimension = Dimension(200,200)
        startMap = Map(dimension, self.rand)
        startMap.makeIsland()
        return startMap
    
    def createPlayer(self) -> Composition:
        player = Composition()
        player.add(RenderComponent(self, player, self.loader.avatar))
        player.add(PositionComponent(self, player, self.map.startPoint))
        player.add(FieldOfViewComponent(self, player, 6))
        return player
    
    def centralizeCamera(self) -> None:
        x, y = self.player[PositionComponent].position
        ux, uy = self.pixelsUnit
        self.device.camera.centralize(Point(x * ux, y * uy))

    def update(self):
        self.positionSystem.update()
        self.player[FieldOfViewComponent].update()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self.centralizeCamera()
        self.renderSystem.update(position, visible)
        self.draw()

    def draw(self):
        self.device.clear()
        self.renderSystem.draw()
        self.device.reload()


class RenderComponent:
    def __init__(self, game:RogueLike, entity:Composition, image:Image):
        self.game = game
        self.image = image
        self.entity = entity
        game.renderSystem.components.add(self)
    
    def draw(self):
        width, height = self.entity[PositionComponent].position
        unit = self.game.pixelsUnit
        self.image.draw(Point(width * unit.width, height * unit.height))
    
    def destroy(self):
        self.game.renderSystem.components.remove(self)


class PositionComponent:
    def __init__(self, game:RogueLike, entity:Composition, position:Point):
        self.game = game
        self.entity = entity
        self.position:Point = position
        self.collided: List[Tuple[Composition|None,Point]] = []
        self.game.positionSystem.positionToComponent[position] = self
    
    def move(self, direction:Direction) -> None:
        self.game.positionSystem.toMove.add((self, direction))


class FieldOfViewComponent:
    def __init__(self, game:RogueLike, entity:Composition, radius:int):
        self.game = game
        self.radius = radius
        self.entity = entity
        self.visible: Set[Point] = set()
    
    def update(self):
        self.game.fieldOfViewSystem.update(self)
