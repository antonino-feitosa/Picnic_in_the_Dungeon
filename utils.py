
from core import ECS
from device import Color, Font

class Logger:
    def __init__(self, font:Font, length:int, x:int, y:int):
        self.turn = 1
        self.messages:list[str] = []
        self.x = x
        self.y = y
        self.font = font
        self.foreground:Color = (200, 200, 200, 255)
        self.background:Color = (0, 0, 0, 0)
        self.length = length
    
    def log(self, message:str) -> None:
        self.messages.append(f"Turn:{self.turn}: {message}")
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
