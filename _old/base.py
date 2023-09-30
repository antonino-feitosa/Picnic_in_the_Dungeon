




class ControlComponentMove(ControlComponent):
    def __init__(self, system: "MouseControlSystem", game: Composition, loader: Loader):
        super().__init__()
        self.game = game
        self.radius = 12
        self.system = system
        self.pathSize = 3  # TODO num of moves, turn component
        _, h = loader.device.dimension
        height = h - loader.descriptionBackground.dimension.height
        width = loader.descriptionBackground.dimension.width

        self.position = Point(width - 30 - 16, height)
        self.imageIdle = loader.iconMove
        self.imageActive = loader.iconSelectedMove
        self.imageCurrent = self.imageIdle
        self.tooptip = "Move to Location"
        self.selectedEntity: Composition

        self._enabled = False
        self.active = False
        self._selectedPath: List[Point] = []

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

    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        result = False
        if self.active:
            self.active = False
            self.imageCurrent = self.imageIdle
            self.system.controlPathSelection.enabled = False
        else:
            activeSelection = self.system.activeSelection
            if activeSelection and self.clickInRadius(screenPosition):
                self.active = True
                self.imageCurrent = self.imageActive
                entity = self.system.controlUnitSelection.selectedEntity
                self.system.controlPathSelection.callback = self.performPath
                self.system.controlPathSelection.startSelection(entity)
                result = True
        return result

    def performPath(self, path: List[Point]) -> None:
        self.selectedPath = path
        self.system.controlPathSelection.callback = lambda _: None
        print('Move to', self.selectedPath)
        if len(self.selectedPath) > 0:
            entity = self.system.controlUnitSelection.selectedEntity
            entity[MotionComponent].callback = self.perform
            self.perform()

    def perform(self) -> None:
        entity = self.system.controlUnitSelection.selectedEntity
        if len(self.selectedPath) == 0:
            entity[MotionComponent].callback = lambda: None
        else:
            position = entity[PositionComponent].position
            next = self.selectedPath.pop(0)
            direction = relativeDirection(position, next)
            entity[MotionComponent].move(direction)
            self.system.updateGame()

    def draw(self) -> None:
        self.imageCurrent.drawAtScreen(self.position)

    def clickInRadius(self, clickPosition: Point) -> bool:
        offset = Point(self.position.x + self.radius, self.position.y + self.radius)
        distance = distanceEuclidean(clickPosition, offset)
        return distance <= self.radius



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











class MessageSystem:
    def __init__(self, loader: Loader):
        self.component: MessageComponent | None = None
        self.confirm = False
        self.cancel = False
        self.option = 0
        self.lockControls = False
        self._message = Message(loader)

    def showMessage(self, component: "MessageComponent") -> None:
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


##############################################################################
# Components
##############################################################################







class MessageComponent:
    def __init__(self, system: MessageSystem, text: str):
        self.text = text
        self.system = system
        self.confirmed = False
        self.canceled = False
        self.answer = 0

    def showMessage(self) -> None:
        self.system.showMessage(self)

    @property
    def enabled(self):
        pass

    @enabled.setter
    def enabled(self, value):
        pass
