
from algorithms import Rectangle
from algorithms.dimension import Dimension

from core import Game

from algorithms import Position

from systems import ControlSystem
from systems import ControlComponent


class DragCameraComponent(ControlComponent):
    def __init__(self, game: Game, system: ControlSystem, dimension:Dimension):
        super().__init__(system)
        self.game = game
        self.speed = 3
        self.system = system
        self.dimension = dimension
        self.enabled = True
        self._lastPosition:Position = Position()

    def mousePosition(self, screenPosition: Position, worldPosition: Position) -> bool:
        if self.system.buttonRightDown:
            position = self.game.device.camera.translate
            source = self._lastPosition
            destination = screenPosition
            difference = Position(destination.x - source.x, destination.y - source.y)
            position = Position(position.x - difference.x, position.y - difference.y)
            self.game.device.camera.translate = position
            self.game.draw()
        self._lastPosition = screenPosition
        return self.system.buttonRightDown
        

class MoveCameraComponent(ControlComponent):
    def __init__(self, game: Game, system: ControlSystem, dimension:Dimension):
        super().__init__(system)
        self.game = game
        self.speed = 3
        self.system = system
        self.dimension = dimension
        self.enabled = True

    def mousePosition(self, screenPosition: Position, worldPosition: Position) -> bool:
        offset = Position()
        x, y = screenPosition
        base = 10
        width, height = self.dimension
        xlimit = base if y > base and y < height - base else 30
        ylimit = base if x > base and x < width - base else 30
        if screenPosition.x <= xlimit:
            offset.x = self.speed
        if screenPosition.x >= width -xlimit:
            offset.x = -self.speed
        if screenPosition.y <= ylimit:
            offset.y = self.speed
        if screenPosition.y >= height -ylimit:
            offset.y = -self.speed
        self.game.device.camera.translate += offset
        self.game.draw()
        return False