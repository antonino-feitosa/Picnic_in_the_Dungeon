
from base import Map
from base import Loader

from device import Device
from device import KeyboardListener
from device import MouseDragListener

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

from algorithms import Point
from algorithms import Random
from algorithms import Dimension
from algorithms import Direction
from algorithms import Composition

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
        if self.game.animationControllerSystem.lockControls or self.game.motionSystem.lockControls:
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
    def __init__(self, seed: int = 0, enableFOV=True):
        self.rand = Random(seed)
        self.device = Device("Picnic in the Dungeon", tick=16)
        self.pixelsUnit = Dimension(32, 32)
        self.pixelsUnitMinimap = Dimension(4, 4)
        self.loader = Loader(self.device, self.pixelsUnit, self.pixelsUnitMinimap)
        self.loader.load()
        self.map = self.createStartMap()

        ground = self.map.groundPositions
        self.renderSystem = RenderSystem(self.rand, self.loader)
        self.positionSystem = PositionSystem(ground)
        self.fieldOfViewSystem = FieldOfViewSystem(ground, enableFOV)
        self.controlSystem = ControlSystem(self)
        self.animationSystem = AnimationSystem()
        self.cameraSystem = CameraSystem(self.device.camera, self.rand, self.pixelsUnit)
        self.animationControllerSystem = AnimationControllerSystem()
        self.motionSystem = MotionSystem(self.pixelsUnit)

        self.player: Composition = self.createPlayer()
        self.player[CameraComponent].centralize()
        self.player[FieldOfViewComponent].update()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self.renderSystem.setMap(self.map)
        self.renderSystem.setView(position, visible)
        self.animationSystem.visible = visible
        self.animationControllerSystem.visible = visible

    def createStartMap(self) -> Map:
        dimension = Dimension(200, 200)
        startMap = Map(dimension, self.rand)
        startMap.makeIsland()
        return startMap

    def createPlayer(self) -> Composition:
        player = Composition()
        player.add(RenderComponent(self.renderSystem, player, self.loader.avatar))
        player.add(PositionComponent(self.positionSystem, player, self.map.startPoint))
        player.add(FieldOfViewComponent(self.fieldOfViewSystem, player, 6))
        player.add(AnimationComponent(self.animationSystem, player[RenderComponent], self.loader.avatarSprites[('idle', Direction.RIGHT)]))
        player[AnimationComponent].play()
        player.add(CameraComponent(self.cameraSystem, player))
        controller = AnimationControllerComponent(self.animationControllerSystem, player)
        render = player[RenderComponent]
        for (key, sprite) in self.loader.avatarSprites.items():
            animation = AnimationComponent(self.animationSystem, render, sprite)
            controller.addAnimation(str(key), animation)
        player.add(controller)
        player.add(MotionComponent(self.motionSystem, player[PositionComponent], controller))
        return player

    def update(self) -> None:
        self.positionSystem.update()
        self.motionSystem.update()
        self.player[FieldOfViewComponent].update()
        #self.player[CameraComponent].focus()
        position = self.player[PositionComponent].position
        visible = self.player[FieldOfViewComponent].visible
        self.animationSystem.visible = visible
        self.animationControllerSystem.visible = visible
        self.renderSystem.update(position, visible)
        self.draw()

    def draw(self) -> None:
        self.device.clear()
        self.renderSystem.draw()
        self.device.reload()

    def isRunning(self) -> bool:
        return self.device.running

    def loop(self) -> None:
        self.cameraSystem.update()
        self.motionSystem.updateOnline()
        self.animationControllerSystem.update()
        self.animationSystem.update()
        self.device.update()
        self.draw()
