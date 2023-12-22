
# binary space partition

from algorithms.point import Point
from algorithms.random import Random
from core import Scene
from map import Map, Rect, TileType
from map_builders.mapBuilderBase import MapBuilderBase
from spawner import createBearTrap, createConfusionScroll, createDagger, createFireballScroll, createGoblin, createHealthPotion, createLongSword, createMagicMapperScroll, createMagicMissileScroll, createOrc, createRations, createShield, createTowerShield, roomTable


class BSPDungeonBuilder(MapBuilderBase):

    def __init__(self):
        super().__init__()
        self.roomRate = 1.0
        self.levels = 10
        self.gap = 2
        self.minWidth = 5
        self.minHeight = 5
        self.maxWidth = 10
        self.maxHeight = 10

    def build(self, width: int, height: int, depth: int, rand: Random) -> tuple[Map, Point]:
        self.map = Map(width, height)
        self.rooms: list[Rect] = list()

        bounds = Rect(1, 1, width - 2, height - 2)
        rects = self.binaryPartition(bounds, self.levels, rand)
        gap = self.gap
        for rect in rects:
            rect = Rect(rect.x1 + gap, rect.y1 + gap, rect.x2 - rect.x1 - gap, rect.y2 - rect.y1 - gap)
            if rand.nextDouble() < self.roomRate and self.isPossibleSubRect(rect):
                room = self.randomSubRect(rect, rand)
                self.rooms.append(room)
                self.applyRoomToMap(self.map.tiles, room)
                self.takeSnapshot()

        x, y = self.rooms[0].center()
        return (self.map, Point(x, y))

    def spawn(self, scene: Scene, map: Map, depth: int, rand: Random) -> None:
        # for room in self.rooms[1:]:
        #    self.spawnRoom(scene, room, depth, rand, 4)
        pass

    def isPossibleSubRect(self, rect: Rect) -> bool:
        maxWidth = min(rect.x2 - rect.x1, self.maxWidth)
        maxHeight = min(rect.y2 - rect.y1, self.maxHeight)
        if maxWidth < self.minWidth or maxHeight < self.minHeight:
            return False
        if rect.x2 - rect.x1 < self.minWidth:
            return False
        if rect.y2 - rect.y1 < self.minHeight:
            return False
        return True

    def randomSubRect(self, rect: Rect, rand: Random) -> Rect:
        maxWidth = min(rect.x2 - rect.x1, self.maxWidth)
        maxHeight = min(rect.y2 - rect.y1, self.maxHeight)
        width = rand.nextRange(self.minWidth, maxWidth) if maxWidth > self.minWidth else self.minWidth
        height = rand.nextRange(self.minHeight, maxHeight) if maxHeight > self.minHeight else self.minHeight
        maxX = maxWidth - width
        maxY = maxHeight - height
        x = rand.nextRange(0, maxX) if maxX > 0 else 0
        y = rand.nextRange(0, maxY) if maxY > 0 else 0
        return Rect(rect.x1 + x, rect.y1 + y, width, height)

    def binaryPartition(self, bounds: Rect, levels: int, rand: Random) -> list[Rect]:
        rects: list[Rect] = list()
        rects.append(bounds)
        while levels > 0:
            nextLevel: list[Rect] = list()
            for rect in rects:
                if rand.nextBool():
                    xmin = rect.x1 + self.minWidth
                    xmax = rect.x2 - self.minWidth
                    if xmax > xmin:
                        half = rand.nextRange(xmin, xmax)
                        w1 = half - rect.x1
                        w2 = rect.x2 - half
                        r1 = Rect(rect.x1, rect.y1, w1, rect.y2 - rect.y1)
                        r2 = Rect(half, rect.y1, w2, rect.y2 - rect.y1)
                        nextLevel.append(r1)
                        nextLevel.append(r2)
                    else:
                        nextLevel.append(rect)
                else:
                    ymin = rect.y1 + self.minHeight
                    ymax = rect.y2 - self.minHeight
                    if ymax > ymin:
                        half = rand.nextRange(ymin, ymax)
                        h1 = half - rect.y1
                        h2 = rect.y2 - half
                        r1 = Rect(rect.x1, rect.y1, rect.x2 - rect.x1, h1)
                        r2 = Rect(rect.x1, half, rect.x2 - rect.x1, h2)
                        nextLevel.append(r1)
                        nextLevel.append(r2)
                    else:
                        nextLevel.append(rect)
            levels -= 1
            rects = nextLevel
        return rects
