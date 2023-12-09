
from core import ECS
from device import Color, Font

class Logger:
    def __init__(self, font:Font, length:int, x:int, y:int):
        self.messages:list[str] = []
        self.x = x
        self.y = y
        self.font = font
        self.foreground:Color = (200, 200, 200, 255)
        self.background:Color = (0, 0, 0, 0)
        self.length = length
    
    def clear(self):
        self.messages.clear()
    
    def log(self, message:str) -> None:
        turn = ECS.scene.retrieve("turn")
        self.messages.append(f"Turn:{turn}: {message}")
        size = len(self.messages)
        if size > self.length:
            self.messages = self.messages[-self.length:]
    
    def print(self) -> None:
        font:Font = ECS.scene.retrieve("font")
        font.background = self.background
        font.foreground = self.foreground
        (ux, uy) = ECS.scene.retrieve("pixels unit")
        for i in range(len(self.messages)):
            message = self.messages[i]
            font.drawAtScreen(message, self.x, self.y + i * uy)
