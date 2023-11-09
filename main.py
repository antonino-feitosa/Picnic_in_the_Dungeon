from typing import cast
from enum import Enum
from algorithms import Random
from core import ECS, Component, Scene
from device import Device, Image, Font, Color
from coordinates import Dimension

UNITS = Dimension(16,16)

class TileType(Enum):
    Wall = 0,
    Floor = 1


def makeMap(width:int, height:int, rand:Random, x:int, y:int) -> list[list[TileType]]:
    map: list[list[TileType]] = list()
    for row in range(0, height):
        column:list[TileType] = list()
        map.append(column)
        for col in range(0, width):
            if row == y and col == x:
                column.append(TileType.Floor)
            else:
                tile = TileType.Floor if rand.nextBool() else TileType.Wall
                column.append(tile)
            if row == 0 or row == width - 1:
                map[row][col] = TileType.Wall
            if col == 0 or col == height - 1:
                map[row][col] = TileType.Wall
    return map
        


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


def drawMap():
    glyphWall = cast(Glyph, ECS.scene.retrieve("glyph wall"))
    glyphFloor = cast(Glyph, ECS.scene.retrieve("glyph floor"))
    map = cast(list[list[TileType]], ECS.scene.retrieve("map"))
    for row in range(0, 20):
        for col in range(0,40):
            tile = map[row][col]
            if tile == TileType.Floor:
                glyphFloor.draw(col * UNITS.width, row * UNITS.height)
            if tile == TileType.Wall:
                glyphWall.draw(col * UNITS.width, row * UNITS.height)


def tryMovePlayer(dx:int, dy:int):
    map = cast(list[list[TileType]], ECS.scene.retrieve("map"))
    entities = ECS.scene.filter(Position.id | Player.id)
    for entity in entities:
        position = cast(Position, entity[Position.id])
        # TODO check map, map as vector
        position.x = max(0, min(position.x + dx, 39))
        position.y = max(0, min(position.y + dy, 19))


def playerInput(keys:set[str]):
    if 'up' in keys: tryMovePlayer(0, -1)
    elif 'down' in keys: tryMovePlayer(0, +1)
    if 'left' in keys: tryMovePlayer(-1, 0)
    elif 'right' in keys: tryMovePlayer(+1, 0)


def update():
    drawMap()

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
    rand = Random(0)
    glyphWall = Glyph(background, font, '#')
    glyphWall.foreground = (0, 255, 0, 255)
    glyphFloor = Glyph(background, font, '.')
    glyphFloor.foreground = (127, 127, 127, 255)

    scene.store("background", background)
    scene.store("font", font)
    scene.store("rand", rand)
    scene.store("map", makeMap(40, 20, rand, 5, 5))
    scene.store("glyph wall", glyphWall)
    scene.store("glyph floor", glyphFloor)

    scene.create() \
        .add(Position(5, 5)) \
        .add(Renderable(Glyph(background, font, '@'))) \
        .add(Player())

    device.onLoop.append(update)
    device.onPressed.append(playerInput)

    ECS.scene = scene

    while device.running:
        device.clear()
        device.loop()
        device.draw()


if __name__ == "__main__":
    main()
