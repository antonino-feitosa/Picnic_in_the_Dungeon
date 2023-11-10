

from algorithms import FieldOfView, Point
from component import Monster, Player, Position, Viewshed, Name
from core import ECS
from map import Map, TileType


def monsterAISystem():
    entities = ECS.scene.filter(Position.id | Viewshed.id | Monster.id | Name.id)
    xplayer, yplayer = ECS.scene.retrieve("player position")

    for entity in entities:
        view:Viewshed = entity[Viewshed.id]
        name:Name = entity[Name.id]
        if Point(xplayer, yplayer) in view.visibleTiles:
            print(f"{name.name} shouts insults!")
