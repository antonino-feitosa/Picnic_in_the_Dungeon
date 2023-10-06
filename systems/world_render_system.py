
from algorithms import Dimension, Position
from core import Entity, Game
from device import Image
from systems import PositionComponent, ScreenRenderComponent, ScreenRenderSystem, ViewSystem


class WorldRenderComponent(ScreenRenderComponent):
    def __init__(self, system: "WorldRenderSystem", entity: Entity, image: Image):
        super().__init__(system, entity, image)
        self.enabled = True

    def draw(self):
        width, height = self.entity[PositionComponent].position
        uw, uh = self.system.pixelsUnit
        dx, dy = self.offset
        position = Position(width * uw + dx, height * uh + dy)
        self.image.draw(position)


class WorldRenderSystem(ScreenRenderSystem):
    def __init__(self, game: Game, pixelsUnit: Dimension):
        super().__init__(game, set())
        self.pixelsUnit = pixelsUnit
        game.drawSystems.append(self)

    def draw(self):
        view = self.game[ViewSystem]
        for component in self.components:
            if view.isVisible(component):
                component.draw()
