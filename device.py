
import os
import pygame

from typing import List
from typing import Tuple


class DeviceError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Rectangle:
    def __init__(self, x: float, y: float, x2: float, y2: float):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.position = (x, y)
        self.endPosition = (x2, y2)
        self.dimension = (x2 - x, y2 - y)

    def contains(self, x: float, y: float):
        return not (x < self.x or x >= self.x2 or y < self.y or y >= self.y2)


class Camera:
    def __init__(self):
        self.translateVector = (0, 0)

    def translate(self, x: int, y: int) -> None:
        self.translateVector = (x, y)


class Image:
    def __init__(self, device: 'Device', image: pygame.Surface):
        self.device = device
        self.image = image
        self.dimension = (image.get_width(), image.get_height())

    def draw(self, position: Tuple[int, int] = (0, 0)) -> None:
        self.device.drawImage(self, position, self.dimension)


class SpriteSheet:
    def __init__(self, sheet: Image, dimension: Tuple[int, int]):
        self.device = sheet.device
        self.sheet = sheet
        self.images: List[Image] = []
        for y in range(0, sheet.dimension[1], dimension[1]):
            for x in range(0, sheet.dimension[0], dimension[0]):
                rect = pygame.Rect((x, y), dimension)
                image = pygame.Surface(rect.size, pygame.SRCALPHA)
                image.blit(self.sheet.image, (0, 0), rect)
                self.images.append(Image(sheet.device, image))
        pass


class Canvas:
    def __init__(self, device: 'Device', dimension: Tuple[int, int]):
        self.device = device
        self.canvas = pygame.Surface(dimension, pygame.SRCALPHA)
        self.dimension = dimension

    def drawAtCanvas(self, image: Image, dest: Rectangle) -> None:
        destRect = pygame.Rect(dest.position, dest.endPosition)
        self.canvas.blit(image.image, destRect)
    
    def draw(self, position: Tuple[int, int], dimension: Tuple[int, int] | None = None) -> None:
        dimension = dimension or self.dimension
        self.device.drawImage(self.toImage(), position, dimension)
    
    def toImage(self):
        return Image(self.device, self.canvas)


class Device:
    def __init__(self, title: str = '', dimension=(800, 600)):
        pygame.init()
        pygame.display.set_caption(title)
        self.dimension = dimension
        self.screen = pygame.display.set_mode(dimension)
        self.running = True
        self.camera = Camera()

    def loadCanvas(self, dimension: Tuple[int, int]) -> Canvas:
        return Canvas(self, dimension)

    def loadImage(self, name: str, dir: str = '.') -> Image:
        try:
            path = os.path.join(dir, name)
            image = pygame.image.load(path)
            return Image(self, image)
        except pygame.error as err:
            raise DeviceError(err)

    def loadSpriteSheet(self, name: str, dimension: Tuple[int, int], dir: str = '.') -> SpriteSheet:
        image = self.loadImage(name, dir)
        sheet = SpriteSheet(image, dimension)
        return sheet

    def drawImage(self, image:Image, position: Tuple[int, int], dimension: Tuple[int, int]) -> None:
        translate = self.camera.translateVector
        translatedPosition = (position[0] - translate[0], position[0] - translate[1])
        dest = pygame.Rect(translatedPosition, dimension)
        self.screen.blit(image.image, dest)

    def reload(self) -> None:
        pygame.display.flip()
    
    def update(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
