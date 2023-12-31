from typing import Callable

from algorithms import Dimension, Direction, Point
from core import Component, Entity, Game, System
from systems import (
    AnimationControllerComponent,
    CollisionComponent,
    ControlSystem,
    WorldRenderComponent,
)


class MotionComponent(Component["MotionSystem"]):
    def __init__(self, system: "MotionSystem", entity: Entity):
        super().__init__(system, entity)
        self.speed = 8
        self.callback: Callable[[], None] = lambda: None
        self.enabled = True

    def move(self, direction: Direction) -> None:
        self.system.toMove.add((self, direction))


class MotionSystem(System[MotionComponent]):
    def __init__(self, game: Game, unitPixels: Dimension):
        super().__init__(game, set())
        self.unitPixels = unitPixels
        self.lockControls = False
        self.toMove: set[tuple[MotionComponent, Direction]] = set()
        self.moving: set[tuple[WorldRenderComponent, Point, int]] = set()
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
                render = component.entity[WorldRenderComponent]
                controller.shootAnimation("walk." + str(direction))
                x, y = self.unitPixels
                delta = Point(x * direction.x // spd, y * direction.y // spd)
                self.moving.add((render, delta, spd - 1))
                render.offset = Point(x * -direction.x, y * -direction.y)
        self.toMove.clear()

    def tick(self) -> None:
        lock = False
        if len(self.moving) > 0:
            moving: set[tuple[WorldRenderComponent, Point, int]] = set()
            for render, delta, spd in self.moving:
                spd -= 1
                if spd == 0:
                    render.offset = Point(0, 0)
                    render.entity[MotionComponent].callback()
                else:
                    lock = True
                    x, y = render.offset
                    render.offset = Point(x + delta.x, y + delta.y)
                    moving.add((render, delta, spd))
            self.moving = moving
        self.game[ControlSystem].lockControls = lock
