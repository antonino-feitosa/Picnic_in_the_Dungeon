from enum import Enum

from algorithms import Point
from algorithms.direction import Direction
from component import Renderable
from core import ECS, Entity
from screen import Screen, ScreenLayer


class TileType(Enum):
    Wall = 0
    Floor = 1
    DownStairs = 2


class Rect:
    __slots__ = ["x1", "y1", "x2", "y2"]

    def __init__(self, x: int, y: int, w: int = 0, h: int = 0):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def intersect(self, rect) -> bool:
        return (
            self.x1 <= rect.x2
            and self.x2 >= rect.x1
            and self.y1 <= rect.y2
            and self.y2 >= rect.y1
        )

    def center(self) -> tuple[int, int]:
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def __repr__(self) -> str:
        return f"<(x1={self.x1}, y1={self.y1}), (x2={self.x2}, y2={self.y2})>"


class Map:
    def __init__(self, width: int, height: int):
        self.name = ''
        self.width = width
        self.height = height
        self.tiles: dict[Point, TileType] = dict()
        self.visibleTiles: set[Point] = set()
        self.revealedTiles: set[Point] = set()
        self.blocked: set[Point] = set()
        self.tileContent: dict[Point, list[Entity]] = dict()
        self.bloodstains: set[Point] = set()
        self.depth = 0
        for row in range(0, self.height):
            for col in range(0, self.width):
                self.tiles[Point(col, row)] = TileType.Wall

    def populateBlocked(self):
        self.blocked.clear()
        for row in range(0, self.height):
            for col in range(0, self.width):
                point = Point(col, row)
                if self.tiles[point] == TileType.Wall:
                    self.blocked.add(point)

    def clearContentIndex(self):
        self.tileContent.clear()

    def clone(self) -> 'Map':
        newMap = Map(self.width, self.height)
        newMap.tiles = self.tiles.copy()
        newMap.visibleTiles = self.visibleTiles.copy()
        newMap.revealedTiles = self.revealedTiles.copy()
        newMap.blocked = self.blocked.copy()
        for pos in self.tileContent:
            newMap.tileContent[pos] = self.tileContent[pos].copy()
        newMap.bloodstains = self.bloodstains.copy()
        return newMap


def drawMapBackground(screen: Screen, map: Map):
    wallTiles: set[Point] = set()
    for point in map.tiles:
        tile = map.tiles[point]
        if tile == TileType.Floor:
            for dir in Direction.All:
                n = point + dir
                if n in map.tiles and map.tiles[n] == TileType.Wall:
                    wallTiles.add(n)

    for point in wallTiles:
        glyph = getWallGlyph(point, wallTiles)
        screen.setGlyph(ScreenLayer.BackgroundRevealed, point, Renderable(glyph, 0, (127, 127, 127, 255)))
        screen.setGlyph(ScreenLayer.BackgroundVisible, point, Renderable(glyph, 0, (0, 255, 0, 255)))

    for point in map.tiles:
        tile = map.tiles[point]
        if tile == TileType.Floor:
            screen.setGlyph(ScreenLayer.BackgroundRevealed, point, Renderable('.', 0, (127, 127, 127, 255)))
            screen.setGlyph(ScreenLayer.BackgroundVisible, point, Renderable('.', 0, (0, 127, 127, 255)))
        if tile == TileType.DownStairs:
            screen.setGlyph(ScreenLayer.BackgroundRevealed, point, Renderable('>', 0, (127, 127, 127, 255)))
            screen.setGlyph(ScreenLayer.BackgroundVisible, point, Renderable('>', 0, (0, 255, 255, 255)))


def drawMap(screen: Screen, map: Map):
    bloodstain = Renderable(' ', 0, (255, 255, 255, 0))
    bloodstain.background = (100, 0, 0, 255)
    for point in map.bloodstains:
        screen.setGlyph(ScreenLayer.BackgroundEffects, point, bloodstain)
    screen.setRevealed(map.revealedTiles)
    screen.setVisible(map.visibleTiles)


def getWallGlyph(point: Point, walls: set[Point]) -> str:
    mask = 0
    if point + Direction.Up in walls:
        mask += 1
    if point + Direction.Down in walls:
        mask += 2
    if point + Direction.Left in walls:
        mask += 4
    if point + Direction.Right in walls:
        mask += 8

    match mask:
        case 0: return '○'  # { 9 } // Pillar because we can't see neighbors
        case 1: return '║'  # { 186 } // Wall only to the north
        case 2: return '║'  # { 186 } // Wall only to the south
        case 3: return '║'  # { 186 } // Wall to the north and south
        case 4: return '═'  # { 205 } // Wall only to the west
        case 5: return '╝'  # { 188 } // Wall to the north and west
        case 6: return '╗'  # { 187 } // Wall to the south and west
        case 7: return '╣'  # { 185 } // Wall to the north, south and west
        case 8: return '═'  # { 205 } // Wall only to the east
        case 9: return '╚'  # { 200 } // Wall to the north and east
        case 10: return '╔'  # { 201 } // Wall to the south and east
        case 11: return '╠'  # { 204 } // Wall to the north, south and east
        case 12: return '═'  # { 205 } // Wall to the east and west
        case 13: return '╩'  # { 202 } // Wall to the east, west, and south
        case 14: return '╦'  # { 203 } // Wall to the east, west, and north
        case 15: return '╬'  # { 206 }  // ╬ Wall on all sides
    return '#'
