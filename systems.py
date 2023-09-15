
from typing import Set
from typing import Dict
from typing import List
from typing import Tuple
from typing import Callable

from core import Entity
from core import Component
from core import Subsystem

from device import Image
from device import Device
from device import Rectangle

from algorithms import Point
from algorithms import Direction
from algorithms import FieldOfView


class FieldOfViewComponent(Component['FieldOfViewSystem']):
    def __init__(self, system: 'FieldOfViewSystem', entity: 'Entity', radius: int):
        super().__init__(system, entity)
        self.radius = radius
        self.center: Point = Point(0, 0)
        self.visible: Set[Point] = set()
        self.removed: Set[Point] = set()
        self.included: Set[Point] = set()
    
    def setDirty(self) -> None:
        self.system.setChanged(self)


class FieldOfViewSystem(Subsystem[FieldOfViewComponent]):
    def __init__(self, ground: Set[Point]):
        super().__init__()
        self.ground: Set[Point] = ground
        self.changed: List[FieldOfViewComponent] = []
        self.algorithm = FieldOfView()
    
    def addEntity(self, entity: Entity, radius:int) -> 'FieldOfViewComponent':
        component = FieldOfViewComponent(self, entity, radius)
        self.changed.append(component)
        entity.addComponent(component)
        self.addComponent(component)
        return component

    def setChanged(self, component: FieldOfViewComponent) -> None:
        if component not in self.changed:
            self.changed.append(component)

    def update(self):
        for component in self.changed:
            center = component.center
            radius = component.radius
            last = component.visible
            component.removed.clear()
            component.included.clear()
            component.visible = self.algorithm.calculate(center, radius, self.ground)
            for pos in component.visible:
                if pos not in last:
                    component.included.add(pos)
            for pos in last:
                if pos not in component.visible:
                    component.removed.add(pos)
        self.changed.clear()


class RenderComponent(Component['RenderSystem']):
    def __init__(self, system: 'RenderSystem', entity: 'Entity', image: Image):
        super().__init__(system, entity)
        self.image = image
        self._position: Point = Point(0, 0)
    
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self.system.updatePosition(self, value)


class RenderSystem(Subsystem[RenderComponent]):
    def __init__(self, unitPixels: int):
        super().__init__()
        self.unitPixels = unitPixels
        self.positionToComponent:Dict[Point,RenderComponent] = dict()
        self.visible:Set[Point] = set()

    def addEntity(self, entity: Entity, image: Image, position: Point) -> 'RenderComponent':
        component = RenderComponent(self, entity, image)
        component.position = position
        self.positionToComponent[position] = component
        entity.addComponent(component)
        self.addComponent(component)
        return component

    def updatePosition(self, component:RenderComponent, position:Point) -> None:
        self.positionToComponent.pop(component.position, None)
        self.positionToComponent[position] = component
        component._position = position

    def update(self):
        for pos in self.visible:
            if pos in self.positionToComponent:
                render = self.positionToComponent[pos]
                viewPosition = Point(pos.x * self.unitPixels, pos.y * self.unitPixels)
                render.image.draw(viewPosition)


class PositionComponent(Component['PositionSystem']):
    def __init__(self, system: 'PositionSystem', entity: 'Entity', position: Point):
        super().__init__(system, entity)
        self.position = position
        self.onCollision: Callable[[
            Point, Entity | None], None] = lambda position, entity: None
        self.onMove: Callable[[Point,
                               Point], None] = lambda source, dest: None

    def move(self, direction: Direction) -> None:
        self.system.move(self, direction)


class PositionSystem(Subsystem[PositionComponent]):
    def __init__(self, ground: Set[Point]):
        super().__init__()
        self.ground = ground
        self.positionToEntity: Dict[Point,
                                    PositionComponent] = dict()
        self.componentsToMove: List[Tuple[PositionComponent, Direction]] = []

    def addEntity(self, entity: Entity, position: Point) -> PositionComponent:
        component = PositionComponent(self, entity, position)
        entity.addComponent(component)
        self.positionToEntity[position] = component
        self.addComponent(component)
        return component

    def move(self, component: PositionComponent, direction: Direction) -> None:
        self.componentsToMove.append((component, direction))

    def update(self):
        # TODO resolve dependencies
        for (component, direction) in self.componentsToMove:
            nextPosition = direction.next(component.position)
            if nextPosition not in self.ground:
                component.onCollision(nextPosition, None)
            elif nextPosition in self.positionToEntity:
                other = self.positionToEntity[nextPosition]
                component.onCollision(nextPosition, other.entity)
            else:
                oldPosition = component.position
                component.position = nextPosition
                self.positionToEntity.pop(oldPosition)
                self.positionToEntity[nextPosition] = component
                component.onMove(oldPosition, nextPosition)
        self.componentsToMove.clear()
