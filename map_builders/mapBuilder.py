
from algorithms.point import Point
from algorithms.random import Random
from core import ECS
from map import Map
from map_builders.BSPMap import BSPDungeonBuilder
from map_builders.mapBuilderBase import MAP_HEIGHT, MAP_WIDTH, MapBuilderBase
from map_builders.simpleMap import SimpleMapBuilder


class MapBuilder(MapBuilderBase):

    def build(self, depth: int):
        rand: Random = ECS.scene.retrieve("random")
        self.depth = depth
        #self.builder = SimpleMapBuilder()
        self.builder = BSPDungeonBuilder()
        self.map, self.startPosition = self.builder.build(MAP_WIDTH, MAP_HEIGHT, depth, rand)
        self.snapshotHistory = self.builder.snapshotHistory

    def spawn(self):
        rand: Random = ECS.scene.retrieve("random")
        self.builder.spawn(ECS.scene, self.map, self.depth, rand)
