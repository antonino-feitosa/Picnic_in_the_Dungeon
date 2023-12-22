
from algorithms.point import Point
from map import Map, Rect, TileType

MAP_WIDTH = 80
MAP_HEIGHT = 30


class MapBuilderBase:

    def __init__(self):
        self.map: Map
        self.startPosition: Point
        self.depth: int = 1
        self.snapshotHistory: list[Map] = list()

    def build(self, depth: int):
        pass

    def spawn(self):
        pass

    def takeSnapshot(self):
        clone = self.map.clone()
        clone.revealedTiles = set(clone.tiles.keys())
        self.snapshotHistory.append(clone)

    def applyRoomToMap(self, tiles: dict[Point, TileType], room: Rect) -> None:
        for y in range(room.y1, room.y2):
            for x in range(room.x1, room.x2):
                tiles[Point(x, y)] = TileType.Floor

    def applyHorizontalTunnel(self, tiles: dict[Point, TileType], x1: int, x2: int, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            tiles[Point(x, y)] = TileType.Floor

    def applyVerticalTunnel(self, tiles: dict[Point, TileType], y1: int, y2: int, x: int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            tiles[Point(x, y)] = TileType.Floor
