
from algorithms import Point
from core import ECS, Component, Entity
from device import Color, Font, Image


class Glyph:
    def __init__(self, image, font, glyph):
        self.image: Image = image
        self.font: Font = font
        self.glyph: str = glyph
        self._foreground: Color = (255, 255, 255, 255)
        self._background: Color = (0, 0, 0, 0)
        self._glyphImage: Image
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

    def draw(self, x: int, y: int):
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

    def __hash__(self) -> int:  # grid (-4096, -4096) x (4096, 4096)
        return 4096 * (4096 + self.y) + (4096 + self.x)

    def __eq__(self, other: "Position"):
        return other is not None and self.x == other.x and self.y == other.y


class Renderable(Component):
    id = ECS.nextSignature()
    __slots__ = "glyph"

    def __init__(self, glyph: Glyph):
        super().__init__(Renderable.id)
        self.glyph: Glyph = glyph


class Player(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(Player.id)


class Viewshed(Component):
    id = ECS.nextSignature()
    __slots__ = ["range", "visibleTiles", "dirty"]

    def __init__(self, range: int):
        super().__init__(Viewshed.id)
        self.dirty = True
        self.range = range
        self.visibleTiles: set[Point] = set()


class Monster(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(Monster.id)


class Name(Component):
    id = ECS.nextSignature()
    __slots__ = 'name'

    def __init__(self, name:str):
        super().__init__(Name.id)
        self.name = name

class BlocksTile(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(BlocksTile.id)

class CombatStats(Component):
    id = ECS.nextSignature()
    __slots__ = ["maxHP", "HP", "defense", "power"]

    def __init__(self, maxHP:int, defense:int, power:int):
        super().__init__(CombatStats.id)
        self.maxHP = maxHP
        self.HP = maxHP
        self.defense = defense
        self.power = power

class WantsToMelee(Component):
    id = ECS.nextSignature()
    __slots__ = ["target"]

    def __init__(self, target:Entity):
        super().__init__(WantsToMelee.id)
        self.target = target
