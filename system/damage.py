

from component import CombatStats, Player, SufferDamage, Name
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
    logger:list[str] = ECS.scene.retrieve("logger")
    turn:int  = ECS.scene.retrieve("turn")
    for entity in entities:
        combatStats:CombatStats = entity[CombatStats.id]
        if combatStats.HP < 1:
            if entity.has(Player.id):
                logger.append(f"Turn {turn}: You are dead!")
            else:
                ECS.scene.destroy(entity)
                if entity.has(Name.id):
                    name:Name = entity[Name.id]
                    logger.append(f"Turn {turn}: {name.name} is dead!")

