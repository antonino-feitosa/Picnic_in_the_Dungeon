


from algorithms.point import Point
from component import EntityMoved, EntryTrigger, Hidden, InflictsDamage, Name, Position, SingleActivation, sufferDamage
from core import ECS
from map import Map
from spawner import createParticle
from utils import Logger


def triggerSystem():
    map: Map = ECS.scene.retrieve("map")
    logger:Logger = ECS.scene.retrieve("logger")
    entities = ECS.scene.filter(EntityMoved.id | Position.id)
    for entity in entities:
        position:Position = entity[Position.id]
        point = Point(position.x, position.y)
        if point in map.tileContent:
            for tileEntity in map.tileContent[point]:
                if entity != tileEntity and tileEntity.has(EntryTrigger.id):
                    if tileEntity.has(Name.id):
                        name:Name = tileEntity[Name.id]
                        logger.log(f"{name.name} triggers!")
                    
                    if tileEntity.has(Hidden.id):
                        tileEntity.remove(Hidden.id)
                    
                    if tileEntity.has(InflictsDamage.id):
                        damage:InflictsDamage = tileEntity[InflictsDamage.id]
                        sufferDamage(entity, damage.damage)
                        position:Position = tileEntity[Position.id]
                        createParticle(ECS.scene, position.x, position.y, '!', (255, 90, 5, 255))
                    
                    if tileEntity.has(SingleActivation.id):
                        ECS.scene.destroy(tileEntity)
                    
        entity.remove(EntityMoved.id)
