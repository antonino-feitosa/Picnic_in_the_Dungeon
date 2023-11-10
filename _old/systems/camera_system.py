import math

from core import Entity

from device import Camera

from algorithms import Random
from algorithms import Point
from algorithms import Dimension

from systems import PositionComponent


class CameraComponent:
    def __init__(self, system: "CameraSystem", entity: Entity):
        self.system = system
        self.entity = entity
        self.delay = 8
        self.speed: Point = Point(4, 4)
        self.ticks = 8
        self.magnitude = 4
        self.enabled = True

    def focus(self) -> None:
        self.system.focus(self)

    def centralize(self) -> None:
        self.system.active = self
        self.system.centralize()

    def shake(self) -> None:
        self.system.shake(self)

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return self.entity.__str__()


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
                direction = self._current.relativeDirection(self._destination)
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
