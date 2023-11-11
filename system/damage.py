

from component import CombatStats, Player, SufferDamage
from core import ECS
from map import Map

def damageSystem():
    entities = ECS.scene.filter(CombatStats.id | SufferDamage.id)
    for entity in entities:
        combatStats:CombatStats = entity[CombatStats.id]
        sufferDamage: SufferDamage = entity[SufferDamage.id]
        combatStats.HP -= sufferDamage.amount
        entity.remove(SufferDamage.id)


def deleteTheDead():
    entities = ECS.scene.filter(CombatStats.id)
    logger:list[str] = ECS.scene.retrieve("logger")
    for entity in entities:
        combatStats:CombatStats = entity[CombatStats.id]
        if combatStats.HP < 1:
            if entity.has(Player.id):
                logger.append("You are dead!")
            else:
                ECS.scene.destroy(entity)

