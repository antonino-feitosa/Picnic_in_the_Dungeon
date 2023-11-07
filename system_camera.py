import math

from core import Entity, Random

from coordinates import Position, Dimension


class CameraComponent:
    def __init__(self, system: "CameraSystem", entity: Entity):
        self.system = system
        self.entity = entity
        self.delay = 8
        self.speed: Position = Position(4, 4)
        self.ticks = 8
        self.magnitude = 4
        self.enabled = True
        self._position: Position = Position()
    
    @property
    def position(self) -> Position:
        return self._position
    
    @position.setter
    def position(self, pos:Position) -> None:
        self._position = pos

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
    def __init__(self, rand: Random, screenDimension:Dimension, pixelsUnit: Dimension):
        self.rand = rand                       
        self.withDelay: bool = True
        self.pixelsUnit = pixelsUnit
        self.screenDimension = screenDimension
        self.active: CameraComponent
        self._offset: Position = Position(0, 0)
        self._countShake = 0
        self._magnitude = 3
        self._applying = False
        self._current: Position = Position(0, 0)
        self._waitingToApply = 0
        self._destination: Position = Position(0, 0)
        self._speed: Position = Position(0, 0)
        self._position: Position = Position()
    
    @property
    def position(self) -> Position:
        return self._position
    
    @position.setter
    def position(self, pos:Position) -> None:
        self._position = pos

    def focus(self, component: "CameraComponent") -> None:
        self.active = component
        if self.withDelay:
            self._current = self._position
            self._waitingToApply = component.delay
            self._applying = True
            position = self.active.position
            position = self.toScreenUnit(position)
            self._destination = self.referenceToCenter(position)
            if self._current != self._destination:
                direction = self._current.relativeDirection(self._destination)
                sx, sy = component.speed
                self._speed = Position(direction.x * sx, direction.y * sy)
        else:
            self.centralize()

    def centralize(self):
        position = self.active.position
        x, y = self.toScreenUnit(position)
        offx, offy = self._offset
        position = Position(x + offx, y + offy)
        self._position = self.referenceToCenter(position)

    def toScreenUnit(self, point: Position) -> Position:
        ux, uy = self.pixelsUnit
        return Position(point.x * ux, point.y * uy)
    
    def referenceToCenter(self, position: Position) -> Position:
        width, height = self.screenDimension
        return Position(position.x - width // 2, position.y - height // 2)

    def shake(self, component: "CameraComponent") -> None:
        self._countShake = component.ticks
        self._magnitude = component.magnitude
        self._applyShake()

    def _applyShake(self) -> None:
        dx = self.rand.nextNormal(0, self._magnitude)
        dy = self.rand.nextNormal(0, self._magnitude)
        self._offset = Position(math.ceil(dx), math.ceil(dy))

    def _applyFocusWithDelay(self) -> bool:
        source = self._current
        dest = self._destination
        sx, sy = self._speed
        x = source.x + sx if abs(source.x - dest.x) >= abs(sx) else dest.x
        y = source.y + sy if abs(source.y - dest.y) >= abs(sy) else dest.y
        self._current = Position(x, y)
        offx, offy = self._offset
        self._position = Position(x + offx, y + offy)
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
            self._offset = Position(0, 0)
            self._countShake = -1
            self.centralize()
