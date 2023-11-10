
from algorithms import Dimension

from core import Game

from algorithms import Point

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
        self._lastPosition:Point = Point()
        self.buttonRightDown = False
    
    def mouseRight(self, down: bool, screenPosition: Point, worldPosition: Point) -> bool:
        if down and not self.buttonRightDown:
            self.buttonRightDown = True
            return True
        if not down and self.buttonRightDown:
            self.buttonRightDown = False
            return True
        return False

    def mousePosition(self, screenPosition: Point, worldPosition: Point) -> bool:
        if self.buttonRightDown:
            position = self.game.device.camera.translate
            source = self._lastPosition
            destination = screenPosition
            difference = Point(destination.x - source.x, destination.y - source.y)
            position = Point(position.x - difference.x, position.y - difference.y)
            self.game.device.camera.translate = position
            self.game.draw()
        self._lastPosition = screenPosition
        return self.buttonRightDown
        

class MoveCameraComponent(ControlComponent):
    def __init__(self, game: Game, system: ControlSystem, dimension:Dimension):
        super().__init__(system)
        self.game = game
        self.speed = 3
        self.system = system
        self.dimension = dimension
        self.enabled = True

    def mousePosition(self, screenPosition: Point, worldPosition: Point) -> bool:
        offset = Point()
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