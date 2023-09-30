
from typing import Set
from typing import Dict
from typing import List
from typing import Deque
from typing import Tuple

from collections import deque


from core import Game
from core import Entity

from systems import MapSystem


from algorithms import Position
from algorithms import Direction

from systems import PositionComponent

class CollisionComponent:
    def __init__(self, system:'CollisionSystem', entity: Entity):
        self.system = system
        self.entity = entity
        self.passiveCollision:Set[CollisionComponent] = set()
        self.activeCollision: CollisionComponent | None = None
        self.wallCollision:bool = False
        self.dependency: Set[CollisionComponent] = set()
        self._enabled = True
        self.system.actualPosition[self.position] = self

        # override move on Position Component
        self.entity[PositionComponent].move = self.move
    
    def move(self, direction:Direction):
        self.wallCollision = False
        self.activeCollision = None
        self.passiveCollision.clear()
        self.system.move(self, direction)
    
    @property
    def position(self) -> Position:
        return self.positionComponent.position
    
    @property
    def positionComponent(self) -> PositionComponent:
        return self.entity[PositionComponent]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value) -> None:
        if value and not self._enabled:
            if self.position not in self.system.actualPosition:
                self.system.actualPosition[self.position] = self
                self._enabled = True
            else:
                raise ValueError('Can not collision on an occupied position: ' + str(self.position))
        if not value and self._enabled:
            del self.system.actualPosition[self.position]
            self._enabled = False

class CollisionSystem:
    def __init__(self, game: Game):
        self.game = game
        self.actualPosition: Dict[Position, CollisionComponent] = dict()
        self.movingInDirection: Dict[CollisionComponent, Direction] = dict()
        self.tryingToMove: Set[CollisionComponent] = set()
        game.updateSystems.append(self)
        self.enabled = True

    def update(self):
        self.resolveDependency()
        for component, direction in self.movingInDirection.items():
            component.positionComponent.direction = direction
            position = component.position
            destination = direction + position
            other = self.actualPosition[destination]
            other.passiveCollision.add(component)
            component.activeCollision = other
            component.dependency.clear()
        
    def resolveDependency(self):
        while self.tryingToMove:
            component = self.tryingToMove.pop()
            position = component.position
            direction = self.movingInDirection[component]
            destination = direction + position
            if destination in self.actualPosition:
                other = self.actualPosition[destination]
                other.dependency.add(component)
            else:
                del self.movingInDirection[component]
                del self.actualPosition[position]
                self.actualPosition[destination] = component
                component.positionComponent.position = destination
                component.positionComponent.direction = direction
                if component.dependency:
                    first = component.dependency.pop() # TODO randomize or initiative
                    self.tryingToMove.add(first)
                    component.dependency.clear()

    def move(self, component:CollisionComponent, direction:Direction) -> None:
        ground: Set[Position] = self.game[MapSystem].ground
        destination = direction + component.position
        if destination in ground:
            self.movingInDirection[component] = direction
            if destination in self.actualPosition:
                self.actualPosition[destination].dependency.add(component)
            else:
                self.tryingToMove.add(component)
        else:
            component.wallCollision = True
