from typing import Set
from algorithms import Dimension
from algorithms.position import Position
from core import Game


class ControlComponent:
    def __init__(self, system: "ControlSystem"):
        self._enabled = True
        self.system = system
        system.components.add(self)

    def mouseClick(self, screenPosition: Position, worldPosition: Position) -> bool:
        return False

    def mouseMove(self, screenPosition: Position, worldPosition: Position) -> None:
        pass

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self._enabled = True
            self.system.components.add(self)
        if not value and self._enabled:
            self._enabled = False
            self.system.components.remove(self)


class ControlSystem:
    def __init__(self, game: Game, units: Dimension):
        self.game = game
        self.units = units
        self.lockControls = False
        self.position: Position = Position()
        self.components: Set[ControlComponent] = set()
        self.enabled = True
        self.game.device.addListenerClick(self.mouseClick)
        self.game.device.addListenerMove(self.mouseMove)

    def mouseClick(self, screenPosition: Position) -> None:
        if self.enabled and not self.lockControls:
            worldPosition = self.screenToWorldPosition(screenPosition)
            for control in self.components.copy():
                control.mouseClick(screenPosition, worldPosition)

    def mouseMove(self, screenPosition: Position) -> None:
        if self.enabled and not self.lockControls:
            worldPosition = self.screenToWorldPosition(screenPosition)
            for control in self.components.copy():
                control.mouseMove(screenPosition, worldPosition)

    def screenToWorldPosition(self, point: Position):
        w, h = self.units
        x, y = self.game.device.camera.translate
        return Position((point.x + x) // w, (point.y + y) // h)
