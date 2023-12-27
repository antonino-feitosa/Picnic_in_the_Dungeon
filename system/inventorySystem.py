
from algorithms.point import Point
from component import AreaOfEffect, CombatStats, Confusion, Consumable, Equippable, Equipped, GUIDescription, HungerClock, InBackpack, InflictsDamage, MagicMapper, Name, Player, Position, ProvidesFood, ProvidesHealing, WantsToRemoveItem, WantsToUseItem, WantsToDropItem, WantsToPickupItem, sufferDamage
from core import ECS, Entity
from map import Map
from spawner import createParticle
from utils import Logger


def itemCollectionSystem() -> None:
    entities = ECS.scene.filter(Position.id | Name.id | WantsToPickupItem.id)
    logger: Logger = ECS.scene.retrieve("logger")
    for entity in entities:
        wantsToPickup: WantsToPickupItem = entity[WantsToPickupItem.id]
        item = wantsToPickup.item
        item.remove(Position.id)
        entity.remove(WantsToPickupItem.id)
        item.add(InBackpack(entity))
        name: Name = entity[Name.id]
        itemName: Name = item[Name.id]
        logger.log(f"{name.name} pick up the {itemName.name}")
    # TODO equip empty slot


def itemUseSystem() -> None:
    entities = ECS.scene.filter(Name.id | WantsToUseItem.id | CombatStats.id)
    logger: Logger = ECS.scene.retrieve("logger")
    map: Map = ECS.scene.retrieve("map")
    for entity in entities:
        wants: WantsToUseItem = entity[WantsToUseItem.id]
        entityItem = wants.item
        stats: CombatStats = entity[CombatStats.id]


        targets: set[Entity] = set()
        if entityItem.has(AreaOfEffect.id):
            area: AreaOfEffect = entityItem[AreaOfEffect.id]
            if wants.target is not None:
                target = wants.target
                for x in range(-area.radius, area.radius + 1):
                    for y in range(-area.radius, area.radius + 1):
                        pos = Point(target.x - x, target.y - y)
                        content = map.tileContent[pos] if pos in map.tileContent else []
                        for entityTarget in content:
                            if entityTarget.has(CombatStats.id):
                                targets.add(entityTarget)
                        createParticle(ECS.scene, pos.x, pos.y, '░', (100, 50, 0, 255))

        elif wants.target is not None:
            target = wants.target
            content = map.tileContent[target] if target in map.tileContent else []
            for entityTarget in content:
                if entityTarget.has(CombatStats.id):
                    targets.add(entityTarget)
        else:
            targets.add(entity)


        if entityItem.has(ProvidesHealing.id):
            for target in targets:
                potion: ProvidesHealing = wants.item[ProvidesHealing.id]
                stats.HP = min(stats.maxHP, stats.HP + potion.heal_amount)
                if entity.has(Player.id):
                    logger.log(f"You drink the {entityItem[Name.id].name}, healing {potion.heal_amount} hp.")
            
                if target.has(Position.id):
                    position:Position = target[Position.id]
                    createParticle(ECS.scene, position.x, position.y, '♥', (0, 255, 0, 255))


        if entityItem.has(InflictsDamage.id):
            for target in targets:
                if target.has(CombatStats.id):
                    inflicts: InflictsDamage = entityItem[InflictsDamage.id]
                    sufferDamage(target, inflicts.damage)
                    if entity.has(Player.id):
                        itemName: Name = entityItem[Name.id]
                        targetName: Name = target[Name.id]
                        logger.log(f"You use {itemName.name} on {targetName.name}, inflicting {inflicts.damage} hp.")
                    
                    if target.has(Position.id):
                        position:Position = target[Position.id]
                        createParticle(ECS.scene, position.x, position.y, '!', (255, 0, 0, 255))


        if entityItem.has(Confusion.id):
            for target in targets:
                if target.has(CombatStats.id):
                    confusion: Confusion = entityItem[Confusion.id]
                    target.add(Confusion(confusion.turns))
                    if entity.has(Player.id):
                        itemName: Name = entityItem[Name.id]
                        targetName: Name = target[Name.id]
                        logger.log(f"You use {itemName.name} on {targetName.name}, confusing them.")
                
                if target.has(Position.id):
                    position:Position = target[Position.id]
                    createParticle(ECS.scene, position.x, position.y, '?', (255, 0, 255, 255))


        if entityItem.has(ProvidesFood.id):
            for target in targets:
                if target.has(HungerClock.id):
                    hunger:HungerClock = target[HungerClock.id]
                    hunger.hungerState = HungerClock.WELL_FED
                    hunger.duration = 20
                    if entity.has(Player.id):
                        logger.log(f"You eat the {entityItem[Name.id].name}.")
        

        if entityItem.has(MagicMapper.id):
            map.revealedTiles.update(map.tiles)
            logger.log("The map is revealed to you!")


        if entityItem.has(Equippable.id):
            toEquip: Equippable = entityItem[Equippable.id]
            unequipEntities = ECS.scene.filter(Name.id | Equipped.id)
            for unequipEntity in unequipEntities:
                unequipEquipped: Equipped = unequipEntity[Equipped.id]
                if unequipEquipped.owner == entity and unequipEquipped.slot == toEquip.slot:
                    unequipEntity.remove(Equipped.id)
                    unequipEntity.add(InBackpack(entity))
                    if entity.has(Player.id):
                        unequipName: Name = unequipEntity[Name.id]
                        logger.log(f"You unequip {unequipName.name}.")


            toEquipName: Name = entityItem[Name.id]
            logger.log(f"You equipped {toEquipName.name}.")

            entityItem.remove(InBackpack.id)
            entityItem.add(Equipped(entity, toEquip.slot))

        if entityItem.has(Consumable.id):
            ECS.scene.destroy(entityItem)
        entity.remove(WantsToUseItem.id)


def itemDropSystem() -> None:
    entities = ECS.scene.filter(Name.id | WantsToDropItem.id)
    logger: Logger = ECS.scene.retrieve("logger")
    player: Entity = ECS.scene.retrieve('player')
    for entity in entities:
        position = entity[Position.id]
        wants: WantsToDropItem = entity[WantsToDropItem.id]
        item: Entity = wants.item
        item.add(Position(position.x, position.y))
        item.remove(InBackpack.id)
        entity.remove(WantsToDropItem.id)
        if entity == player:
            logger.log(f"You drop the {item[Name.id].name}.")


def itemRemoveSystem() -> None:
    entities = ECS.scene.filter(Name.id | WantsToRemoveItem.id)
    logger: Logger = ECS.scene.retrieve("logger")
    player: Entity = ECS.scene.retrieve('player')
    for entity in entities:
        wants: WantsToRemoveItem = entity[WantsToRemoveItem.id]
        item: Entity = wants.item
        item.remove(Equipped.id)
        item.add(InBackpack(entity))
        entity.remove(WantsToRemoveItem.id)
        if entity == player:
            logger.log(f"You unequipped the {item[Name.id].name}.")
