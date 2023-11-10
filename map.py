from enum import Enum

from algorithms import Random, Point
from component import Glyph
from core import ECS, Entity


class TileType(Enum):
    Wall = 0,
    Floor = 1


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
        self.tileContent: dict[Point, list[Entity]]

    def clearMap(self) -> None:
        self.tiles.clear()
        self.visibleTiles.clear()
        self.revealedTiles.clear()
        self.rooms.clear()
        self.blocked.clear()
        self.tileContent.clear()
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

    def newMapRoomsAndCorridors (self, rand: Random) -> None:
        self.clearMap()

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


        



def drawMap():
    glyphWall: Glyph = ECS.scene.retrieve("glyph wall")
    glyphFloor: Glyph = ECS.scene.retrieve("glyph floor")
    map: Map = ECS.scene.retrieve("map")
    widthPixels, heightPixels = ECS.scene.retrieve("pixels unit")

    glyphFloor.foreground = (127, 127, 127, 255)
    glyphWall.foreground = (127, 127, 127, 255)
    for pos in map.revealedTiles:
        if pos not in map.visibleTiles:
            tile = map.tiles[Point(pos.x, pos.y)]
            if tile == TileType.Floor:
                glyphFloor.draw(pos.x * widthPixels, pos.y * heightPixels)
            if tile == TileType.Wall:
                glyphWall.draw(pos.x * widthPixels, pos.y * heightPixels)
    
    glyphFloor.foreground = (0, 127, 127, 255)
    glyphWall.foreground = (0, 255, 0, 255)
    for pos in map.visibleTiles:
        tile = map.tiles[Point(pos.x, pos.y)]
        if tile == TileType.Floor:
            glyphFloor.draw(pos.x * widthPixels, pos.y * heightPixels)
        if tile == TileType.Wall:
            glyphWall.draw(pos.x * widthPixels, pos.y * heightPixels)
