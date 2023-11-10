
from core import Game, Entity, Component, System

from device import Image

from algorithms import Point

class ScreenRenderComponent(Component):
    def __init__(self, system: "ScreenRenderSystem", entity: Entity, image: Image):
        super().__init__(system, entity)
        self.system = system
        self.image = image
        self.offset: Point = Point()
        self.enabled = True

    def draw(self):
        self.image.drawAtScreen(self.offset)


class ScreenRenderSystem(System[ScreenRenderComponent]):
    def __init__(self, game: Game, components: set[ScreenRenderComponent] | list[ScreenRenderComponent]):
        super().__init__(game, components)
        game.drawSystems.append(self)

    def draw(self):
        for component in self.components:
            component.draw()
