
from typing import Set
from typing import Dict
from typing import List
from typing import Type

class Component:
    def __init__(self, system: 'Subsystem', entity: 'Entity'):
        self.system = system
        self.entity = entity

    def destroy(self):
        self.system.removeComponent(self)


class Entity:
    def __init__(self, game:'Game'):
        self.game = game
        self.components:Set[Component] = set()
    
    def addComponent(self, component:Component) -> None:
        self.components.add(component)

    def destroy(self):
        self.game.destroyEntity(self)

    def _applyDestroy(self):
        for component in self.components:
            component.destroy()


class Subsystem:
    def __init__(self):
        self.components: Set[Component] = set()

    def update(self):
        pass

    def addComponent(self, component: Component) -> None:
        self.components.add(component)

    def removeComponent(self, component: Component) -> None:
        self.components.remove(component)


class Game:
    def __init__(self):
        self.typeToSystem: Dict[type,Subsystem] = dict()
        self.systems: List[Subsystem] = []
        self.entitiesToDestroy: List[Entity] = []
    
    def addSystem(self, system: Subsystem) -> None:
        self.typeToSystem[type(system)] = system
        self.systems.append(system)
    
    def getSystem(self, typeOfSystem: Type) -> Subsystem:
        return self.typeToSystem[typeOfSystem]

    def destroyEntity(self, entity:Entity) -> None:
        self.entitiesToDestroy.append(entity)
    
    def update(self) -> None:
        if self.entitiesToDestroy:
            for entity in self.entitiesToDestroy:
                entity._applyDestroy()
            self.entitiesToDestroy.clear()
        
        for system in self.systems:
            system.update()
