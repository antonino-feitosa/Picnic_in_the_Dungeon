
from algorithms import Direction, Point
from core import Entity, Game
from systems import MapSystem


class PositionComponent:
    def __init__(self, system: "PositionSystem", entity: Entity, position: Point):
        self.system = system
        self.entity = entity
        self.direction: Direction = Direction.Right
        self.position: Point = position
        self.enabled = True

    def move(self, direction: Direction) -> None:
        self.system.toMove.add((self, direction))

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.position.__str__()


class PositionSystem:
    def __init__(self, game: Game):
        self.game = game
        self.toMove: set[tuple[PositionComponent, Direction]] = set()
        game.updateSystems.append(self)
        self.enabled = True

    def update(self):
        self.ground: set[Point] = self.game[MapSystem].ground
        for component, direction in self.toMove:
            destination = component.position + direction
            component.direction = direction
            if destination in self.ground:
                component.position = destination
        self.toMove.clear()
