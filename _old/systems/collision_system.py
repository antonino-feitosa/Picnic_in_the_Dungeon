
from core import Game
from core import Entity

from systems import MapSystem


from algorithms import Point
from algorithms import Direction

from systems import PositionComponent


class CollisionComponent:
    def __init__(self, system: "CollisionSystem", entity: Entity):
        self.system = system
        self.entity = entity
        self.passiveCollision: set[CollisionComponent] = set()
        self.activeCollision: CollisionComponent | None = None
        self.wallCollision: bool = False
        self.dependency: set[CollisionComponent] = set()
        self._enabled = True
        self.system.actualPosition[self.position] = self

    def move(self, direction: Direction):
        self.system.move(self, direction)

    @property
    def position(self) -> Point:
        return self.positionComponent.position

    @property
    def positionComponent(self) -> PositionComponent:
        return self.entity[PositionComponent]

    @property
    def collided(self) -> bool:
        return self.wallCollision or self.activeCollision is not None

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
                message = "Occupied position: "
                raise ValueError(message + str(self.position))
        if not value and self._enabled:
            del self.system.actualPosition[self.position]
            self._enabled = False

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.entity.__str__() + ' ' + str(self.position)


class CollisionSystem:
    def __init__(self, game: Game):
        self.game = game
        self.actualPosition: dict[Point, CollisionComponent] = dict()
        self.movingInDirection: dict[CollisionComponent, Direction] = dict()
        self.tryingToMove: set[CollisionComponent] = set()
        self.wallCollision: set[CollisionComponent] = set()
        game.updateSystems.append(self)
        self.enabled = True

    def update(self):
        for component in self.wallCollision:
            component.wallCollision = True
            component.dependency.clear()
        self.wallCollision.clear()
        
        self.resolveDependency()

        for component, direction in self.movingInDirection.items():
            component.positionComponent.direction = direction
            position = component.position
            destination = direction + position
            other = self.actualPosition[destination]
            other.passiveCollision.add(component)
            component.activeCollision = other
            component.dependency.clear()
            component.entity[PositionComponent].direction = direction
        self.movingInDirection.clear()
        

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
                    for next in component.dependency:
                        if next in self.movingInDirection:
                            self.tryingToMove.add(next)
                    component.dependency.clear()

    def move(self, component: CollisionComponent, direction: Direction) -> None:
        component.wallCollision = False
        component.activeCollision = None
        component.passiveCollision.clear()
        ground: set[Point] = self.game[MapSystem].ground
        destination = direction + component.position
        if destination in ground:
            self.movingInDirection[component] = direction
            if destination in self.actualPosition:
                other = self.actualPosition[destination]
                other.dependency.add(component)
            else:
                self.tryingToMove.add(component)
        else:
            self.wallCollision.add(component)
