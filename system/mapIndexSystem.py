

from algorithms.point import Point
from component import BlocksTile, Position
from core import ECS
from map import Map


def mapIndexSystem():
    entities = ECS.scene.filter(Position.id | BlocksTile.id)
    map: Map = ECS.scene.retrieve("map")

    map.populateBlocked()
    map.clearContentIndex()
    for entity in entities:
        position:Position = entity[Position.id]
        point = Point(position.x, position.y)
        map.blocked.add(point)
        content = map.tileContent[point] if point in map.tileContent else []
        content.append(entity)
        map.tileContent[point] = content
