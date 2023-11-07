from typing import Callable

from core import Component, Entity, Game, System


class TimerComponent(Component["TimerSystem"]):
    def __init__(self, system: "TimerSystem", entity: Entity, ticks: int):
        super().__init__(system, entity)
        self.system = system
        self.loop = False
        self.callback: Callable[[], None] = lambda: None
        self.ticks = ticks
        self._count = 0
        self.enabled = True

    def tick(self):
        if self._count >= self.ticks:
            self.callback()
            self._count = 0
            if not self.loop:
                self.enabled = False
        else:
            self._count += 1


class TimerSystem(System["TimerComponent"]):
    def __init__(self, game: Game):
        super().__init__(game, set())
        game.tickSystems.append(self)

    def tick(self):
        for component in self.components.copy():
            component.tick()

