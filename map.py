from enum import Enum

from algorithms import Random, Point
from core import ECS, Entity
from device import Font, Image


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
    def __init__(self, width:int, height:int):
        self.width = width
        self.height = height
        self.tiles: dict[Point, TileType] = dict()
        self.visibleTiles: set[Point] = set()
        self.revealedTiles: set[Point] = set()
        self.rooms: list[Rect] = list()
        self.blocked: set[Point] = set()
        self.tileContent: dict[Point, list[Entity]] = dict()
        self.depth = 0

    def clearMap(self) -> None:
        self.tiles.clear()
        self.visibleTiles.clear()
        self.revealedTiles.clear()
        self.rooms.clear()
        self.blocked.clear()
        self.tileContent.clear()
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

    def applyRoomToMap(self, room:Rect) -> None:
        for y in range(room.y1 + 1, room.y2 + 1):
            for x in range(room.x1 + 1, room.x2 + 1):
                self.tiles[Point(x,y)] = TileType.Floor

    def applyHorizontalTunnel(self, x1:int, x2:int, y:int) -> None:
        for x in range(min(x1, x2), max(x1,x2) + 1):
            self.tiles[Point(x, y)] = TileType.Floor

    def applyVerticalTunnel(self, y1:int, y2:int, x:int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[Point(x,y)] = TileType.Floor

    def newTestMap (self, depth:int) -> None:
        self.clearMap()
        self.depth = depth
        room1 = Rect(10, 5, 10, 10)
        room2 = Rect(25, 5, 10, 10)
        room3 = Rect(40, 5, 10, 10)
        self.rooms.append(room1)
        self.rooms.append(room2)
        self.rooms.append(room3)
        self.applyRoomToMap(room1)
        self.applyRoomToMap(room2)
        self.applyRoomToMap(room3)
        self.applyHorizontalTunnel(15, 30, 10)
        self.applyHorizontalTunnel(30, 45, 10)
        center = room3.center()
        self.tiles[Point(center[0], center[1])] = TileType.DownStairs


    def newMapRoomsAndCorridors (self, depth:int, rand: Random) -> None:
        self.clearMap()
        self.depth = depth

        maxRooms = 30
        minSize = 6
        maxSize = 10
        for _ in range(0, maxRooms):
            w = rand.nextRange(minSize, maxSize)
            h = rand.nextRange(minSize, maxSize)
            x = rand.nextRange(1, self.width - (w + 1))
            y = rand.nextRange(1, self.height - (h + 1))
            newRoom = Rect(x, y, w, h)
            validLocation = True
            for otherRoom in self.rooms:
                if newRoom.intersect(otherRoom):
                    validLocation = False
            if validLocation:
                self.applyRoomToMap(newRoom)
                if self.rooms:
                    xnew, ynew = newRoom.center()
                    xprev, yprev = self.rooms[-1].center()
                    if rand.nextBool():
                        self.applyHorizontalTunnel(xprev, xnew, yprev)
                        self.applyVerticalTunnel(yprev, ynew, xnew)
                    else:
                        self.applyVerticalTunnel(yprev, ynew, xprev)
                        self.applyHorizontalTunnel(xprev, xnew, ynew)
                self.rooms.append(newRoom)
        lastRoom = self.rooms[-1]
        center = lastRoom.center()
        self.tiles[Point(center[0], center[1])] = TileType.DownStairs


        



def drawMap(xoff:int, yoff:int):
    font:Font = ECS.scene.retrieve("font")
    map: Map = ECS.scene.retrieve("map")
    
    font.foreground = (127, 127, 127, 255)
    font.background = (0, 0, 0, 255)
    
    for pos in map.revealedTiles:
        if pos not in map.visibleTiles:
            tile = map.tiles[Point(pos.x, pos.y)]
            if tile == TileType.Floor:
                font.drawGlyphAtScreenCenterSpace('.', pos.x + xoff, pos.y + yoff)
            if tile == TileType.Wall:
                glyph = getWallGlyph(pos.x, pos.y, map)
                font.drawGlyphAtScreen(glyph, pos.x + xoff, pos.y + yoff)
            if tile == TileType.DownStairs:
                font.drawGlyphAtScreenCenterSpace('>', pos.x + xoff, pos.y + yoff)

    for pos in map.visibleTiles:
        tile = map.tiles[Point(pos.x, pos.y)]
        if tile == TileType.Floor:
            font.foreground = (0, 127, 127, 255)
            font.drawGlyphAtScreenCenterSpace('.', pos.x + xoff, pos.y + yoff)
        if tile == TileType.Wall:
            font.foreground = (0, 255, 0, 255)
            glyph = getWallGlyph(pos.x, pos.y, map)
            font.drawGlyphAtScreen(glyph, pos.x + xoff, pos.y + yoff)
        if tile == TileType.DownStairs:
            font.foreground = (0, 255, 255, 255)
            font.drawGlyphAtScreenCenterSpace('>', pos.x + xoff, pos.y + yoff)


def isRevealedAndWall(x:int, y:int, map:Map) -> bool:
    point = Point(x,y)
    return point in map.revealedTiles and map.tiles[point] == TileType.Wall

def getWallGlyph(x:int, y:int, map:Map) -> str:
    mask = 0
    if isRevealedAndWall(x, y-1, map): mask += 1
    if isRevealedAndWall(x, y+1, map): mask += 2
    if isRevealedAndWall(x-1, y, map): mask += 4
    if isRevealedAndWall(x+1, y, map): mask += 8

    match mask:
        case 0: return '○' # { 9 } // Pillar because we can't see neighbors
        case 1: return '║' #  { 186 } // Wall only to the north
        case 2: return '║' #  { 186 } // Wall only to the south
        case 3: return '║' #  { 186 } // Wall to the north and south
        case 4: return '═' #  { 205 } // Wall only to the west
        case 5: return '╝' #  { 188 } // Wall to the north and west
        case 6: return '╗' #  { 187 } // Wall to the south and west
        case 7: return '╣' #  { 185 } // Wall to the north, south and west
        case 8: return '═' #  { 205 } // Wall only to the east
        case 9: return '╚' #  { 200 } // Wall to the north and east
        case 10: return '╔' #  { 201 } // Wall to the south and east
        case 11: return '╠' #  { 204 } // Wall to the north, south and east
        case 12: return '═' #  { 205 } // Wall to the east and west
        case 13: return '╩' #  { 202 } // Wall to the east, west, and south
        case 14: return '╦' #  { 203 } // Wall to the east, west, and north
        case 15: return '╬' #  { 206 }  // ╬ Wall on all sides
    return '#'