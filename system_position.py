
from coordinates import Position, Direction
from core import Entity, Game


class PositionComponent:
    def __init__(self, system: "PositionSystem", entity: Entity, position: Position):
        self.system = system
        self.entity = entity
        self.direction: Direction = Direction.Right
        self.position: Position = position
        self.enabled = True

    def move(self, direction: Direction) -> None:
        self.system.toMove.add((self, direction))

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.position.__str__()


class PositionSystem:
    def __init__(self, game:Game, ground: set[Position]):
        self.game = game
        self.ground = ground
        self.toMove: set[tuple[PositionComponent, Direction]] = set()
        game.updateSystems.append(self)
        self.enabled = True

    def update(self):
        for component, direction in self.toMove:
            destination = component.position + direction
            component.direction = direction
            if destination in self.ground:
                component.position = destination
        self.toMove.clear()
