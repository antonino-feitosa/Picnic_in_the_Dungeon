import math

from typing import Set
from typing import Tuple

from base import Map
from base import Loader
from base import Message
from base import Background

from device import Image
from device import Camera
from device import SpriteSheet

from algorithms import Set
from algorithms import Dict
from algorithms import List
from algorithms import Point
from algorithms import Random
from algorithms import Dimension
from algorithms import Direction
from algorithms import Composition
from algorithms import FieldOfView

from algorithms import relativeDirection


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


class MotionSystem:
    def __init__(self, unitPixels:Dimension):
        self.unitPixels = unitPixels
        self.lockControls = False
        self.components: Set['MotionComponent'] = set()
        self.toMove: Set[Tuple[MotionComponent, Direction]] = set()
        self.moving: Set[Tuple[RenderComponent, Point, int]] = set()
    
    def update(self):
        for (component, direction) in self.toMove:
            positionComponent = component.entity[PositionComponent]
            controller = component.entity[AnimationControllerComponent]
            controller.playAnimation(str(('idle', direction)))
            if len(positionComponent.collided) > 0:
                controller.playAnimationInStack(str(('collision', direction)), lockControls=True)
            else:
                spd = component.speed
                render = controller.getCurrentAnimation().render
                controller.playAnimationInStack(str(('walk', direction)), lockControls=True)
                x, y = self.unitPixels
                delta = Point(x * direction.x // spd, y * direction.y // spd)
                self.moving.add((render, delta, spd - 1))
                render.offset = Point(x * -direction.x, y * -direction.y)
        self.toMove.clear()
    
    def updateOnline(self):
        lock = False
        if len(self.moving) > 0:
            moving:Set[Tuple[RenderComponent, Point, int]] = set()
            for (render, delta, spd) in self.moving:
                spd -= 1
                if spd == 0:
                    render.offset = Point(0,0)
                else:
                    lock = True
                    x, y = render.offset
                    render.offset = Point(x + delta.x, y + delta.y)
                    moving.add((render, delta, spd))
            self.moving = moving
        self.lockControls = lock

        


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


class FieldOfViewSystem:
    def __init__(self, ground: set[Point], enableFOV: bool):
        self.enableFOV = enableFOV
        self.ground = ground
        self._fov = FieldOfView(1, ground)

    def update(self, component: 'FieldOfViewComponent') -> None:
        if self.enableFOV:
            fov = self._fov
            fov.ground = self.ground
            fov.radius = component.radius
            fov.focalDistance = component.focalDistance
            fov.angleOfView = component.angle
            fov.formatOfView = component.format
            direction = component.entity[MotionComponent].direction
            center = component.entity[PositionComponent].position
            component.visible = fov.rayCasting(center, direction)
        else:
            component.visible = self.ground


class CameraSystem:
    def __init__(self, camera: Camera, rand: Random, pixelsUnit: Dimension):
        self.rand = rand
        self.camera = camera
        self.withDelay: bool = True
        self.pixelsUnit = pixelsUnit
        self.active: CameraComponent
        self._offset: Point = Point(0, 0)
        self._countShake = 0
        self._magnitude = 3
        self._applying = False
        self._current: Point = Point(0, 0)
        self._waitingToApply = 0
        self._destination: Point = Point(0, 0)
        self._speed: Point = Point(0, 0)

    def focus(self, component: "CameraComponent") -> None:
        self.active = component
        if self.withDelay:
            self._current = self.camera.translate
            self._waitingToApply = component.delay
            self._applying = True
            position = self.active.entity[PositionComponent].position
            position = self.toScreenUnit(position)
            self._destination = self.camera.referenceToCenter(position)
            if self._current != self._destination:
                direction = relativeDirection(self._current, self._destination)
                sx, sy = component.speed
                self._speed = Point(direction.x * sx, direction.y * sy)
        else:
            self.centralize()

    def centralize(self):
        position = self.active.entity[PositionComponent].position
        x, y = self.toScreenUnit(position)
        offx, offy = self._offset
        self.camera.centralize(Point(x + offx, y + offy))

    def toScreenUnit(self, point: Point) -> Point:
        ux, uy = self.pixelsUnit
        return Point(point.x * ux, point.y * uy)

    def shake(self, component: "CameraComponent") -> None:
        self._countShake = component.ticks
        self._magnitude = component.magnitude
        self._applyShake()

    def _applyShake(self) -> None:
        dx = self.rand.nextNormal(0, self._magnitude)
        dy = self.rand.nextNormal(0, self._magnitude)
        self._offset = Point(math.ceil(dx), math.ceil(dy))

    def _applyFocusWithDelay(self) -> bool:
        source = self._current
        dest = self._destination
        sx, sy = self._speed
        x = source.x + sx if abs(source.x - dest.x) >= abs(sx) else dest.x
        y = source.y + sy if abs(source.y - dest.y) >= abs(sy) else dest.y
        self._current = Point(x, y)
        offx, offy = self._offset
        self.camera.translate = Point(x + offx, y + offy)
        return self._current != self._destination

    def update(self) -> None:
        if self._applying:
            if self._waitingToApply > 0:
                self._waitingToApply -= 1
            else:
                self._applying = self._applyFocusWithDelay()
        if self._countShake > 0:
            self._applyShake()
            self.centralize()
            self._countShake -= 1
        elif self._countShake == 0:
            self._offset = Point(0, 0)
            self._countShake = -1
            self.centralize()


class AnimationSystem:
    def __init__(self):
        self.visible: Set[Point] = set()
        self.components: Set[AnimationComponent] = set()

    def update(self):
        for component in self.components:
            position = component.entity[PositionComponent].position
            if position in self.visible:
                component.update()


class AnimationControllerSystem:
    def __init__(self):
        self.lockControls = False
        self.visible: Set[Point] = set()
        self.components: Set[AnimationControllerComponent] = set()

    def update(self):
        lock = False
        for component in self.components:
            position = component.entity[PositionComponent].position
            if position in self.visible:
                component.update()
                if component.lockControls:
                    lock = True
        self.lockControls = lock


class MessageSystem:
    def __init__(self, loader:Loader):
        self.component: MessageComponent | None = None
        self.confirm = False
        self.cancel = False
        self.option = 0
        self.lockControls = False
        self._message = Message(loader)
    
    def showMessage(self, component:'MessageComponent') -> None:
        self._message.setMessages([component.text])
        self.component = component
        self.lockControls = True
    
    def draw(self):
        if self.component is not None:
            self._message.draw()
    
    def update(self):
        if self.component is not None:
            self.component.confirmed = self.confirm
            self.component.canceled = self.cancel
            self.component.answer = self.option
            self.component = None
        self.confirm = False
        self.cancel = False
        self.option = 0
        self.lockControls = False
        
    

##############################################################################
# Components
##############################################################################


class RenderComponent:
    def __init__(self, system: RenderSystem, entity: Composition, image: Image):
        self.system = system
        self.image = image
        self.entity = entity
        self.offset: Point = Point(0, 0)
        self._enabled = True
        system.components.add(self)
    
    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.system.components.add(self)
                self._enabled = True
        else:
            if self._enabled:
                self.system.components.remove(self)
                self._enabled = False

    def draw(self):
        width, height = self.entity[PositionComponent].position
        uw, uh = self.system.loader.pixelsUnit
        dx, dy = self.offset
        position = Point(width * uw + dx, height * uh + dy)
        self.image.draw(position)


class PositionComponent:
    def __init__(self, system: PositionSystem, entity: Composition, position: Point):
        self.system = system
        self.entity = entity
        self.position: Point = position
        self.collided: List[Tuple[Composition | None, Point]] = []
        self._enabled = False

    def move(self, direction: Direction) -> None:
        self.collided.clear()
        self.system.toMove.add((self, direction))

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.system.positionToComponent[self.position] = self
                self._enabled = True
        else:
            if self._enabled:
                self.system.positionToComponent.pop(self.position)
                self._enabled = False


class MotionComponent:
    def __init__(self, system: MotionSystem, position:PositionComponent, controller:'AnimationControllerComponent'):
        self.system = system
        self.entity = position.entity
        self.controller = controller
        self.speed = 8
        self.direction = Direction.RIGHT
        system.components.add(self)
        self._enabled = True
    
    def move(self, direction:Direction) -> None:
        self.entity[PositionComponent].move(direction)
        self.system.toMove.add((self, direction))
        self.direction = direction
    
    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.system.components.add(self)
                self._enabled = True
        else:
            if self._enabled:
                self.system.components.remove(self)
                self._enabled = False


class FieldOfViewComponent:
    AngleCone = 'cone'
    AngleRadial = 'radial'
    AnglePeripheral = 'peripheral'

    FormatOctal = 'octal'
    FormatCircle = 'circle'
    FormatSquare = 'square'
    FormatDiamond = 'diamond'

    def __init__(self, system: FieldOfViewSystem, entity: Composition, radius: int):
        self.system = system
        self.entity = entity
        self.radius = radius
        self.focalDistance = 0
        self.visible: Set[Point] = set()
        self.angle = FieldOfViewComponent.AngleRadial
        self.format = FieldOfViewComponent.FormatOctal

    def update(self):
        self.system.update(self)
    
    @property
    def enabled(self):
        pass

    @enabled.setter
    def enabled(self, value):
        pass


class AnimationComponent:
    def __init__(
        self, system: AnimationSystem, render: RenderComponent, animation: SpriteSheet
    ):
        self.tick = 1
        self.loop = True
        self._tickCount = 0
        self._frameIndex = 0
        self.render = render
        self.system = system
        self.animation = animation
        self.entity = render.entity
        self._enabled = False
    
    @property
    def finished(self):
        return not self.loop and self._frameIndex == len(self.animation.images) - 1

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.system.components.add(self)
                self._enabled = True
        else:
            if self._enabled:
                self.system.components.remove(self)
                self._enabled = False

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
    def __init__(self, system: CameraSystem, entity: Composition):
        self.system = system
        self.entity = entity
        self.delay = 8
        self.speed: Point = Point(4, 4)
        self.ticks = 8
        self.magnitude = 4

    def focus(self) -> None:
        self.system.focus(self)

    def centralize(self) -> None:
        self.system.active = self
        self.system.centralize()

    def shake(self) -> None:
        self.system.shake(self)
    
    @property
    def enabled(self):
        pass

    @enabled.setter
    def enabled(self, value):
        pass


class AnimationControllerComponent:
    def __init__(self, system: AnimationControllerSystem, entity: Composition):
        self.system = system
        self.entity = entity
        self.lockControls = False
        self.animations: Dict[str, AnimationComponent] = dict()
        self._stackContext: bool = False
        self._baseAnimation: AnimationComponent
        self._stackAnimation: AnimationComponent
        self._baseAnimationName: str
        self._stackAnimationName: str
        system.components.add(self)
        self._enabled = True

    def addAnimation(self, name: str, animation: "AnimationComponent"):
        self.animations[name] = animation

    def getCurrentAnimationName(self) -> str:
        name = self._baseAnimationName
        return name if not self._stackContext else self._stackAnimationName

    def getCurrentAnimation(self) -> AnimationComponent:
        name = self._baseAnimation
        return name if not self._stackContext else self._stackAnimation

    def playAnimation(self, name: str) -> None:
        self._baseAnimationName = name
        self._baseAnimation = self.animations[name]
        self._baseAnimation.loop = True
        self._playAnimation(self._baseAnimation)

    def playAnimationInStack(self, name: str, lockControls = False) -> None:
        self.lockControls = lockControls
        self._stackAnimationName = name
        self._stackAnimation = self.animations[name]
        self._stackAnimation.loop = False
        self._stackContext = True
        self._playAnimation(self._stackAnimation)

    def _restoreBaseAnimation(self) -> None:
        self.entity[AnimationComponent].enabled = False
        self.entity.remove(AnimationComponent)
        self._baseAnimation.enabled = True

    def _playAnimation(self, animation: AnimationComponent) -> None:
        self.entity[AnimationComponent].enabled = False
        self.entity.remove(AnimationComponent)
        animation.reload()
        animation.enabled = True

    def update(self):
        if self._stackContext:
            if self._stackAnimation.finished:
                self._restoreBaseAnimation()
                self._stackContext = False
                self.lockControls = False
    
    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.system.components.add(self)
                self._enabled = True
        else:
            if self._enabled:
                self.system.components.remove(self)
                self._enabled = False


class MessageComponent:
    def __init__(self, system:MessageSystem, text:str):
        self.text = text
        self.system = system
        self.confirmed = False
        self.canceled = False
        self.answer = 0
    
    def showMessage(self) -> None:
        self.system.showMessage(self)
    
    @property
    def enabled(self):
        pass

    @enabled.setter
    def enabled(self, value):
        pass
