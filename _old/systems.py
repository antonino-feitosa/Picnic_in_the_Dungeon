







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
