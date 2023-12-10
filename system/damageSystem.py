

from algorithms.point import Point
from component import CombatStats, Player, Position, SufferDamage, Name
from core import ECS
from map import Map
from utils import Logger


def damageSystem():
    map: Map = ECS.scene.retrieve("map")
    entities = ECS.scene.filter(CombatStats.id | SufferDamage.id)
    for entity in entities:
        combatStats: CombatStats = entity[CombatStats.id]
        sufferDamage: SufferDamage = entity[SufferDamage.id]
        combatStats.HP -= sufferDamage.amount
        entity.remove(SufferDamage.id)
        if entity.has(Position.id):
            position: Position = entity[Position.id]
            map.bloodstains.add(Point(position.x, position.y))


def deleteTheDead():
    entities = ECS.scene.filter(CombatStats.id)
    logger: Logger = ECS.scene.retrieve("logger")
    for entity in entities:
        combatStats: CombatStats = entity[CombatStats.id]
        if combatStats.HP < 1:
            if entity.has(Player.id):
                logger.log("You are dead!")
            else:
                ECS.scene.destroy(entity)
                if entity.has(Name.id):
                    name: Name = entity[Name.id]
                    logger.log(f"{name.name} is dead!")
