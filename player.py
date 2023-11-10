from algorithms import Point
from component import Player, Position, Viewshed
from core import ECS
from map import Map, TileType


def tryMovePlayer(dx: int, dy: int):
    map: Map = ECS.scene.retrieve("map")
    entities = ECS.scene.filter(Position.id | Player.id | Viewshed.id)
    for entity in entities:
        position: Position = entity[Position.id]
        nextPoint = Point(position.x + dx, position.y + dy)
        if nextPoint not in map.blocked:
            position.x = nextPoint.x
            position.y = nextPoint.y
            view: Viewshed = entity[Viewshed.id]
            view.dirty = True
            ECS.scene.store("player position", (nextPoint.x, nextPoint.y))


def playerInput(keys: set[str]) -> bool:
    if "up" in keys or "k" in keys or "[8]" in keys:
        tryMovePlayer(0, -1)
    elif "down" in keys or "j" in keys or "[2]" in keys:
        tryMovePlayer(0, +1)
    elif "left" in keys or "h" in keys or "[4]" in keys:
        tryMovePlayer(-1, 0)
    elif "right" in keys or "l" in keys or "[6]" in keys:
        tryMovePlayer(+1, 0)
    elif "y" in keys or "[9]" in keys:
        tryMovePlayer(+1, -1)
    elif "u" in keys or "[7]" in keys:
        tryMovePlayer(-1, -1)
    elif "n" in keys or "[3]" in keys:
        tryMovePlayer(+1, +1)
    elif "b" in keys or "[1]" in keys:
        tryMovePlayer(-1, +1)
    else:
        return False
    return True
