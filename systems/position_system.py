from core import Game
from core import Entity

from typing import Set
from typing import Dict
from typing import List
from typing import Tuple

from algorithms import Position
from algorithms import Direction

from systems import MapSystem


class PositionComponent:
    def __init__(self, system: "PositionSystem", entity: Entity, position: Position):
        self.system = system
        self.entity = entity
        self.direction: Direction = Direction.Right
        self.position: Position = position

    def move(self, direction: Direction) -> None:
        self.system.toMove.add((self, direction))

    @property
    def enabled(self):
        return True

    @enabled.setter
    def enabled(self, value):
        pass

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return self.entity.__str__()

class PositionSystem:
    def __init__(self, game: Game):
        self.game = game
        self.toMove: Set[Tuple[PositionComponent, Direction]] = set()
        game.updateSystems.append(self)
        self.enabled = True

    def update(self):
        self.ground: Set[Position] = self.game[MapSystem].ground
        for component, direction in self.toMove:
            destination = component.position + direction
            component.direction = direction
            if destination in self.ground:
                component.position = destination
        self.toMove.clear()
