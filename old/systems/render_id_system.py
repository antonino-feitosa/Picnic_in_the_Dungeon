
from core import Game
from core import Entity

from systems import PositionComponent
from systems import WorldRenderSystem
from systems import WorldRenderComponent

from algorithms import Position
from algorithms import Dimension


class RenderIdComponent(WorldRenderComponent):

    def __init__(self, game: Game, entity: Entity, id: str):
        background = game.loadImage("image.tile.background.alpha.png").clone()
        font = game.loadFont("font.write.gadaj.otf", 8)
        font.foreground = (0,0,0,255)
        font.drawAtImageCenter(id, background)
        super().__init__(game[RenderIdSystem], entity, background)

    def draw(self):
        width, height = self.entity[PositionComponent].position
        dx, dy = self.entity[WorldRenderComponent].offset
        uw, uh = self.system.pixelsUnit
        position = Position(width * uw + dx, height * uh + dy)
        self.image.draw(position)


class RenderIdSystem(WorldRenderSystem):
    def __init__(self, game: Game, pixelsUnit: Dimension):
        super().__init__(game, pixelsUnit)
        self.enabled = True
