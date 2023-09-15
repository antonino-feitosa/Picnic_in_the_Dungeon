
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
        self.inclued: Set[Point] = set()
        self.isFreePosition: Callable[[Point], bool] = lambda _: False


class FieldOfViewSystem(Subsystem[FieldOfViewComponent]):
    def __init__(self, isFreePosition: Callable[[Point], bool]):
        self.isFreePosition: Callable[[Point], bool] = isFreePosition
        self.changed: List[FieldOfViewComponent] = []
        self.algorithm = FieldOfView()

    def setChanged(self, component: FieldOfViewComponent) -> None:
        self.changed.append(component)

    def update(self):
        for component in self.changed:
            center = component.center
            radius = component.radius
            free = component.isFreePosition
            component.removed = component.visible
            component.inclued.clear()
            component.visible = self.algorithm.calculate(center, radius, free)
            for pos in component.visible:
                if pos in component.removed:
                    component.removed.remove(pos)
                else:
                    component.inclued.add(pos)



class RenderComponent(Component['RenderSystem']):
    def __init__(self, system: 'RenderSystem', entity: 'Entity', image: Image):
        super().__init__(system, entity)
        self.image = image
        self.position: Point = Point(0, 0)


class RenderSystem(Subsystem[RenderComponent]):
    def __init__(self, pixelsUnit: int, device: Device):
        super().__init__()
        self.device = device
        self.pixelsUnit = pixelsUnit

    def addEntity(self, entity: Entity, image: Image, position: Point) -> 'RenderComponent':
        component = RenderComponent(self, entity, image)
        component.position = position
        entity.addComponent(component)
        self.addComponent(component)
        return component

    def update(self):
        # TODO replace viewPort by fieldOfView
        unit = self.pixelsUnit
        cameraPos = self.device.camera.translateVector
        dimension = self.device.dimension
        self.viewPort = Rectangle(
            cameraPos.x - unit,
            cameraPos.y - unit,
            cameraPos.x + dimension.width + unit,
            cameraPos.y + dimension.height + unit)
        pixelsUnit = self.pixelsUnit
        for render in self.components:
            position = Point(render.position.x * pixelsUnit,
                             render.position.y * pixelsUnit)
            if self.viewPort.contains(position.x, position.y):
                render.image.draw(position)


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
