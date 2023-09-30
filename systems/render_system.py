from typing import Set

from core import Game
from core import Entity

from device import Image

from systems import ViewSystem
from systems import PositionComponent

from algorithms import Position
from algorithms import Dimension


class RenderComponent:
    def __init__(self, system: "RenderSystem", entity: Entity, image: Image):
        self.system = system
        self.image = image
        self.entity = entity
        self.offset: Position = Position()
        self._enabled = True
        system.components.add(self)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.system.components.add(self)
                self._enabled = True
        else:
            if self._enabled:
                self.system.components.remove(self)
                self._enabled = False

    def draw(self):
        width, height = self.entity[PositionComponent].position
        uw, uh = self.system.pixelsUnit
        dx, dy = self.offset
        position = Position(width * uw + dx, height * uh + dy)
        self.image.draw(position)


class RenderSystem:
    def __init__(self, game: Game, pixelsUnit: Dimension):
        self.game = game
        self.pixelsUnit = pixelsUnit
        self.components: Set[RenderComponent] = set()
        self.enabled = True
        game.drawSystems.append(self)

    def draw(self):
        view = self.game[ViewSystem]
        for component in self.components:
            if view.isVisible(component):
                component.draw()
