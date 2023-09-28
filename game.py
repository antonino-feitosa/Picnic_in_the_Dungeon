
from typing import List
from typing import Tuple
from typing import Callable

from base import Map
from base import Loader

from device import Image
from device import Device
from device import SpriteSheet
from device import KeyboardListener
from device import MouseDragListener
from device import MouseClickListener
from device import MouseMotionListener

from systems import PositionSystem
from systems import PositionComponent
from systems import MotionSystem
from systems import MotionComponent
from systems import RenderSystem
from systems import RenderComponent
from systems import AnimationSystem
from systems import AnimationComponent
from systems import FieldOfViewSystem
from systems import FieldOfViewComponent
from systems import CameraSystem
from systems import CameraComponent
from systems import AnimationControllerSystem
from systems import AnimationControllerComponent
from systems import MessageSystem
from systems import MessageComponent

from algorithms import Point
from algorithms import Random
from algorithms import Dimension
from algorithms import Direction
from algorithms import Composition
from algorithms import PathFinding
from algorithms import DIRECTIONS
from algorithms import distanceEuclidean
from algorithms import distanceSquare


class ControlComponent:
    def __init__(self, position:Point):
        self.radius = 12
        self.imageIdle: Image
        self.imageActive: Image
        self.tooptip: str
        self.processing: bool = False
        self.enabled:bool = True
    
    def clickScreen(self, position:Point) -> bool:
        return False

    def clickWorld(self, position:Point) -> bool:
        return False

    def mouseMove(self, position:Point) -> None:
        pass

    def update(self) -> None:
        pass





class MouseButton:
    def __init__(self, position:Point, image:Image):
        self.tooltip: str = ''
        self.image:Image = image
        self.position: Point = position
        self.action = None

class MouseControlSystem:
    def __init__(self, game: 'RogueLike'):
        self.game = game
        self.device = game.device
        self.hasClick:bool = False
        self.pathSize = 3
        self.position:Point = Point(0,0)
        self._hasSelectedUnit = False
        self._selectedUnitPosition:Point = Point(0,0)
        self._onMoveAction:bool = False
        self._pathEntity: List[Composition] = []
        self._pathDestination:List[Point] = []

        selectSheet = self.game.loader.selectedUnit
        self._entityControl = self._createAnimation(selectSheet)
        pathSheet = self.game.loader.selectedPath
        for _ in range(self.pathSize):
            self._pathEntity.append(self._createAnimation(pathSheet))
        self._pathFinding = PathFinding(game.map.groundPositions, DIRECTIONS)

        self.icons:List[Tuple[Image,Point,Callable[[],None]]] = []
        self._createIcons()
    
    def _createIcons(self):
        _, h = self.game.device.dimension
        loader = self.game.loader
        height = h - loader.descriptionBackground.dimension.height
        width = loader.descriptionBackground.dimension.width
        icons = [
            loader.iconMove,
            loader.iconPass,
            loader.iconAlert,
            loader.iconDefend,
            loader.iconAttack,
            loader.iconBag,
            loader.iconConfig,
            loader.iconEnvironment
        ]
        actions = [
            self._actionMove,
            lambda : print('Action Pass'),
            lambda : print('Action Alert'),
            lambda : print('Action Defend'),
            lambda : print('Action Attack'),
            lambda : print('Action Bag'),
            lambda : print('Action Config'),
            lambda : print('Action Environment')
        ]
        dx = width - 30 - 16
        for image, action in zip(icons, actions):
            self.icons.append((image, Point(dx, height), action))
            dx -= 30
        
    def update(self) -> None:
        if self.hasClick:
            if self._onMoveAction:
                self._actionMovePerform()
            else:

                acted = False
                for _, position, action in self.icons:
                    destination = Point(position.x + 12, position.y + 12)
                    if distanceEuclidean(destination, self.position) < 12:
                        action()
                        acted = True
                        break

                if not acted:
                    position = self.screenToWorldPoint(self.position)
                    if position in self.game[PositionSystem].positionToComponent:
                        self._selectedUnitPosition = position
                        if self._hasSelectedUnit:
                            self._entityControl[PositionComponent].position = position
                        else:
                            self._enableEntitySelect()
                        self._hasSelectedUnit = True
                    else:
                        self._hasSelectedUnit = False
        else:
            if self._onMoveAction:
                self._updateEntityPath()
        
        if not self._hasSelectedUnit:
            self._disableEntitySelect()
        self.hasClick = False
    
    def _disableEntitySelect(self):
        self._entityControl[RenderComponent].enabled = False
        self._entityControl[AnimationComponent].enabled = False

    def _enableEntitySelect(self):
        self._entityControl[PositionComponent].position = self._selectedUnitPosition
        self._entityControl[RenderComponent].enabled = True
        self._entityControl[AnimationComponent].enabled = True
    
    def _createAnimation(self, sheet: SpriteSheet) -> Composition:
        positionSystem = self.game[PositionSystem]
        renderSystem = self.game[RenderSystem]
        animationSystem = self.game[AnimationSystem]
        image = sheet.images[0]

        entity = Composition()
        position = PositionComponent(positionSystem, entity, Point(0,0))
        render = RenderComponent(renderSystem, entity, image)
        render.enabled = False
        animation = AnimationComponent(animationSystem, render, sheet)
        entity.add(position)
        entity.add(render)
        entity.add(animation)
        return entity


    def _updateEntityPath(self):
        for entity in self._pathEntity:
            entity[RenderComponent].enabled = False
            entity[AnimationComponent].enabled = False
        
        dest = self.screenToWorldPoint(self.position)
        source = self._selectedUnitPosition
        distance = distanceSquare(source, dest)
        inRange = distance > 0 and distance <= self.pathSize
            
        if inRange and self._onMoveAction and dest != source:
            path = self._pathFinding.searchPath(source, dest)
            if len(path) > 0:
                path = path[1:]
            self._pathDestination = path
            for position, entity in zip(path, self._pathEntity):
                entity[PositionComponent].position = position
                entity[RenderComponent].enabled = True
                entity[AnimationComponent].enabled = True
                

    def screenToWorldPoint(self, point:Point):
        w, h = self.game.pixelsUnit
        x, y = self.device.camera.translate
        return Point((point.x + x)//w, (point.y + y)//h)

    def draw(self):
        if self._hasSelectedUnit:
            self.drawControlUnitInterface()

    def drawControlUnitInterface(self) -> None:
        loader = self.game.loader
        loader.descriptionBackground.drawAtScreen(Point(0, self.icons[0][1].y))
        for image, point, _ in self.icons:
            image.drawAtScreen(point)
    
    def _actionMove(self):
        self._onMoveAction = True
        moveElement = self.icons[0]
        image = self.game.loader.iconSelectedMove
        self.icons[0] = (image, moveElement[1], self._actionMove)
        self._updateEntityPath()
    
    def _actionMovePerform(self):
        self._onMoveAction = False
        moveElement = self.icons[0]
        image = self.game.loader.iconMove
        self.icons[0] = (image, moveElement[1], self._actionMove)
        print('Moving to', self._pathDestination)
        self._hasSelectedUnit = False
        self._disableEntitySelect()
        self._updateEntityPath()


class ControlSystem:
    def __init__(self, game: 'RogueLike'):
        self.game = game
        self.minimapOffset = 25
        device = self.game.device

        listenAction = KeyboardListener({'1'})
        listenAction.onKeyUp = self.listenerAction
        device.addListener(listenAction)

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

        listenMove = MouseMotionListener()
        listenMove.onMove = self.listenerMove
        device.addListener(listenMove)

        listenClick = MouseClickListener()
        listenClick.onMouseUp = self.listenerClick
        device.addListener(listenClick)

    def listenerControlPlayer(self, key: str) -> None:
        if (self.game[AnimationControllerSystem].lockControls
            or self.game[MotionSystem].lockControls
            or self.game[MessageSystem].lockControls):
            return

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
            self.game.player[MotionComponent].move(direction)
            self.game.update()

    def listenerControlMinimap(self, key: str) -> None:
        visible = self.game[RenderSystem].minimapVisible
        if visible:
            off = self.minimapOffset
            position = self.game[RenderSystem].minimapPosition
            if key == "down":
                position = Point(position.x, position.y + off)
            if key == "up":
                position = Point(position.x, position.y - off)
            if key == "left":
                position = Point(position.x - off, position.y)
            if key == "right":
                position = Point(position.x + off, position.y)
            self.game[RenderSystem].minimapPosition = position
            self.game.draw()

    def listenerShowMinimap(self, key: str) -> None:
        visible = self.game[RenderSystem].minimapVisible
        self.game[RenderSystem].minimapVisible = not visible
        self.game[RenderSystem].resetMinimapPosition()
        self.game.draw()

    def listenerTranslateMap(self, source: Point, dest: Point) -> None:
        position = self.game.device.camera.translate
        diff = Point(dest.x - source.x, dest.y - source.y)
        position = Point(position.x - diff.x, position.y - diff.y)
        self.game.device.camera.translate = position
        self.game.draw()

    def listenerResetCamera(self, key: str | None = None) -> None:
        self.game[CameraSystem].centralize()
        self.game[RenderSystem].resetMinimapPosition()
        self.game.draw()
    
    def listenerAction(self, key: str | None = None) -> None:
        if self.game[MessageSystem].lockControls:
            self.game[MessageSystem].update()
        else:
            self.game.player.add(MessageComponent(self.game[MessageSystem], 'Ok!'))
            self.game.player[MessageComponent].showMessage()
        self.game.draw()
    
    def listenerClick(self, point:Point) -> None:
        self.game[MouseControlSystem].hasClick = True
        self.game[MouseControlSystem].position = point
        self.game[MouseControlSystem].update()

    def listenerMove(self, point:Point) -> None:
        self.game[MouseControlSystem].position = point
        self.game[MouseControlSystem].update()

class RogueLike(Composition):
    def __init__(self, seed: int = 0, enableFOV=True):
        super().__init__()
        self.rand = Random(seed)
        self.device = Device("Picnic in the Dungeon", tick=16)
        self.pixelsUnit = Dimension(32, 32)
        self.pixelsUnitMinimap = Dimension(4, 4)
        self.loader = Loader(self.device, self.pixelsUnit, self.pixelsUnitMinimap)
        self.loader.load()
        self.map = self.createStartMap()

        ground = self.map.groundPositions
        self.add(RenderSystem(self.rand, self.loader))
        self.add(PositionSystem(ground))
        self.add(FieldOfViewSystem(ground, enableFOV))
        self.add(AnimationSystem())
        self.add(CameraSystem(self.device.camera, self.rand, self.pixelsUnit))
        self.add(AnimationControllerSystem())
        self.add(MotionSystem(self.pixelsUnit))
        self.add(MessageSystem(self.loader))
        self.add(ControlSystem(self))
        self.add(MouseControlSystem(self))

        self.player: Composition = self.createPlayer()
        self.player[CameraComponent].centralize()
        self.player[FieldOfViewComponent].update()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self[RenderSystem].setMap(self.map)
        self[RenderSystem].setView(position, visible)
        self[AnimationSystem].visible = visible
        self[AnimationControllerSystem].visible = visible

    def createStartMap(self) -> Map:
        dimension = Dimension(200, 200)
        startMap = Map(dimension, self.rand)
        startMap.makeIsland()
        return startMap

    def createPlayer(self) -> Composition:
        player = Composition()
        player.add(RenderComponent(self[RenderSystem], player, self.loader.avatar))
        player.add(PositionComponent(self[PositionSystem], player, self.map.startPoint))
        player.add(FieldOfViewComponent(self[FieldOfViewSystem], player, 6))
        player.add(AnimationComponent(self[AnimationSystem], player[RenderComponent], self.loader.avatarSprites[('idle', Direction.RIGHT)]))
        player[AnimationComponent].enabled = True
        player.add(CameraComponent(self[CameraSystem], player))
        controller = AnimationControllerComponent(self[AnimationControllerSystem], player)
        render = player[RenderComponent]
        for (key, sprite) in self.loader.avatarSprites.items():
            animation = AnimationComponent(self[AnimationSystem], render, sprite)
            controller.addAnimation(str(key), animation)
        player.add(controller)
        player.add(MotionComponent(self[MotionSystem], player[PositionComponent], controller))
        player[PositionComponent].enabled = True
        return player

    def update(self) -> None:
        self[PositionSystem].update()
        self[MotionSystem].update()
        self.player[FieldOfViewComponent].update()
        #self.player[CameraComponent].focus()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self[AnimationSystem].visible = visible
        self[AnimationControllerSystem].visible = visible
        self[RenderSystem].update(position, visible)
        self.draw()

    def draw(self) -> None:
        self.device.clear()
        self[RenderSystem].draw()
        self[MessageSystem].draw()
        self[MouseControlSystem].draw()
        self.device.reload()

    def isRunning(self) -> bool:
        return self.device.running

    def loop(self) -> None:
        self[CameraSystem].update()
        self[MotionSystem].updateOnline()
        self[AnimationControllerSystem].update()
        self[AnimationSystem].update()
        self.device.update()
        self.draw()
