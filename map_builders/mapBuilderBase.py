
from algorithms.point import Point
from map import Map

MAP_WIDTH = 80
MAP_HEIGHT = 30


class MapBuilderBase:

    def __init__(self):
        self.map: Map
        self.startPosition: Point
        self.depth: int = 1
        self.snapshotHistory:list[Map] = list()

    def build(self, depth: int):
        pass

    def spawn(self):
        pass
    
    def takeSnapshot(self):
        clone = self.map.clone()
        clone.revealedTiles = set(clone.tiles.keys())
        self.snapshotHistory.append(clone)
