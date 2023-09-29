from typing import Set
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

from entities import SimpleAnimation

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
from algorithms import relativeDirection


class ControlComponent:
    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        return False

    def mouseMove(self, screenPosition: Point, worldPosition: Point) -> None:
        pass


class ControlComponentSelectEntity(ControlComponent):
    def __init__(
        self, system: "MouseControlSystem", game: Composition, spriteSheet: SpriteSheet
    ):
        self.game = game
        self.system = system
        self.selectedEntity: Composition
        self.selectedAnimation: SimpleAnimation = SimpleAnimation(
            game, spriteSheet, Point(0, 0)
        )
        self._enabled = False

    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        if self.enabled:
            if worldPosition in self.game[PositionSystem].positionToComponent:
                component = self.game[PositionSystem].positionToComponent[worldPosition]
                self.selectedEntity = component.entity
                self.selectedAnimation[PositionComponent].position = component.position
                self.selectedAnimation.play()
                self.system.activeSelection = True
                return True
        return False

    def dropSelection(self) -> None:
        self.system.activeSelection = False
        self.selectedAnimation.stop()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self._enabled = True
            self.system.components.add(self)
        if not value and self._enabled:
            self._enabled = False
            self.selectedAnimation.stop()
            self.system.components.remove(self)


class ControlComponentPath(ControlComponent):
    def __init__(
        self, system: "MouseControlSystem", game: Composition, spriteSheet: SpriteSheet
    ):
        self.system = system
        self.pathSize = 3  # TODO num of moves, turn component
        self.selectedEntity: Composition

        self._enabled = False
        self.callback: Callable[[List[Point]], None] = lambda _: None

        self.path: List[Point] = []
        self.pathFinding = PathFinding(game[Map].groundPositions, DIRECTIONS)
        self.pathAnimations: List[SimpleAnimation] = []
        for _ in range(self.pathSize):
            self.pathAnimations.append(SimpleAnimation(game, spriteSheet, Point(0, 0)))

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self._enabled = True
            self.system.components.add(self)
        if not value and self._enabled:
            self._enabled = False
            self.clearPath()
            self.system.components.remove(self)

    def startSelection(self, entity: Composition) -> None:
        self.enabled = True
        self.selectedEntity = entity

    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        if self.enabled:
            #print('Path Selected \t', self.path)
            self.callback(self.path)
            self.clearPath()
            self.enabled = False
            return True
        return False

    def mouseMove(self, screenPosition: Point, worldPosition: Point) -> None:
        if self.enabled:
            source = self.selectedEntity[PositionComponent].position
            self.updatePath(source, worldPosition)

    def updatePath(self, source: Point, destination: Point) -> None:
        if destination == source:
            self.path = []
        else:
            distance = distanceSquare(source, destination)
            if distance > 0 and distance <= self.pathSize:
                self.path = self.pathFinding.searchPath(source, destination)
                if len(self.path) > 0:
                    self.path = self.path[1:]
                for position, entity in zip(self.path, self.pathAnimations):
                    entity[PositionComponent].position = position
                    entity.play()
        for i in range(len(self.path), self.pathSize):
            self.pathAnimations[i].stop()

    def clearPath(self):
        self.path = []
        for anim in self.pathAnimations:
            anim.stop()


class ControlComponentMove(ControlComponent):
    def __init__(self, system: "MouseControlSystem", game: Composition, loader: Loader):
        super().__init__()
        self.game = game
        self.radius = 12
        self.system = system
        self.pathSize = 3  # TODO num of moves, turn component
        _, h = loader.device.dimension
        height = h - loader.descriptionBackground.dimension.height
        width = loader.descriptionBackground.dimension.width

        self.position = Point(width - 30 - 16, height)
        self.imageIdle = loader.iconMove
        self.imageActive = loader.iconSelectedMove
        self.imageCurrent = self.imageIdle
        self.tooptip = "Move to Location"
        self.selectedEntity: Composition

        self._enabled = False
        self.active = False
        self._selectedPath: List[Point] = []

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self._enabled = True
            self.system.components.add(self)
        if not value and self._enabled:
            self._enabled = False
            self.system.components.remove(self)

    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        result = False
        if self.active:
            self.active = False
            self.imageCurrent = self.imageIdle
            self.system.controlPathSelection.enabled = False
        else:
            activeSelection = self.system.activeSelection
            if activeSelection and self.clickInRadius(screenPosition):
                self.active = True
                self.imageCurrent = self.imageActive
                entity = self.system.controlUnitSelection.selectedEntity
                self.system.controlPathSelection.callback = self.performPath
                self.system.controlPathSelection.startSelection(entity)
                result = True
        return result

    def performPath(self, path: List[Point]) -> None:
        self.selectedPath = path
        self.system.controlPathSelection.callback = lambda _: None
        print('Move to', self.selectedPath)
        if len(self.selectedPath) > 0:
            entity = self.system.controlUnitSelection.selectedEntity
            entity[MotionComponent].callback = self.perform
            self.perform()

    def perform(self) -> None:
        entity = self.system.controlUnitSelection.selectedEntity
        if len(self.selectedPath) == 0:
            entity[MotionComponent].callback = lambda: None
        else:
            position = entity[PositionComponent].position
            next = self.selectedPath.pop(0)
            direction = relativeDirection(position, next)
            entity[MotionComponent].move(direction)
            self.system.updateGame()

    def draw(self) -> None:
        self.imageCurrent.drawAtScreen(self.position)

    def clickInRadius(self, clickPosition: Point) -> bool:
        offset = Point(self.position.x + self.radius, self.position.y + self.radius)
        distance = distanceEuclidean(clickPosition, offset)
        return distance <= self.radius


class MouseControlSystem:
    def __init__(self, game: "RogueLike", loader: Loader):
        self.game = game
        self.device = game.device
        self.lockControls = False
        self._enabled = False
        self.position: Point = Point(0, 0)
        self.components: Set[ControlComponent] = set()
        self.activeSelection = False
        self.activePath: List[Point] = []

        self.background: Image = loader.descriptionBackground
        _, h = self.game.device.dimension
        loader = self.game.loader
        height = h - loader.descriptionBackground.dimension.height
        self.backgroundPosition = Point(0, height)

        self.controlUnitSelection = ControlComponentSelectEntity(
            self, game, loader.selectedUnit
        )
        self.controlPathSelection = ControlComponentPath(
            self, game, loader.selectedPath
        )
        self.controlMove = ControlComponentMove(self, game, loader)

        self.enabled = True

    def mouseClick(self, screenPosition: Point) -> None:
        worldPosition = self.screenToWorldPoint(screenPosition)
        reset = True
        for control in self.components.copy():
            if control.mouseClick(screenPosition, worldPosition):
                reset = False
        if reset:
            self.controlUnitSelection.dropSelection()

    def mouseMove(self, screenPosition: Point) -> None:
        worldPosition = self.screenToWorldPoint(screenPosition)
        for control in self.components.copy():
            control.mouseMove(screenPosition, worldPosition)

    def screenToWorldPoint(self, point: Point):
        w, h = self.game.pixelsUnit
        x, y = self.device.camera.translate
        return Point((point.x + x) // w, (point.y + y) // h)

    def draw(self):
        if self.activeSelection:
            self.background.drawAtScreen(self.backgroundPosition)
            self.controlMove.draw()
    
    def updateGame(self):
        self.game.update()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self._enabled = True
            self.controlUnitSelection.enabled = True
            self.controlMove.enabled = True
        if not value and self._enabled:
            self._enabled = False
            self.controlUnitSelection.enabled = False
            self.controlMove.enabled = False


class ControlSystem:
    def __init__(self, game: "RogueLike"):
        self.game = game
        self.minimapOffset = 25
        device = self.game.device
        self.__active = False

        listenAction = KeyboardListener({"1"})
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
        listenMove.onMove = self.game[MouseControlSystem].mouseMove
        device.addListener(listenMove)

        listenClick = MouseClickListener()
        listenClick.onMouseUp = self.game[MouseControlSystem].mouseClick
        device.addListener(listenClick)

    def listenerControlPlayer(self, key: str) -> None:
        if (
            self.game[AnimationControllerSystem].lockControls
            or self.game[MotionSystem].lockControls
            or self.game[MessageSystem].lockControls
        ):
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
        if self.__active:
            self.__active = False
            self.game[MouseControlSystem].enabled = False
        else:
            self.__active = True
            self.game[MouseControlSystem].enabled = True
        self.game.draw()


class RogueLike(Composition):
    def __init__(self, seed: int = 0, enableFOV=True):
        super().__init__()
        self.rand = Random(seed)
        self.device = Device("Picnic in the Dungeon", tick=16)
        self.pixelsUnit = Dimension(32, 32)
        self.pixelsUnitMinimap = Dimension(4, 4)
        self.loader = Loader(self.device, self.pixelsUnit, self.pixelsUnitMinimap)
        self.loader.load()

        self.add(self.createStartMap())
        self.add(RenderSystem(self.rand, self.loader))
        self.add(PositionSystem(self[Map].groundPositions))
        self.add(FieldOfViewSystem(self[Map].groundPositions, enableFOV))
        self.add(AnimationSystem())
        self.add(CameraSystem(self.device.camera, self.rand, self.pixelsUnit))
        self.add(AnimationControllerSystem())
        self.add(MotionSystem(self.pixelsUnit))
        self.add(MessageSystem(self.loader))
        self.add(MouseControlSystem(self, self.loader))
        self.add(ControlSystem(self))

        self.player: Composition = self.createPlayer()
        self.player[CameraComponent].centralize()
        self.player[FieldOfViewComponent].update()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self[RenderSystem].setMap(self[Map])
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
        player.add(
            PositionComponent(self[PositionSystem], player, self[Map].startPoint)
        )
        player.add(FieldOfViewComponent(self[FieldOfViewSystem], player, 6))
        player.add(
            AnimationComponent(
                self[AnimationSystem],
                player[RenderComponent],
                self.loader.avatarSprites[("idle", Direction.RIGHT)],
            )
        )
        player[AnimationComponent].enabled = True
        player.add(CameraComponent(self[CameraSystem], player))
        controller = AnimationControllerComponent(
            self[AnimationControllerSystem], player
        )
        render = player[RenderComponent]
        for key, sprite in self.loader.avatarSprites.items():
            animation = AnimationComponent(self[AnimationSystem], render, sprite)
            controller.addAnimation(str(key), animation)
        player.add(controller)
        player.add(
            MotionComponent(self[MotionSystem], player[PositionComponent], controller)
        )
        player[PositionComponent].enabled = True
        return player

    def update(self) -> None:
        self[PositionSystem].update()
        self[MotionSystem].update()
        self.player[FieldOfViewComponent].update()
        # self.player[CameraComponent].focus()
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
