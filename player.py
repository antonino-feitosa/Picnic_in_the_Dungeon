from algorithms import Point
from component import CombatStats, EntityMoved, Item, Player, Position, Viewshed, WantsToMelee, WantsToPickupItem
from core import ECS
from map import Map, TileType


def tryMovePlayer(dx: int, dy: int):
    map: Map = ECS.scene.retrieve("map")
    entities = ECS.scene.filter(Position.id | Player.id | Viewshed.id)
    for entity in entities:
        position: Position = entity[Position.id]
        nextPoint = Point(position.x + dx, position.y + dy)

        tileContent = map.tileContent[nextPoint] if nextPoint in map.tileContent else []
        for potentialTarget in tileContent:
            if potentialTarget.has(CombatStats.id):
               wantsToMelee = WantsToMelee(potentialTarget)
               entity.add(wantsToMelee)

        if nextPoint not in map.blocked:
            position.x = nextPoint.x
            position.y = nextPoint.y
            view: Viewshed = entity[Viewshed.id]
            view.dirty = True
            entity.add(EntityMoved())
            ECS.scene.store("player position", (nextPoint.x, nextPoint.y))


def getItem():
    # TODO multiple items
    players = ECS.scene.filter(Position.id | Player.id)
    items = ECS.scene.filter(Position.id | Item.id)
    for player in players:
        playerPosition:Position = player[Position.id]
        for item in items:
            itemPosition:Position = item[Position.id]
            if playerPosition == itemPosition:
                pickUp = WantsToPickupItem(player, item)
                player.add(pickUp)
                return True
    return False
