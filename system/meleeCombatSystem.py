
from component import CombatStats, DefenseBonus, Equipped, MeleePowerBonus, Name, WantsToMelee, doDamage
from core import ECS, Entity
from utils import Logger


def getOffensiveBonus(entity:Entity) -> int:
    offensiveBonus = 0
    powerBonusEntities = ECS.scene.filter(MeleePowerBonus.id | Equipped.id)
    for powerBonusEntity in powerBonusEntities:
        equipped:Equipped = powerBonusEntity[Equipped.id]
        if equipped.owner == entity:
            powerBonus:MeleePowerBonus = powerBonusEntity[MeleePowerBonus.id]
            offensiveBonus += powerBonus.power
    return offensiveBonus


def getDefensiveBonus(entity:Entity) -> int:
    defensiveBonus = 0
    defenseBonusEntities = ECS.scene.filter(DefenseBonus.id | Equipped.id)
    for defenseBonusEntity in defenseBonusEntities:
        equipped:Equipped = defenseBonusEntity[Equipped.id]
        if equipped.owner == entity:
            defenseBonus:DefenseBonus = defenseBonusEntity[DefenseBonus.id]
            defensiveBonus += defenseBonus.defense
    return defensiveBonus


def meleeCombatSystem():
    entities = ECS.scene.filter(WantsToMelee.id | Name.id | CombatStats.id)
    logger:Logger = ECS.scene.retrieve("logger")
    for entity in entities:
        combatStats = entity[CombatStats.id]
        if combatStats.HP > 0:

            wantsToMelee:WantsToMelee = entity[WantsToMelee.id]
            target = wantsToMelee.target

            offensiveBonus = getOffensiveBonus(entity)
            defensiveBonus = getDefensiveBonus(target)

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
