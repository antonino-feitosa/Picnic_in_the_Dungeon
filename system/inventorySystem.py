
from component import InBackpack, Name, Position, WantsToPickupItem
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
