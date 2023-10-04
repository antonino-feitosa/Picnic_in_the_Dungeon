
from typing import List, Set

from core import Game
from core import Entity

from device import Image

from algorithms import Position

class GuiRenderComponent:
    def __init__(self, system: "GuiRenderSystem", entity: Entity, image: Image):
        self.system = system
        self.image = image
        self.entity = entity
        self.position: Position = Position()
        system.components.append(self)
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.system.components.append(self)
                self._enabled = True
        else:
            if self._enabled:
                self.system.components.remove(self)
                self._enabled = False

    def draw(self):
        self.image.drawAtScreen(self.position)
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return self.entity.__str__()


class GuiRenderSystem:
    def __init__(self, game: Game):
        self.game = game
        self.components: List[GuiRenderComponent] = []
        self.enabled = True
        game.drawSystems.append(self)

    def draw(self):
        for component in self.components:
            component.draw()
