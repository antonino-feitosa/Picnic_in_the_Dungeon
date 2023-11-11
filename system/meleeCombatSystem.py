
from component import CombatStats, Name, WantsToMelee, doDamage
from core import ECS


def meleeCombatSystem():
    entities = ECS.scene.filter(WantsToMelee.id | Name.id | CombatStats.id)
    for entity in entities:
        combatStats = entity[CombatStats.id]
        if combatStats.HP > 0:
            wantsToMelee:WantsToMelee = entity[WantsToMelee.id]
            target = wantsToMelee.target
            targetName:Name = target[Name.id]
            targetStats:CombatStats = target[CombatStats.id]
            damage = combatStats.power - targetStats.defense
            name:Name = entity[Name.id]
            if damage <= 0:
                print(f"{name.name} is unable to hurt {targetName.name}")
            else:
                print(f"{name.name} hits {targetName.name}, for {damage} hp.")
                doDamage(target, damage)
            entity.remove(WantsToMelee.id)
