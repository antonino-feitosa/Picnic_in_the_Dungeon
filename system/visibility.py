

from algorithms import FieldOfView, Point
from algorithms.random import Random
from component import Hidden, Name, Player, Position, Viewshed
from core import ECS
from map import Map, TileType
from utils import Logger

RATE_PERCEPT_HIDDEN:float = 0.05

def visibilitySystem():
    map: Map = ECS.scene.retrieve("map")
    logger:Logger = ECS.scene.retrieve("logger")
    entities = ECS.scene.filter(Position.id | Viewshed.id)

    isOpaque = lambda x, y : map.tiles[Point(x,y)] == TileType.Wall if Point(x,y) in map.tiles else False
    fieldOfView = FieldOfView(8, isOpaque)

    for entity in entities:
        position: Position = entity[Position.id]
        viewshed:Viewshed = entity[Viewshed.id]
        if viewshed.dirty:
            fieldOfView.radius = viewshed.range
            viewshed.dirty = False
            viewshed.visibleTiles = fieldOfView.rayCasting(Point(position.x,position.y))

            if entity.has(Player.id):
                map.visibleTiles.clear()
                map.visibleTiles = viewshed.visibleTiles
                map.revealedTiles.update(map.visibleTiles)

                rand:Random = ECS.scene.retrieve("random")

                for point in viewshed.visibleTiles:
                    if point in map.tileContent:
                        for tileEntity in map.tileContent[point]:
                            if tileEntity.has(Hidden.id) and rand.nextDouble() < RATE_PERCEPT_HIDDEN:
                                tileEntity.remove(Hidden.id)
                                if tileEntity.has(Name.id):
                                    name:Name = tileEntity[Name.id]
                                    logger.log(f"You spotted a {name.name}.")
