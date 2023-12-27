
from algorithms.point import Point
from algorithms.random import Random
from core import Scene
from map import Map, Rect, TileType
from map_builders.mapBuilderBase import MapBuilderBase


class SimpleMapBuilder(MapBuilderBase):

    def __init__(self):
        super().__init__()
        self.name = 'Simple'
        self.maxRooms = 30
        self.minSize = 6
        self.maxSize = 10

    def build(self, width: int, height: int, depth: int, rand: Random) -> tuple[Map, Point]:
        self.map = Map(width, height)
        self.map.name = self.name
        self.map.depth = depth
        self.rooms: list[Rect] = list()
        self.newMapRoomsAndCorridors(self.map, rand)
        x, y = self.rooms[0].center()
        return (self.map, Point(x, y))

    def spawn(self, scene: Scene, map: Map, depth: int, rand: Random) -> None:
        for room in self.rooms[1:]:
            self.spawnRoom(scene, room, depth, rand, 4)

    def newMapRoomsAndCorridors(self, map: Map, rand: Random) -> None:
        for _ in range(0, self.maxRooms):
            w = rand.nextRange(self.minSize, self.maxSize)
            h = rand.nextRange(self.minSize, self.maxSize)
            x = rand.nextRange(1, map.width - (w + 1))
            y = rand.nextRange(1, map.height - (h + 1))
            newRoom = Rect(x, y, w, h)
            validLocation = True
            for otherRoom in self.rooms:
                if newRoom.intersect(otherRoom):
                    validLocation = False
            if validLocation:
                self.applyRoomToMap(map.tiles, newRoom)
                self.takeSnapshot()
                if self.rooms:
                    xnew, ynew = newRoom.center()
                    xprev, yprev = self.rooms[-1].center()
                    if rand.nextBool():
                        self.applyHorizontalTunnel(map.tiles, xprev, xnew, yprev)
                        self.applyVerticalTunnel(map.tiles, yprev, ynew, xnew)
                    else:
                        self.applyVerticalTunnel(map.tiles, yprev, ynew, xprev)
                        self.applyHorizontalTunnel(map.tiles, xprev, xnew, ynew)
                self.rooms.append(newRoom)
                self.takeSnapshot()
        lastRoom = self.rooms[-1]
        center = lastRoom.center()
        map.tiles[Point(center[0], center[1])] = TileType.DownStairs
