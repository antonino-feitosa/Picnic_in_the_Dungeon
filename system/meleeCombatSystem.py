
from component import CombatStats, DefenseBonus, Equipped, HungerClock, MeleePowerBonus, Name, Position, WantsToMelee, sufferDamage
from core import ECS, Entity
from spawner import createParticle
from utils import Logger


def getOffensiveBonus(entity:Entity) -> int:
    offensiveBonus = 0
    powerBonusEntities = ECS.scene.filter(MeleePowerBonus.id | Equipped.id)
    for powerBonusEntity in powerBonusEntities:
        equipped:Equipped = powerBonusEntity[Equipped.id]
        if equipped.owner == entity:
            powerBonus:MeleePowerBonus = powerBonusEntity[MeleePowerBonus.id]
            offensiveBonus += powerBonus.power
    
    if entity.has(HungerClock.id):
        hunger: HungerClock = entity[HungerClock.id]
        if hunger.hungerState == HungerClock.WELL_FED:
            offensiveBonus += 1

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
                sufferDamage(target, damage)
            entity.remove(WantsToMelee.id)
            
            if target.has(Position.id):
                position:Position = target[Position.id]
                createParticle(ECS.scene, position.x, position.y, '!', (255, 90, 5, 255))
