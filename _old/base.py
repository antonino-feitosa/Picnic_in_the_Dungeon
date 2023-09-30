

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

