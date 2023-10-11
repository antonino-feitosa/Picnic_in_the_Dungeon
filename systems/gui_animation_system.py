
from typing import Callable

from core import Game
from core import Entity

from device import SpriteSheet
from systems.screen_render_system import ScreenRenderComponent

from systems.render_id_system import RenderIdComponent

class GuiAnimationComponent:
    def __init__(self, system: "GuiAnimationSystem", entity: Entity, sheet: SpriteSheet):
        self.tickWait = 0
        self.loop = True
        self._tickCount = 0
        self._frameIndex = 0
        self.system = system
        self.animation = sheet
        self.entity = entity
        self._enabled = True
        self.system.components.add(self)
        self.callback: set[Callable[[], None]] = set()

    @property
    def finished(self):
        return not self.loop and self._frameIndex == len(self.animation.images) - 1

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

    def reload(self):
        self._tickCount = 0
        self._frameIndex = 0

    def tick(self):
        if self._tickCount >= self.tickWait:
            self._tickCount = 0
            nextFrame = self.animation.images[self._frameIndex]
            self.entity[ScreenRenderComponent].image = nextFrame
            length = len(self.animation.images)
            if self._frameIndex + 1 < length:
                self._frameIndex += 1
            else:
                for call in self.callback.copy():
                    call()
                if self.loop:
                    self._frameIndex = 0
        else:
            self._tickCount += 1
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return self.entity.__str__()


class GuiAnimationSystem:
    def __init__(self, game: Game):
        self.game = game
        self.components: set[GuiAnimationComponent] = set()
        self.enabled = True
        game.tickSystems.append(self)

    def tick(self):
        for component in self.components:
            component.tick()
