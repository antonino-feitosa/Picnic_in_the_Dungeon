
from component import CombatStats, DefenseBonus, Equipped, MeleePowerBonus, Name, WantsToMelee, doDamage
from core import ECS
from utils import Logger


def meleeCombatSystem():
    entities = ECS.scene.filter(WantsToMelee.id | Name.id | CombatStats.id)
    logger:Logger = ECS.scene.retrieve("logger")
    for entity in entities:
        combatStats = entity[CombatStats.id]
        if combatStats.HP > 0:

            offensiveBonus = 0
            powerBonusEntities = ECS.scene.filter(MeleePowerBonus.id | Equipped.id)
            for powerBonusEntity in powerBonusEntities:
                equipped:Equipped = powerBonusEntity[Equipped.id]
                if equipped.owner == entity:
                    powerBonus:MeleePowerBonus = powerBonusEntity[MeleePowerBonus.id]
                    offensiveBonus += powerBonus.power

            wantsToMelee:WantsToMelee = entity[WantsToMelee.id]
            target = wantsToMelee.target

            defensiveBonus = 0
            defenseBonusEntities = ECS.scene.filter(DefenseBonus.id | Equipped.id)
            for defenseBonusEntity in defenseBonusEntities:
                equipped:Equipped = defenseBonusEntity[Equipped.id]
                if equipped.owner == entity:
                    defenseBonus:DefenseBonus = defenseBonusEntity[DefenseBonus.id]
                    defensiveBonus += defenseBonus.defense

            print("Offensive", offensiveBonus, "Defensive", defensiveBonus)

            targetName:Name = target[Name.id]
            targetStats:CombatStats = target[CombatStats.id]
            damage = (combatStats.power + offensiveBonus) - (targetStats.defense + defensiveBonus)
            name:Name = entity[Name.id]
            if damage <= 0:
                logger.log(f"{name.name} is unable to hurt {targetName.name}")
            else:
                logger.log(f"{name.name} hits {targetName.name}, for {damage} hp.")
                doDamage(target, damage)
            entity.remove(WantsToMelee.id)
