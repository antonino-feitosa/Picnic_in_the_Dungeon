

from component import CombatStats, Player, SufferDamage, Name
from core import ECS
from utils import Logger

def damageSystem():
    entities = ECS.scene.filter(CombatStats.id | SufferDamage.id)
    for entity in entities:
        combatStats:CombatStats = entity[CombatStats.id]
        sufferDamage: SufferDamage = entity[SufferDamage.id]
        combatStats.HP -= sufferDamage.amount
        entity.remove(SufferDamage.id)


def deleteTheDead():
    entities = ECS.scene.filter(CombatStats.id)
    logger:Logger = ECS.scene.retrieve("logger")
    for entity in entities:
        combatStats:CombatStats = entity[CombatStats.id]
        if combatStats.HP < 1:
            if entity.has(Player.id):
                logger.log("You are dead!")
            else:
                ECS.scene.destroy(entity)
                if entity.has(Name.id):
                    name:Name = entity[Name.id]
                    logger.log(f"{name.name} is dead!")

