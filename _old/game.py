


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

