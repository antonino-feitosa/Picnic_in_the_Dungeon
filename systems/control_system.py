from typing import Set
from algorithms import Dimension
from algorithms.position import Position
from core import Game


class ControlComponent:
    def __init__(self, system: "ControlSystem"):
        self._enabled = True
        self.system = system
        system.components.add(self)

    def mouseClick(self, screenPosition: Position, worldPosition: Position) -> bool:
        return False
    
    def mouseClickRight(self, screenPosition: Position, worldPosition: Position) -> bool:
        return False

    def mousePosition(self, screenPosition: Position, worldPosition: Position) -> None:
        pass

    @property
    def lock(self):
        return self.system.lockComponent is not None

    @lock.setter
    def lock(self, value):
        if value:
            self.system.lockControls = True
            self.system.lockComponent = self

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self._enabled = True
            self.system.components.add(self)
        if not value and self._enabled:
            self._enabled = False
            self.system.components.remove(self)


class ControlSystem:
    def __init__(self, game: Game, units: Dimension = Dimension(1,1)):
        self.game = game
        self.units = units
        self.lockControls = False
        w, h = game.device.dimension
        self.position: Position = Position(w//2, h//2)
        self.components: Set[ControlComponent] = set()
        self.enabled = True
        self.game.device.addListenerClick(self.mouseClick)
        self.game.device.addListenerClickRight(self.mouseClickRight)
        self.game.device.addListenerMove(self.mousePosition)
        self.game.tickSystems.append(self)
        self._position:Position = Position()
        self._lastPosition: Position = Position()
        self._click = False
        self._clickRight = False
        self._clickPosition:Position = Position()
        self._clickPositionRight:Position = Position()
        self.buttonLeftDown = False
        self.buttonRightDown = False
        self.lockComponent:ControlComponent | None = None

    def mouseClick(self, screenPosition: Position) -> None:
        if self.enabled:
            self._clickPosition = screenPosition
            self._click = True
    
    def mouseClickRight(self, screenPosition: Position) -> None:
        if self.enabled:
            self._clickPositionRight = screenPosition
            self._clickRight = True

    def mousePosition(self, screenPosition: Position) -> None:
        if self.enabled:
            self._position = screenPosition

    def screenToWorldPosition(self, point: Position):
        w, h = self.units
        x, y = self.game.device.camera.translate
        return Position((point.x + x) // w, (point.y + y) // h)

    def tick(self):
        position, click = self._clickPosition, self._click
        positionRight, clickRight = self._clickPositionRight, self._clickRight
        self._click = False
        self._clickRight = False
        movePosition = self._position

        if not self.lockControls:
            self.buttonLeftDown = self.game.device.buttonLeftDown
            self.buttonRightDown = self.game.device.buttonRightDown

            if click:
                worldPosition = self.screenToWorldPosition(position)
                for control in self.components.copy():
                    if control.mouseClick(position, worldPosition):
                        break
            
            if clickRight:
                worldPosition = self.screenToWorldPosition(positionRight)
                for control in self.components.copy():
                    if control.mouseClickRight(positionRight, worldPosition):
                        break

            worldPosition = self.screenToWorldPosition(movePosition)
            for control in self.components.copy():
                control.mousePosition(movePosition, worldPosition)
        
        elif self.lockComponent is not None:
            worldPosition = self.screenToWorldPosition(position)
            if click:
                if self.lockComponent.mouseClick(position, worldPosition):
                    self.lockControls = False
            
            if self.lockComponent.mousePosition(movePosition, worldPosition):
                self.lockControls = False

            if clickRight:
                worldPosition = self.screenToWorldPosition(positionRight)
                if self.lockComponent.mouseClickRight(positionRight, worldPosition):
                    self.lockControls = False

        if self.lockComponent is None and self.lockControls:
            self.lockControls = False
            self.lockComponent = None
            
