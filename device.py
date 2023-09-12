
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


class Camera:  # TODO
    def __init__(self):
        self.changed = False
        self._translate = (0, 0)
        self._scale = 1.0

    def visible(self) -> Rectangle:
        return Rectangle(0, 0, 0, 0)

    def translate(self, x: int, y: int) -> None:
        self._translate = (x, y)

    def zoom(self, scale: float) -> None:
        self._scale = scale


class Image:
    def __init__(self, device: 'Device', image: pygame.Surface):
        self.device = device
        self.image = image
        self.dimension = (image.get_width(), image.get_height())

    def draw(self, position: Tuple[int, int] = (0, 0)) -> None:
        self.device.screen.blit(self.image, position)


class SpriteSheet:
    def __init__(self, sheet: Image, dimension: Tuple[int, int]):
        self.device = sheet.device
        self.sheet = sheet
        self.images: List[Image] = []
        for y in range(0, sheet.dimension[1], dimension[1]):
            for x in range(0, sheet.dimension[0], dimension[0]):
                rect = pygame.Rect((x, y), dimension)
                image = pygame.Surface(rect.size).convert()
                image.blit(self.sheet.image, (0, 0), rect)
                self.images.append(Image(sheet.device, image))
        pass


class Canvas:
    def __init__(self, device: 'Device', dimension: Tuple[int, int]):
        self.device = device
        self.canvas = pygame.Surface(dimension)
        self.dimension = dimension

    def draw(self, image: Image, dest: Rectangle, source: Rectangle | None = None):
        destRect = pygame.Rect(dest.position, dest.endPosition)
        if source is None:
            sourceRect = pygame.Rect((0, 0), image.dimension)
        else:
            sourceRect = pygame.Rect(source.position, source.endPosition)
        self.canvas.blit(image.image, destRect, sourceRect)

    def toImage(self):
        return Image(self.device, self.canvas)


class Device:
    def __init__(self, title: str = '', dimension=(800, 600)):
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(dimension)
        self.running = True
        pass

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

    def reload(self) -> None:
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
