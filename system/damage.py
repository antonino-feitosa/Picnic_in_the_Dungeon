

from component import CombatStats, Player, SufferDamage
from core import ECS

def damageSystem():
    entities = ECS.scene.filter(CombatStats.id | SufferDamage.id)
    for entity in entities:
        combatStats:CombatStats = entity[CombatStats.id]
        sufferDamage: SufferDamage = entity[SufferDamage.id]
        combatStats.HP -= sufferDamage.amount
        entity.remove(SufferDamage.id)


def deleteTheDead():
    entities = ECS.scene.filter(CombatStats.id)
    for entity in entities:
        combatStats:CombatStats = entity[CombatStats.id]
        if combatStats.HP < 1:
            if entity.has(Player.id):
                print("You are dead!")
            else:
                ECS.scene.destroy(entity)
