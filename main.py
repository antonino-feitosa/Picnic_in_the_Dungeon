from typing import cast
from core import ECS, Component, Scene, Entity
from device import Device, Image
from coordinates import Dimension


class Position(Component):
    id = ECS.nextSignature()
    __slots__ = "x", "y"

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(Position.id)
        self.x = x
        self.y = y


class Renderable(Component):
    id = ECS.nextSignature()
    __slots__ = "image"

    def __init__(self, image: Image):
        super().__init__(Renderable.id)
        self.image: Image = image


class LeftMover(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(LeftMover.id)


def leftWalker():
    entities = ECS.scene.filter(Position.id | LeftMover.id)
    for entity in entities:
        position = cast(Position, entity[Position.id])
        position.x = position.x - 1 if position.x > 0 else 19


def update():
    leftWalker()

    entities = ECS.scene.filter(Position.id | Renderable.id)
    for entity in entities:
        position = cast(Position, entity[Position.id])
        render = cast(Renderable, entity[Renderable.id])
        render.image.draw(position.x * 32, position.y * 32)


def main():
    screenDimension = Dimension(640, 320)
    device = Device("Picnic in the Dungeon", screenDimension, tick=1)

    scene = Scene()

    scene.store("avatar", device.loadImage("./_resources/Modelo de Avatar.png"))

    scene.create().add(Position(5, 5)).add(Renderable(scene.retrieve("avatar")))

    for i in range(1, 10, 2):
        scene.create(). \
            add(Position(i, 2)). \
            add(Renderable(scene.retrieve("avatar"))). \
            add(LeftMover())

    device.onLoop.append(update)

    ECS.scene = scene

    while device.running:
        device.clear()
        device.loop()
        device.draw()


if __name__ == "__main__":
    main()
