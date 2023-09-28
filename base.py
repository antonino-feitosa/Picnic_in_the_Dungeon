
from typing import Set
from typing import List
from typing import Tuple
from typing import Callable

from device import Font
from device import Image
from device import Device
from device import SpriteSheet
from device import TiledCanvas

from algorithms import Set
from algorithms import Dict
from algorithms import Point
from algorithms import Random
from algorithms import Overlap
from algorithms import Direction
from algorithms import Dimension
from algorithms import RandomWalk

from algorithms import CARDINALS
from algorithms import DIRECTIONS
from algorithms import distanceManhattan


class Loader:

    AvatarWhiteSprites:Dict[Tuple[str, Direction],str] = {
        ('idle', Direction.UP): 'White - Idle - Up.png',
        ('idle', Direction.DOWN): 'White - Idle - Down.png',
        ('idle', Direction.LEFT): 'White - Idle - Left.png',
        ('idle', Direction.RIGHT): 'White - Idle - Right.png',
        ('idle', Direction.UP_LEFT): 'White - Idle - Up - Left.png',
        ('idle', Direction.UP_RIGHT): 'White - Idle - Up - Right.png',
        ('idle', Direction.DOWN_LEFT): 'White - Idle - Down - Left.png',
        ('idle', Direction.DOWN_RIGHT): 'White - Idle - Down - Right.png',
        ('walk', Direction.UP): 'White - Walk - Up.png',
        ('walk', Direction.DOWN): 'White - Walk - Down.png',
        ('walk', Direction.LEFT): 'White - Walk - Left.png',
        ('walk', Direction.RIGHT): 'White - Walk - Right.png',
        ('walk', Direction.UP_LEFT): 'White - Walk - Up - Left.png',
        ('walk', Direction.UP_RIGHT): 'White - Walk - Up - Right.png',
        ('walk', Direction.DOWN_LEFT): 'White - Walk - Down - Left.png',
        ('walk', Direction.DOWN_RIGHT): 'White - Walk - Down - Right.png',
        ('collision', Direction.UP): 'White - Collision - Up.png',
        ('collision', Direction.DOWN): 'White - Collision - Down.png',
        ('collision', Direction.LEFT): 'White - Collision - Left.png',
        ('collision', Direction.RIGHT): 'White - Collision - Right.png',
        ('collision', Direction.UP_LEFT): 'White - Collision - Up - Left.png',
        ('collision', Direction.UP_RIGHT): 'White - Collision - Up - Right.png',
        ('collision', Direction.DOWN_LEFT): 'White - Collision - Down - Left.png',
        ('collision', Direction.DOWN_RIGHT): 'White - Collision - Down - Right.png',
    }

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
        self.avatarSprites: Dict[Tuple[str,Direction],SpriteSheet] = dict()
        self.messageBackground: Image
        self.textFont: Font
        self.descriptionBackground:Image
        self.iconPass:Image
        self.iconMove:Image
        self.iconAttack:Image
        self.iconDefend:Image
        self.iconAlert:Image
        self.iconEnvironment:Image
        self.iconConfig:Image
        self.iconBag:Image
        self.iconSelectedPass:Image
        self.iconSelectedMove:Image
        self.iconSelectedAttack:Image
        self.iconSelectedDefend:Image
        self.iconSelectedAlert:Image
        self.iconSelectedEnvironment:Image
        self.iconSelectedConfig:Image
        self.iconSelectedBag:Image
        self.selectedUnit:SpriteSheet
        self.selectedPath:SpriteSheet

    def load(self) -> None:
        self.messageBackground = self.loadImage('Message - Background.png')
        self.textFont = self.loadFont('gomarice_no_continue.ttf')
        self.selectedUnit = self.loadSheet('Selected Place.png', self.pixelsUnit)
        self.selectedPath = self.loadSheet('Path.png', self.pixelsUnit)

        self.groundSheet = self.loadSheet('Tileset - Ground.png', self.pixelsUnit)
        self.wallSheet = self.loadSheet('Tileset - Walls.png', self.pixelsUnit)
        self.minimapGroundSheet = self.loadSheet(
            'Tileset - MiniMap - Ground.png', self.pixelsUnitMinimap
        )
        self.minimapWallSheet = self.loadSheet(
            'Tileset - MiniMap - Walls.png', self.pixelsUnitMinimap
        )
        self.minimapPlayer = self.loadImage('Tileset - MiniMap - Avatar.png')
        self.minimapReference = self.loadImage('Tileset - MiniMap - Reference.png')
        self.avatar = self.loadImage('Avatar - White.png')
        self.avatarIdleRight = self.loadSheet(
            'Avatar - White - Idle - Right.png', self.pixelsUnit
        )

        self.descriptionBackground = self.loadImage('Icons/Description - Background.png')
        self.iconPass = self.loadImage('Icons/Pass.png')
        self.iconBag = self.loadImage('Icons/Bag.png')
        self.iconMove = self.loadImage('Icons/Move.png')
        self.iconAttack = self.loadImage('Icons/Attack.png')
        self.iconDefend = self.loadImage('Icons/Defend.png')
        self.iconAlert = self.loadImage('Icons/Alert.png')
        self.iconEnvironment = self.loadImage('Icons/Environment.png')
        self.iconConfig = self.loadImage('Icons/Config.png')

        self.iconSelectedPass = self.loadImage('Icons/Pass - Selected.png')
        self.iconSelectedBag = self.loadImage('Icons/Bag - Selected.png')
        self.iconSelectedMove = self.loadImage('Icons/Move - Selected.png')
        self.iconSelectedAttack = self.loadImage('Icons/Attack - Selected.png')
        self.iconSelectedDefend = self.loadImage('Icons/Defend - Selected.png')
        self.iconSelectedAlert = self.loadImage('Icons/Alert - Selected.png')
        self.iconSelectedEnvironment = self.loadImage('Icons/Environment - Selected.png')
        self.iconSelectedConfig = self.loadImage('Icons/Config - Selected.png')

        for (entry,path) in Loader.AvatarWhiteSprites.items():
            self.avatarSprites[entry] = self.loadSheet('Avatar/' + path, self.pixelsUnit)

    def loadSheet(self, name: str, unit: Dimension) -> SpriteSheet:
        return self.device.loadSpriteSheet(name, unit, 'resources')

    def loadImage(self, name: str) -> Image:
        return self.device.loadImage(name, 'resources')
    
    def loadFont(self, name: str) -> Font:
        return self.device.loadFont(name, 16, 'resources/Fonts')

    def loadGroundCanvas(self, dimension: Dimension) -> TiledCanvas:
        return self.device.loadTiledCanvas(self.pixelsUnit, dimension)

    def loadMinimapCanvas(self, dimension: Dimension) -> TiledCanvas:
        return self.device.loadTiledCanvas(self.pixelsUnitMinimap, dimension)


class Message:
    def __init__(self, loader:Loader):
        self.loader = loader
        self.background:Image = loader.messageBackground # 650 x 250
        self.currentMessage = 0
        w, h = self.loader.device.dimension
        self._messages: List[str] = ['']
        self._backgroundPosition = Point((w - 610)//2, h - 210)
        self._currentImage: Image
    
    def setMessages(self, messages: List[str] = ['']) -> None:
        self._messages = messages
        self._setMessage(0)
    
    def _setMessage(self, index:int) -> None:
        self._currentImage = self.background.clone()
        font = self.loader.textFont
        font.drawAtImage(self._messages[index], self._currentImage, Point(30,30))

    def nextMessage(self) -> None:
        if self.currentMessage < len(self._messages):
            self.currentMessage += 1
            self._setMessage(self.currentMessage)
    
    def previousMessage(self) -> None:
        if self.currentMessage > 0:
            self.currentMessage -= 1
            self._setMessage(self.currentMessage)

    def draw(self) -> None:
        self._currentImage.drawAtScreen(self._backgroundPosition)


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

