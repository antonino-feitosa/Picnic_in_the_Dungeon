from typing import cast
from core import ECS, Component, Scene
from device import Device, Image, Font, Color
from coordinates import Dimension


class Glyph:
    def __init__(self, image, font, glyph):
        self.image:Image = image
        self.font:Font = font
        self.glyph:str = glyph
        self._foreground:Color = (255,255,255, 255)
        self._background:Color = (0,0,0, 0)
        self._glyphImage:Image
        self.update()
    
    @property
    def foreground(self):
        return self._foreground
    
    @foreground.setter
    def foreground(self, value):
        if value != self._foreground:
            self._foreground = value
            self.update()
    
    @property
    def background(self):
        return self._foreground
    
    @background.setter
    def background(self, value):
        if value != self._background:
            self._background = value
            self.update()
    
    def draw(self, x:int, y:int):
        self._glyphImage.draw(x, y)
    
    def update(self):
        self._glyphImage = self.image.clone()
        self.font.foreground = self._foreground
        self.font.background = self._background
        self.font.drawAtImageCenter(self.glyph, self._glyphImage)


class Position(Component):
    id = ECS.nextSignature()
    __slots__ = "x", "y"

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(Position.id)
        self.x = x
        self.y = y


class Renderable(Component):
    id = ECS.nextSignature()
    __slots__ = "glyph"

    def __init__(self, glyph: Glyph):
        super().__init__(Renderable.id)
        self.glyph:Glyph = glyph

class Player(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(Player.id)

class LeftMover(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(LeftMover.id)


def leftWalker():
    entities = ECS.scene.filter(Position.id | LeftMover.id)
    for entity in entities:
        position = cast(Position, entity[Position.id])
        position.x = position.x - 1 if position.x > 0 else 19


def  tryMovePlayer(dx:int, dy:int):
    entities = ECS.scene.filter(Position.id | Player.id)
    for entity in entities:
        position = cast(Position, entity[Position.id])
        position.x = max(0, min(position.x + dx, 39))
        position.y = max(0, min(position.y + dy, 19))


def playerInput(keys:set[str]):
    if 'up' in keys: tryMovePlayer(0, -1)
    elif 'down' in keys: tryMovePlayer(0, +1)
    if 'left' in keys: tryMovePlayer(-1, 0)
    elif 'right' in keys: tryMovePlayer(+1, 0)


def update():
    leftWalker()

    entities = ECS.scene.filter(Position.id | Renderable.id)
    for entity in entities:
        position = cast(Position, entity[Position.id])
        render = cast(Renderable, entity[Renderable.id])
        render.glyph.draw(position.x * 16, position.y * 16)


def main():
    screenDimension = Dimension(640, 320)
    device = Device("Picnic in the Dungeon", screenDimension, tick=8)

    scene = Scene()

    background = device.loadImage("./_resources/_roguelike/background.png")
    font = device.loadFont("./_resources/_roguelike/gadaj.otf", 16)

    scene.store("background", background)
    scene.store("font", font)

    scene.create() \
        .add(Position(5, 5)) \
        .add(Renderable(Glyph(background, font, '@'))) \
        .add(Player())

    for i in range(1, 10, 2):
        scene.create() \
            .add(Position(i, 2)) \
            .add(Renderable(Glyph(background, font, 'M'))) \
            .add(LeftMover())

    device.onLoop.append(update)
    device.onPressed.append(playerInput)

    ECS.scene = scene

    while device.running:
        device.clear()
        device.loop()
        device.draw()


if __name__ == "__main__":
    main()
