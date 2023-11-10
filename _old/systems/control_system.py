
from algorithms import Dimension
from algorithms.position import Point
from core import Game


class ControlComponent:
    def __init__(self, system: "ControlSystem"):
        self._enabled = True
        self.system = system
        system.components.append(self)
        self.lock = False
        self.leftPressed = False
        self.rightPressed = False

    def mouseLeft(
        self, down: bool, screenPosition: Point, worldPosition: Point
    ) -> bool:
        result = False
        if self.leftPressed and not down:
            result = self.mouseClick(screenPosition, worldPosition)
        self.leftPressed = down
        return result

    def mouseRight(
        self, down: bool, screenPosition: Point, worldPosition: Point
    ) -> bool:
        result = False
        if self.rightPressed and not down:
            result = self.mouseClickRight(screenPosition, worldPosition)
        self.rightPressed = down
        return result

    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        return False

    def mouseClickRight(
        self, screenPosition: Point, worldPosition: Point
    ) -> bool:
        return False

    def mousePosition(self, screenPosition: Point, worldPosition: Point) -> None:
        pass

    def keyPressed(self, keys: set[str]) -> bool:
        return False

    def tick(self) -> None:
        pass

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self._enabled = True
            self.system.components.append(self)
        if not value and self._enabled:
            self._enabled = False
            self.lock = False
            self.leftPressed = False
            self.rightPressed = False
            self.system.components.remove(self)

    def __repr__(self) -> str:
        return type(self).__name__

    def __str__(self) -> str:
        return type(self).__name__


class ControlSystem:
    def __init__(self, game: Game, units: Dimension = Dimension(1, 1)):
        self.game = game
        self.units = units
        self.lockControls = False
        w, h = game.device.dimension
        self.position: Point = Point(w // 2, h // 2)
        self.components: list[ControlComponent] = []
        self._enabled = False
        self.game.tickSystems.append(self)
        self._position: Point = Point()
        self._leftButtonEvent = False
        self._leftButton: tuple[bool, Point] = (False, Point())
        self._rightButtonEvent = False
        self._rightButton: tuple[bool, Point] = (False, Point())
        self._pressed: set[str] = set()
    
    @property
    def enabled(self):
        return self._enabled
    
    @enabled.setter
    def enabled(self, value):
        if not self._enabled and value:
            self._enabled = True
            self.registerlisteners()
        elif self._enabled and not value:
            self._leftButtonEvent = False
            self._rightButtonEvent = False
            self._enabled = False
            self.deregisterlisteners()
    
    def registerlisteners(self):
        self.game.device.onClick.append(self.mouseClick)
        self.game.device.onClickRight.append(self.mouseClickRight)
        self.game.device.onMove.append(self.mousePosition)
        self.game.device.onPressed.append(self.keyPressed)
    
    def deregisterlisteners(self):
        self.game.device.onClick.remove(self.mouseClick)
        self.game.device.onClickRight.remove(self.mouseClickRight)
        self.game.device.onMove.remove(self.mousePosition)
        self.game.device.onPressed.remove(self.keyPressed)

    def mouseClick(self, down: bool, screenPosition: Point) -> None:
        if self.enabled:
            self._leftButtonEvent = True
            self._leftButton = (down, screenPosition)

    def mouseClickRight(self, down: bool, screenPosition: Point) -> None:
        if self.enabled:
            self._rightButtonEvent = True
            self._rightButton = (down, screenPosition)

    def mousePosition(self, screenPosition: Point) -> None:
        if self.enabled:
            self._position = screenPosition

    def keyPressed(self, keyName: str) -> None:
        if self.enabled:
            self._pressed.add(keyName)

    def screenToWorldPosition(self, point: Point):
        w, h = self.units
        x, y = self.game.device.camera.translate
        return Point((point.x + x) // w, (point.y + y) // h)

    def tick(self):
        if not self.lockControls:
            leftEvent = self._leftButtonEvent
            self._leftButtonEvent = False
            if leftEvent:
                down, position = self._leftButton
                worldPosition = self.screenToWorldPosition(position)
                for i in range(len(self.components) - 1, -1, -1):
                    control = self.components[i]
                    if control.mouseLeft(down, position, worldPosition) or control.lock:
                        break

            rightEvent = self._rightButtonEvent
            self._rightButtonEvent = False
            if rightEvent:
                down, position = self._rightButton
                worldPosition = self.screenToWorldPosition(position)
                for i in range(len(self.components) - 1, -1, -1):
                    control = self.components[i]
                    if (
                        control.mouseRight(down, position, worldPosition)
                        or control.lock
                    ):
                        break

            keys = self._pressed.copy()
            self._pressed.clear()
            if keys:
                for i in range(len(self.components) - 1, -1, -1):
                    control = self.components[i]
                    if control.keyPressed(keys) or control.lock:
                        break

            movePosition = self._position
            worldPosition = self.screenToWorldPosition(movePosition)
            for i in range(len(self.components) - 1, -1, -1):
                control = self.components[i]
                control.mousePosition(movePosition, worldPosition)
                if control.lock:
                    break
            
            for i in range(len(self.components) - 1, -1, -1):
                control = self.components[i].tick()
