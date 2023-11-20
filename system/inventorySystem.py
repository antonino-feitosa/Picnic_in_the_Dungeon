
from component import CombatStats, Consumable, InBackpack, Name, Player, Position, ProvidesHealing, WantsToUseItem, WantsToDropItem, WantsToPickupItem
from core import ECS, Entity
from utils import Logger


def itemCollectionSystem():
    entities = ECS.scene.filter(Position.id | Name.id | WantsToPickupItem.id)
    logger:Logger = ECS.scene.retrieve("logger")
    for entity in entities:
        wantsToPickup:WantsToPickupItem = entity[WantsToPickupItem.id]
        item = wantsToPickup.item
        item.remove(Position.id)
        entity.remove(WantsToPickupItem.id)
        item.add(InBackpack(entity))
        name:Name = entity[Name.id]
        itemName:Name = item[Name.id]
        logger.log(f"{name.name} pick up the {itemName.name}")

def itemUseSystem():
    entities = ECS.scene.filter(Name.id | WantsToUseItem.id | CombatStats.id)
    logger:Logger = ECS.scene.retrieve("logger")
    for entity in entities:
        wants:WantsToUseItem = entity[WantsToUseItem.id]
        entityItem = wants.potion
        stats:CombatStats = entity[CombatStats.id]

        if entityItem.has(ProvidesHealing.id):
            potion:ProvidesHealing = wants.potion[ProvidesHealing.id]
            stats.HP = min(stats.maxHP, stats.HP + potion.heal_amount)
            if entity.has(Player.id):
                logger.log(f"You drink the {entityItem[Name.id].name}, healing {potion.heal_amount} hp.")
        
        if entityItem.has(Consumable.id):
            ECS.scene.destroy(entityItem)
        entity.remove(WantsToUseItem.id)
        

def itemDropSystem():
    entities = ECS.scene.filter(Name.id | WantsToDropItem.id)
    logger:Logger = ECS.scene.retrieve("logger")
    player:Entity = ECS.scene.retrieve('player')
    for entity in entities:
        position = entity[Position.id]
        wants:WantsToDropItem = entity[WantsToDropItem.id]
        item:Entity = wants.item
        item.add(Position(position.x, position.y))
        item.remove(InBackpack.id)
        entity.remove(WantsToDropItem.id)
        if entity == player:
            logger.log(f"You drop the {item[Name.id].name}.")
