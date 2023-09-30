from typing import Callable, Set, Tuple
from algorithms.dimension import Dimension
from algorithms.direction import Direction
from algorithms.position import Position
from core import Entity, Game
from systems.animation_system import AnimationControllerComponent
from systems.collision_system import CollisionComponent
from systems.control_system import ControlSystem
from systems.position_system import PositionComponent
from systems.render_system import RenderComponent


class MotionComponent:
    def __init__(self, system: "MotionSystem", entity:Entity):
        self.system = system
        self.entity = entity
        self.speed = 8
        system.components.add(self)
        self._enabled = True
        self.callback: Callable[[], None] = lambda: None
        self.system.components.add(self)

    def move(self, direction: Direction) -> None:
        self.system.toMove.add((self, direction))

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self.system.components.add(self)
            self._enabled = True
        if not value and self._enabled:
            self.system.components.remove(self)
            self._enabled = False
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return self.entity.__str__()


class MotionSystem:
    def __init__(self, game: Game, unitPixels: Dimension):
        self.game = game
        self.unitPixels = unitPixels
        self.lockControls = False
        self.components: Set[MotionComponent] = set()
        self.toMove: Set[Tuple[MotionComponent, Direction]] = set()
        self.moving: Set[Tuple[RenderComponent, Position, int]] = set()
        self.enabled = True
        self.game.updateSystems.append(self)
        self.game.tickSystems.append(self)

    def update(self) -> None:
        for component, direction in self.toMove:
            collisionComponent = component.entity[CollisionComponent]
            controller = component.entity[AnimationControllerComponent]
            controller.playAnimation("idle." + str(direction))
            self.game[ControlSystem].lockControls = True
            if collisionComponent.collided:
                controller.shootAnimation("collision." + str(direction))
            else:
                spd = component.speed
                render = component.entity[RenderComponent]
                controller.shootAnimation("walk." + str(direction))
                x, y = self.unitPixels
                delta = Position(x * direction.x // spd, y * direction.y // spd)
                self.moving.add((render, delta, spd - 1))
                render.offset = Position(x * -direction.x, y * -direction.y)
        self.toMove.clear()

    def tick(self) -> None:
        lock = False
        if len(self.moving) > 0:
            moving: Set[Tuple[RenderComponent, Position, int]] = set()
            for render, delta, spd in self.moving:
                spd -= 1
                if spd == 0:
                    render.offset = Position(0, 0)
                    render.entity[MotionComponent].callback()
                else:
                    lock = True
                    x, y = render.offset
                    render.offset = Position(x + delta.x, y + delta.y)
                    moving.add((render, delta, spd))
            self.moving = moving
        self.game[ControlSystem].lockControls = lock
