
from typing import Callable, List
from algorithms.direction import Direction
from algorithms.pathfinding import PathFinding
from core import Game
from core import Entity

from device import SpriteSheet

from algorithms import Position
from entities.animation import SimpleImage

from systems import ControlSystem
from systems import ControlComponent
from systems import CollisionSystem
from systems import PositionComponent

from entities import SimpleAnimation
from systems.map_system import MapSystem

class MessageInfoComponent(ControlComponent):
    def __init__(self, game: Game, system: ControlSystem, info:str):
        self.game = game
        self.system = system
        self.info = info
        self.callback: Callable[[],None] = lambda : None
        image = game.loadImage('_resources/image.gui.background.message.png')
        w, h = image.dimension
        width, height = self.game.device.dimension
        position = Position((width - w) // 2, (height - h) // 2)
        self._background = SimpleImage(game, image, position)
    
# https://all-free-download.com/font/





class Message:
    def __init__(self, loader:Loader):
        self.loader = loader
        self.background:Image = loader.messageBackground # 650 x 250
        self.currentMessage = 0
        w, h = self.loader.device.dimension
        self._messages: List[str] = ['']
        self._backgroundPosition = Point((w - 610)//2, h - 210)
        self._currentImage: Image
    
    def setMessages(self, messages: List[str] = ['']) -> None:
        self._messages = messages
        self._setMessage(0)
    
    def _setMessage(self, index:int) -> None:
        self._currentImage = self.background.clone()
        font = self.loader.textFont
        font.drawAtImage(self._messages[index], self._currentImage, Point(30,30))

    def nextMessage(self) -> None:
        if self.currentMessage < len(self._messages):
            self.currentMessage += 1
            self._setMessage(self.currentMessage)
    
    def previousMessage(self) -> None:
        if self.currentMessage > 0:
            self.currentMessage -= 1
            self._setMessage(self.currentMessage)

    def draw(self) -> None:
        self._currentImage.drawAtScreen(self._backgroundPosition)





 

class MessageComponent:
    def __init__(self, game: Game, system: ControlSystem, spriteSheet: SpriteSheet):
        self.text = text
        self.system = system
        self.confirmed = False
        self.canceled = False
        self.answer = 0

    def showMessage(self, text:str) -> None:
        self.system.showMessage(self)
    
    def showConfirm(self, text:str) -> None:
        self.system.showMessage(self)
    
    def showOptions(self, text:str) -> None:
        self.system.showMessage(self)

    @property
    def enabled(self):
        pass

    @enabled.setter
    def enabled(self, value):
        pass


class MessageSystem:
    def __init__(self, game:Game):
        self.component: MessageComponent | None = None
        self.confirm = False
        self.cancel = False
        self.option = 0
        self.lockControls = False
        self._message = Message(loader)

    def showMessage(self, component: MessageComponent) -> None:
        self._message.setMessages([component.text])
        self.component = component
        self.lockControls = True

    def draw(self):
        if self.component is not None:
            self._message.draw()

    def update(self):
        if self.component is not None:
            self.component.confirmed = self.confirm
            self.component.canceled = self.cancel
            self.component.answer = self.option
            self.component = None
        self.confirm = False
        self.cancel = False
        self.option = 0
        self.lockControls = False


