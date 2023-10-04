from typing import Set
from typing import Callable

from core import Game


class TimerComponent:
    def __init__(self, system: "TimerSystem", ticks: int):
        self.system = system
        self.loop = False
        self.callback: Callable[[], None] = lambda: None
        self.ticks = ticks
        self._count = 0
        self._enabled = True
        self.system.components.add(self)

    def tick(self):
        if self._count >= self.ticks:
            self.callback()
            self._count = 0
            if not self.loop:
                self.enabled = False
        else:
            self._count += 1

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self.system.components.add(self)
            self._enabled = True
        if not value and self._enabled:
            self.system.components.remove(self)
            self._enabled = False


class TimerSystem:
    def __init__(self, game: Game):
        self.game = game
        self.components: Set[TimerComponent] = set()
        self.enabled = True
        game.tickSystems.append(self)

    def tick(self):
        for component in self.components.copy():
            component.tick()
