

class MotionSystem:
    def __init__(self, unitPixels: Dimension):
        self.unitPixels = unitPixels
        self.lockControls = False
        self.components: Set["MotionComponent"] = set()
        self.toMove: Set[Tuple[MotionComponent, Direction]] = set()
        self.moving: Set[Tuple[RenderComponent, Point, int]] = set()

    def update(self):
        for component, direction in self.toMove:
            positionComponent = component.entity[PositionComponent]
            controller = component.entity[AnimationControllerComponent]
            controller.playAnimation(str(("idle", direction)))
            if len(positionComponent.collided) > 0:
                controller.playAnimationInStack(
                    str(("collision", direction)), lockControls=True
                )
            else:
                spd = component.speed
                render = controller.getCurrentAnimation().render
                controller.playAnimationInStack(
                    str(("walk", direction)), lockControls=True
                )
                x, y = self.unitPixels
                delta = Point(x * direction.x // spd, y * direction.y // spd)
                self.moving.add((render, delta, spd - 1))
                render.offset = Point(x * -direction.x, y * -direction.y)
        self.toMove.clear()

    def updateOnline(self):
        lock = False
        if len(self.moving) > 0:
            moving: Set[Tuple[RenderComponent, Point, int]] = set()
            for render, delta, spd in self.moving:
                spd -= 1
                if spd == 0:
                    render.offset = Point(0, 0)
                    render.entity[MotionComponent].callback()
                else:
                    lock = True
                    x, y = render.offset
                    render.offset = Point(x + delta.x, y + delta.y)
                    moving.add((render, delta, spd))
            self.moving = moving
        self.lockControls = lock







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





class MotionComponent:
    def __init__(
        self,
        system: MotionSystem,
        position: PositionComponent,
        controller: "AnimationControllerComponent",
    ):
        self.system = system
        self.entity = position.entity
        self.controller = controller
        self.speed = 8
        self.direction = Direction.RIGHT
        system.components.add(self)
        self._enabled = True
        self.callback: Callable[[], None] = lambda: None

    def move(self, direction: Direction) -> None:
        self.entity[PositionComponent].move(direction)
        self.system.toMove.add((self, direction))
        self.direction = direction

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value:
            if not self._enabled:
                self.system.components.add(self)
                self._enabled = True
        else:
            if self._enabled:
                self.system.components.remove(self)
                self._enabled = False





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
