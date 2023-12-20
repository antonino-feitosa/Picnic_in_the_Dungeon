
from algorithms.point import Point
from algorithms.random import Random
from core import ECS
from map import Map
from map_builders.simpleMap import SimpleMapBuilder


MAP_WIDTH = 80
MAP_HEIGHT = 30


class MapBuilder:

    def __init__(self):
        self.map: Map
        self.startPosition: Point
        self.depth: int = 1

    def build(self, depth: int):
        rand: Random = ECS.scene.retrieve("random")
        self.depth = depth
        self.map, self.startPosition = SimpleMapBuilder().build(MAP_WIDTH, MAP_HEIGHT, depth, rand)

    def spawn(self):
        rand: Random = ECS.scene.retrieve("random")
        SimpleMapBuilder().spawn(ECS.scene, self.map, self.depth, rand)
