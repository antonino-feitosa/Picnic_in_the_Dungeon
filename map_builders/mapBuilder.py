
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
        self.builder = rand.choice(self._builderTable())
        self.map, self.startPosition = self.builder.build(MAP_WIDTH, MAP_HEIGHT, depth, rand)
        self.snapshotHistory = self.builder.snapshotHistory

    def spawn(self):
        rand: Random = ECS.scene.retrieve("random")
        self.builder.spawn(ECS.scene, self.map, self.depth, rand)
    
    def _builderTable(self) -> list[MapBuilderBase]:
        builders: list[MapBuilderBase] = list()
        
        steelCave = SimpleMapBuilder()
        steelCave.minSize = 5
        steelCave.maxSize = 8
        steelCave.name = "Steel Cave"
        builders.append(steelCave)

        saarangMine = SimpleMapBuilder()
        saarangMine.minSize = 8
        saarangMine.maxSize = 12
        saarangMine.name = "Saraang Mine"
        builders.append(saarangMine)

        dalaranRuins = BSPDungeonBuilder()
        dalaranRuins.gap = 1
        dalaranRuins.minWidth = 5
        dalaranRuins.minHeight = 5
        dalaranRuins.name = "Dalaran Ruins"
        builders.append(dalaranRuins)

        buriedOasis = BSPDungeonBuilder()
        buriedOasis.gap = 5
        buriedOasis.minWidth = 7
        buriedOasis.minHeight = 5
        buriedOasis.name = "Buried Oasis"
        builders.append(buriedOasis)

        agamemnonCatacombs = BSPDungeonBuilder()
        agamemnonCatacombs.gap = 3
        agamemnonCatacombs.minWidth = 3
        agamemnonCatacombs.minHeight = 3
        agamemnonCatacombs.name = "Agamemnon's catacombs"
        builders.append(agamemnonCatacombs)

        hallsOfTorment = BSPDungeonBuilder()
        hallsOfTorment.gap = 1
        hallsOfTorment.minWidth = 10
        hallsOfTorment.minHeight = 10
        hallsOfTorment.name = "Halls of Torment"
        builders.append(hallsOfTorment)

        return builders
