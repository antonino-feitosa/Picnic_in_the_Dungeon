from enum import Enum

from algorithms import Point
from core import ECS, Entity
from glyphScreen import GlyphScreen


class TileType(Enum):
    Wall = 0
    Floor = 1
    DownStairs = 2


class Rect:
    __slots__ = ["x1", "y1", "x2", "y2"]

    def __init__(self, x: int, y: int, w: int, h: int):
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
        return f"<({self.x1}, {self.y1}), ({self.x2}, {self.y2})>"


class Map:
    def __init__(self, width: int, height: int):
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

    # def newTestMap (self, depth:int) -> None:
    #     self.clearMap()
    #     self.depth = depth
    #     room1 = Rect(5, 5, 6, 6)
    #     room2 = Rect(15, 5, 6, 6)
    #     room3 = Rect(25, 5, 6, 6)
    #     self.rooms.append(room1)
    #     self.rooms.append(room2)
    #     self.rooms.append(room3)
    #     self.applyRoomToMap(self.tiles, room1)
    #     self.applyRoomToMap(self.tiles, room2)
    #     self.applyRoomToMap(self.tiles, room3)
    #     self.applyHorizontalTunnel(self.tiles, 6, 16, 8)
    #     self.applyHorizontalTunnel(self.tiles, 16, 26, 8)
    #     center = room3.center()
    #     self.tiles[Point(center[0], center[1])] = TileType.DownStairs


def drawMap(screen: GlyphScreen, map:Map):
    for pos in map.revealedTiles:
        if pos not in map.visibleTiles:
            tile = map.tiles[Point(pos.x, pos.y)]
            glyph = ''
            if tile == TileType.Floor:
                glyph = '.'
            if tile == TileType.DownStairs:
                glyph = '>'
            if tile == TileType.Wall:
                glyph = getWallGlyph(pos.x, pos.y, map)
            if glyph != '':
                screen.setGlyph(pos.x, pos.y, glyph, (127, 127, 127, 255))

    for pos in map.visibleTiles:
        if pos in map.bloodstains:
            screen.setBackground(pos.x, pos.y, (100, 0, 0, 255))

        tile = map.tiles[Point(pos.x, pos.y)]
        if tile == TileType.Floor:
            screen.setGlyph(pos.x, pos.y, '.', (0, 127, 127, 255))
        if tile == TileType.DownStairs:
            screen.setGlyph(pos.x, pos.y, '>', (0, 255, 255, 255))
        if tile == TileType.Wall:
            glyph = getWallGlyph(pos.x, pos.y, map)
            screen.setGlyph(pos.x, pos.y, glyph, (0, 255, 0, 255))


def isRevealedAndWall(x: int, y: int, map: Map) -> bool:
    point = Point(x, y)
    return point in map.tiles and point in map.revealedTiles and map.tiles[point] == TileType.Wall


def getWallGlyph(x: int, y: int, map: Map) -> str:
    mask = 0
    if isRevealedAndWall(x, y-1, map):
        mask += 1
    if isRevealedAndWall(x, y+1, map):
        mask += 2
    if isRevealedAndWall(x-1, y, map):
        mask += 4
    if isRevealedAndWall(x+1, y, map):
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
