

from algorithms import FieldOfView, Point
from component import Player, Position, Viewshed
from core import ECS
from map import Map, TileType


def visibilitySystem():
    entities = ECS.scene.filter(Position.id | Viewshed.id)
    map: Map = ECS.scene.retrieve("map")

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
