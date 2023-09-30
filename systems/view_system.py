from core import Entity, Game
from typing import Dict, List, Set
from algorithms import Direction, FieldOfView, Position
from systems import PositionComponent, MapSystem


class ViewComponent:
    AngleCone = "cone"
    AngleRadial = "radial"
    AnglePeripheral = "peripheral"

    FormatOctal = "octal"
    FormatCircle = "circle"
    FormatSquare = "square"
    FormatDiamond = "diamond"

    def __init__(self, system: "ViewSystem", entity: Entity, radius: int):
        self.system = system
        self.entity = entity
        self.radius = radius
        self.focalDistance = 0
        self.visible: Set[Position] = set()
        self.angle = ViewComponent.AngleRadial
        self.format = ViewComponent.FormatOctal
        self._lastPosition = Position()

    def update(self):
        center = self.entity[PositionComponent].position
        if self._lastPosition != center:
            direction = self.entity[PositionComponent].direction
            self._lastPosition = center
            algorithm = self.system.algorithm
            self.system.visible = algorithm.rayCasting(center, direction)


class ViewSystem:
    def __init__(self, game: Game, lineOfSight: bool = False):
        self.game = game
        self.lineOfSight = lineOfSight
        self.algorithm = FieldOfView(1, self.game[MapSystem].ground)
        self.activeComponent: ViewComponent
        self.visible: Set[Position] = set()
        game.updateSystems.append(self)
        self.enabled = True

    def update(self):
        if self.lineOfSight:
            if self.activeComponent is not None:
                self.algorithm.ground = self.game[MapSystem].ground
                self.activeComponent.update()
        else:
            self.visible = self.game[MapSystem].ground

    def isVisible(self, component) -> bool:
        position = component.entity[PositionComponent].position
        return position in self.visible