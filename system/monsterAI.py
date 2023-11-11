

from algorithms import PathFinding, Point
from algorithms.direction import Direction
from component import Monster, Position, Viewshed, Name, WantsToMelee
from core import ECS, Entity
from map import Map


def monsterAISystem():
    entities = ECS.scene.filter(Position.id | Viewshed.id | Monster.id | Name.id)
    player:Entity = ECS.scene.retrieve("player")
    playerPosition:Position = player[Position.id]
    playerPoint = Point(playerPosition.x, playerPosition.y)
    map: Map = ECS.scene.retrieve("map")
    logger:list[str] = ECS.scene.retrieve("logger")

    for entity in entities:
        view:Viewshed = entity[Viewshed.id]
        name:Name = entity[Name.id]
        position: Position = entity[Position.id]
        if playerPoint in view.visibleTiles:
            logger.append(f"{name.name} shouts insults!")
            isExit = lambda point: point not in map.blocked or point == playerPoint
            astar = PathFinding(isExit, Direction.All)
            path = astar.searchPath(Point(position.x, position.y), playerPoint)
            if len(path) >= 2:
                nextPoint = path[1]
                if nextPoint == playerPoint:
                    wantsToMelee = WantsToMelee(player)
                    entity.add(wantsToMelee)
                else:
                    map.blocked.remove(Point(position.x, position.y))
                    map.blocked.add(nextPoint)
                    position.x = nextPoint.x
                    position.y = nextPoint.y
                    view.dirty = True
                    
