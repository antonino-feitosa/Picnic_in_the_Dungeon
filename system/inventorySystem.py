
from component import CombatStats, InBackpack, Name, Player, Position, Potion, WantsToDrinkPotion, WantsToPickupItem
from core import ECS
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

def potionUseSystem():
    entities = ECS.scene.filter(Name.id | WantsToDrinkPotion.id | CombatStats.id)
    logger:Logger = ECS.scene.retrieve("logger")
    for entity in entities:
        wants:WantsToDrinkPotion = entity[WantsToDrinkPotion.id]
        stats:CombatStats = entity[CombatStats.id]
        potion:Potion = wants.potion[Potion.id]
        stats.HP = min(stats.maxHP, stats.HP + potion.heal_amount)
        if entity.has(Player.id):
            logger.log(f"You drink the {wants.potion[Name.id].name}, healing {potion.heal_amount} hp.")
        ECS.scene.destroy(wants.potion)
        entity.remove(WantsToDrinkPotion.id)
        
