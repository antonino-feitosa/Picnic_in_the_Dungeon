

from algorithms.point import Point
from component import BlocksTile, Position
from core import ECS
from map import Map


def mapIndexSystem():
    entities = ECS.scene.filter(Position.id | BlocksTile.id)
    map: Map = ECS.scene.retrieve("map")

    map.populateBlocked()
    for entity in entities:
        position:Position = entity[Position.id]
        map.blocked.add(Point(position.x, position.y))
