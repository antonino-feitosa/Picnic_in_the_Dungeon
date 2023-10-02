from typing import List
from typing import Tuple

from core import Game
from core import Entity

from systems import PositionComponent
from systems import RenderSystem
from systems import RenderComponent

from algorithms import Position
from algorithms import Dimension


class RenderIdComponent(RenderComponent):

    def __init__(self, game: Game, entity: Entity, id: str):
        background = game.loadImage("image.tile.background.alpha.png").clone()
        font = game.loadFont("font.write.gadaj.otf", 8)
        font.foreground = (0,0,0,255)
        font.drawAtImageCenter(id, background)
        super().__init__(game[RenderIdSystem], entity, background)

    def draw(self):
        super().draw()
        width, height = self.entity[PositionComponent].position
        dx, dy = self.entity[RenderComponent].offset
        uw, uh = self.system.pixelsUnit
        position = Position(width * uw + dx, height * uh + dy)
        self.image.draw(position)


class RenderIdSystem(RenderSystem):
    def __init__(self, game: Game, pixelsUnit: Dimension):
        super().__init__(game, pixelsUnit)
        self.enabled = True
