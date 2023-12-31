
from typing import Callable
from core import Game
from algorithms import Point
from entities.animation import GuiSimpleImage

from systems import ControlSystem
from systems import ControlComponent

class MessageInfoComponent(ControlComponent):
    def __init__(self, game: Game, system: ControlSystem):
        super().__init__(system)
        self.game = game
        self.system = system
        self.info = ''
        self.font = game.loadFont('font.write.gadaj.otf', 20)
        self.callback: Callable[[],None] = lambda : None
        self.image = game.loadImage('image.gui.background.message.png')
        w, h = self.image.dimension
        width, height = self.game.device.dimension
        position = Point((width - w) // 2, (height - h))
        self._background = GuiSimpleImage(game, self.image, position)
        self.enabled = False
        self.processing = False
    
    def showMessage(self, info:str):
        self.info = info
        image = self.image.clone()
        self.font.drawAtImage(info, image, Point(30,30))
        self._background.image = image
        self._background.enabled = True
        self.lock = True
        self.processing = True
        self.enabled = True
    
    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        if self.enabled and self.processing:
            self.enabled = False
            self.processing = False
            self._background.enabled = False
            self.callback()
            return True
        return False
