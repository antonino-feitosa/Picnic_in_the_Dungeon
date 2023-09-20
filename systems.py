
import math

from typing import Set
from typing import Tuple

from base import Map
from base import Loader
from base import Background

from device import Image
from device import Camera
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

from algorithms import sign
from algorithms import CARDINALS
from algorithms import DIRECTIONS
from algorithms import relativeDirection
from algorithms import distanceManhattan
from algorithms import fieldOfViewRayCasting


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
    def __init__(self, ground: set[Point], enableFOV: bool):
        self.enableFOV = enableFOV
        self.ground = ground

    def update(self, component: 'FieldOfViewComponent') -> None:
        if self.enableFOV:
            radius = component.radius
            center = component.entity[PositionComponent].position
            ground = self.ground
            component.visible = fieldOfViewRayCasting(center, radius, ground)
        else:
            component.visible = self.ground


class CameraSystem:
    def __init__(self, camera: Camera, rand:Random, pixelsUnit:Dimension):
        self.rand = rand
        self.camera = camera
        self.withDelay: bool = True
        self.pixelsUnit = pixelsUnit
        self.active: CameraComponent
        self._offset: Point = Point(0, 0)
        self._countShake = 0
        self._applying = False
        self._current: Point = Point(0, 0)
        self._waitingToApply = 0
        self._destination: Point = Point(0, 0)
        self._speed: Point = Point(0, 0)

    def focus(self, component: 'CameraComponent') -> None:
        self.active = component
        if self.withDelay:
            self._current = self.camera.translate
            self._waitingToApply = component.delay
            self._applying = True
            position = self.active.entity[PositionComponent].position
            position = self.toScreenUnit(position)
            self._destination = self.camera.referenceToCenter(position)
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
        self.countShake = component.ticks
        self.magnitude = component.magnitude
        self._applyShake()

    def _applyShake(self) -> None:
        dx = self.rand.nextNormal(0, self.magnitude)
        dy = self.rand.nextNormal(0, self.magnitude)
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


# Components



class RenderComponent:
    def __init__(self, system: RenderSystem, entity: Composition, image: Image):
        self.system = system
        self.image = image
        self.entity = entity
        self.offset: Point = Point(0, 0)
        system.components.add(self)

    def draw(self):
        width, height = self.entity[PositionComponent].position
        uw, uh = self.system.loader.pixelsUnit
        dx, dy = self.offset
        position = Point(width * uw + dx, height * uh + dy)
        self.image.draw(position)

    def destroy(self):
        self.system.components.remove(self)


class PositionComponent:
    def __init__(self, system: PositionSystem, entity: Composition, position: Point):
        self.system = system
        self.entity = entity
        self.position: Point = position
        self.collided: List[Tuple[Composition | None, Point]] = []
        system.positionToComponent[position] = self

    def move(self, direction: Direction) -> None:
        self.system.toMove.add((self, direction))


class FieldOfViewComponent:
    def __init__(self, system: FieldOfViewSystem, entity: Composition, radius: int):
        self.system = system
        self.radius = radius
        self.entity = entity
        self.visible: Set[Point] = set()

    def update(self):
        self.system.update(self)


class AnimationComponent:
    def __init__(self, system:AnimationSystem, render: RenderComponent, animation: SpriteSheet):
        self.tick = 1
        self.loop = True
        self._tickCount = 0
        self._frameIndex = 0
        self.render = render
        self.system = system
        self.animation = animation
        self.entity = render.entity
        self.system.components.add(self)

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
    def __init__(self, system:CameraSystem, entity: Composition):
        self.system = system
        self.entity = entity
        self.delay = 5
        self.speed: Point = Point(4, 4)
        self.ticks = 3
        self.magnitude = 3

    def focus(self) -> None:
        self.system.focus(self)

    def centralize(self) -> None:
        self.system.active = self
        self.system.centralize()

    def shake(self) -> None:
        self.system.shake(self)


