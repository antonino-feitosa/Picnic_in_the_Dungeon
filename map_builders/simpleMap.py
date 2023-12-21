
from algorithms.point import Point
from algorithms.random import Random
from core import Scene
from map import Map, Rect, TileType
from spawner import createBearTrap, createConfusionScroll, createDagger, createFireballScroll, createGoblin, createHealthPotion, createLongSword, createMagicMapperScroll, createMagicMissileScroll, createOrc, createRations, createShield, createTowerShield, roomTable


class SimpleMapBuilder:

    def __init__(self):
        self.rooms: list[Rect] = list()

    def build(self, width: int, height: int, depth: int, rand: Random) -> tuple[Map, Point]:
        map = Map(width, height)
        self.rooms = list()
        self.newMapRoomsAndCorridors(map, depth, rand)
        x, y = self.rooms[0].center()
        return (map, Point(x, y))

    def spawn(self, scene: Scene, map: Map, depth: int, rand: Random) -> None:
        for room in self.rooms[1:]:
            self.spawnRoom(scene, room, depth, rand, 4)

    def applyRoomToMap(self, tiles: dict[Point, TileType], room: Rect) -> None:
        for y in range(room.y1 + 1, room.y2 + 1):
            for x in range(room.x1 + 1, room.x2 + 1):
                tiles[Point(x, y)] = TileType.Floor

    def applyHorizontalTunnel(self, tiles: dict[Point, TileType], x1: int, x2: int, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            tiles[Point(x, y)] = TileType.Floor

    def applyVerticalTunnel(self, tiles: dict[Point, TileType], y1: int, y2: int, x: int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            tiles[Point(x, y)] = TileType.Floor

    def newMapRoomsAndCorridors(self, map: Map, depth: int, rand: Random) -> None:
        map.depth = depth

        maxRooms = 30
        minSize = 6
        maxSize = 10
        for _ in range(0, maxRooms):
            w = rand.nextRange(minSize, maxSize)
            h = rand.nextRange(minSize, maxSize)
            x = rand.nextRange(1, map.width - (w + 1))
            y = rand.nextRange(1, map.height - (h + 1))
            newRoom = Rect(x, y, w, h)
            validLocation = True
            for otherRoom in self.rooms:
                if newRoom.intersect(otherRoom):
                    validLocation = False
            if validLocation:
                self.applyRoomToMap(map.tiles, newRoom)
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
        lastRoom = self.rooms[-1]
        center = lastRoom.center()
        map.tiles[Point(center[0], center[1])] = TileType.DownStairs

    def spawnRoom(self, scene: Scene, room: Rect, depth: int, rand: Random, startNumMonster: int = 4) -> None:
        numMonsters = rand.nextRange(1, startNumMonster + 3) + (depth - 1) - 3
        positions: set[tuple[Point, str]] = set()
        spawnTable = roomTable(depth)
        errors = 10

        while (len(positions) < numMonsters and errors > 0):
            x = (room.x1 + 1) + rand.nextInt((room.x2 - room.x1) - 1)
            y = (room.y1 + 1) + rand.nextInt((room.y2 - room.y1) - 1)
            point = Point(x, y)
            if point not in positions:
                spawn = spawnTable.roll(rand)
                positions.add((point, spawn))
            else:
                errors -= 1

        for (point, name) in positions:
            x = point.x
            y = point.y
            match name:
                case "Goblin": createGoblin(scene, x, y)
                case "Orc": createOrc(scene, x, y)
                case "Health Potion": createHealthPotion(scene, x, y)
                case "Fireball Scroll": createMagicMissileScroll(scene, x, y)
                case "Confusion Scroll": createFireballScroll(scene, x, y)
                case "Magic Missile Scroll": createConfusionScroll(scene, x, y)
                case "Dagger": createDagger(scene, x, y)
                case "Shield": createShield(scene, x, y)
                case "Long Sword": createLongSword(scene, x, y)
                case "Tower Shield": createTowerShield(scene, x, y)
                case "Rations": createRations(scene, x, y)
                case "Magic Mapper Scroll": createMagicMapperScroll(scene, x, y)
                case "Bear Trap": createBearTrap(scene, x, y)
