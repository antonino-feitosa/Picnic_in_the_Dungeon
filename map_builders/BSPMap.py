# binary space partition

from algorithms.point import Point
from algorithms.random import Random
from core import Scene
from map import Map, Rect, TileType
from map_builders.mapBuilderBase import MapBuilderBase


class BSPDungeonBuilder(MapBuilderBase):
    def __init__(self):
        super().__init__()
        self.levels = 10
        self.gap = 5
        self.minWidth = 5
        self.minHeight = 5
        self.map: Map
        self.rooms: list[Rect]

    def build(self, width: int, height: int, depth: int, rand: Random) -> tuple[Map, Point]:
        self.map = Map(width, height)
        self.map.depth = depth
        self.rooms: list[Rect] = list()

        bounds = Rect(1, 1, width - 2, height - 2)
        rects = self.binaryPartition(bounds, self.levels, rand)
        for rect in rects:
            self.rooms.append(rect)
            self.applyRoomToMap(self.map.tiles, rect)
            self.takeSnapshot()

        sortOption = rand.nextRange(1,5)
        name = 'Random BSP'
        if sortOption == 1:
            name = 'Direct Horizontal BSP'
            self.rooms.sort(key=lambda room: room.x1)
        elif sortOption == 2:
            name = 'Reverse Horizontal BSP'
            self.rooms.sort(key=lambda room: -room.x1)
        elif sortOption == 3:
            name = 'Direct Vertical BSP'
            self.rooms.sort(key=lambda room: room.y1)
        elif sortOption == 4:
            name = 'Reverse Vertical BSP'
            self.rooms.sort(key=lambda room: -room.y1)
        
        if self.name == '':
            self.map.name = name
        else:
            self.map.name = self.name

        previous = self.rooms[0]
        for room in self.rooms[1:]:
            pCenter = previous.center()
            rCenter = room.center()
            self.drawCorridor(pCenter[0], pCenter[1], rCenter[0], rCenter[1])
            self.takeSnapshot()
            previous = room

        ex, ey = self.rooms[-1].center()
        self.map.tiles[Point(ex, ey)] = TileType.DownStairs
        self.takeSnapshot()

        x, y = self.rooms[0].center()
        return (self.map, Point(x, y))

    def spawn(self, scene: Scene, map: Map, depth: int, rand: Random) -> None:
        for room in self.rooms[1:]:
            self.spawnRoom(scene, room, depth, rand, 4)

    def binaryPartition(self, bounds: Rect, levels: int, rand: Random) -> list[Rect]:
        rects: list[Rect] = list()
        rects.append(bounds)
        while levels > 0:
            nextLevel: list[Rect] = list()
            for rect in rects:
                cantDivide = True
                if rand.nextBool():
                    if rect.x2 - rect.x1 > 2 * self.minWidth + self.gap:
                        half = rand.nextRange(rect.x1 + self.minWidth, rect.x2 - self.minWidth - self.gap)
                        w1 = half - rect.x1
                        w2 = rect.x2 - half
                        r1 = Rect(rect.x1, rect.y1, w1, rect.y2 - rect.y1)
                        r2 = Rect(half, rect.y1, w2, rect.y2 - rect.y1)
                        r2.x1 += self.gap
                        v1 = r1.x2 - r1.x1 > self.minWidth
                        v2 = r2.x2 - r2.x1 > self.minWidth
                        if v1 and v2:
                            cantDivide = False
                            nextLevel.append(r1)
                            nextLevel.append(r2)
                else:
                    if rect.y2 - rect.y1 > 2 * self.minHeight + self.gap:
                        half = rand.nextRange(rect.y1 + self.minHeight, rect.y2 - self.minHeight - self.gap)
                        h1 = half - rect.y1
                        h2 = rect.y2 - half
                        r1 = Rect(rect.x1, rect.y1, rect.x2 - rect.x1, h1)
                        r2 = Rect(rect.x1, half, rect.x2 - rect.x1, h2)
                        r2.y1 += self.gap
                        v1 = r1.y2 - r1.y1 > self.minHeight
                        v2 = r2.y2 - r2.y1 > self.minHeight
                        if v1 and v2:
                            cantDivide = False
                            nextLevel.append(r1)
                            nextLevel.append(r2)
                if cantDivide:
                    nextLevel.append(rect)
            levels -= 1
            rects = nextLevel
        return rects

    def drawCorridor(self, x1: int, y1: int, x2: int, y2: int) -> None:
        while x1 != x2 or y1 != y2:
            if x1 < x2:
                x1 += 1
            elif x1 > x2:
                x1 -= 1
            elif y1 < y2:
                y1 += 1
            elif y1 > y2:
                y1 -= 1
            self.map.tiles[Point(x1, y1)] = TileType.Floor
