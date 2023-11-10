

from algorithms import PathFinding, Point
from algorithms.direction import Direction
from component import Monster, Position, Viewshed, Name
from core import ECS
from map import Map


def monsterAISystem():
    entities = ECS.scene.filter(Position.id | Viewshed.id | Monster.id | Name.id)
    xplayer, yplayer = ECS.scene.retrieve("player position")
    map: Map = ECS.scene.retrieve("map")

    for entity in entities:
        view:Viewshed = entity[Viewshed.id]
        name:Name = entity[Name.id]
        position: Position = entity[Position.id]
        if Point(xplayer, yplayer) in view.visibleTiles:
            print(f"{name.name} shouts insults!")
            isExit = lambda point: point not in map.blocked
            astar = PathFinding(isExit, Direction.All)
            path = astar.searchPath(Point(position.x, position.y), Point(xplayer, yplayer))
            if len(path) >= 2:
                nextPosition = path[1]
                if nextPosition == Point(xplayer, yplayer):
                    print('Goes Attack!')
                else:
                    position.x = nextPosition.x
                    position.y = nextPosition.y
                    view.dirty = True
