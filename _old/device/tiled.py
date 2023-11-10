import pygame

from typing import TYPE_CHECKING

from device import Image

if TYPE_CHECKING:
    from device import Device, Color

from algorithms import Point
from algorithms import Dimension


class TiledCanvas:
    def __init__(self, device: "Device", pixelsUnit: Dimension, dimension: Dimension):
        self.device = device
        self.dimension = dimension
        self.pixelsUnit = pixelsUnit
        sw, sh = self.pixelsUnit
        width, height = dimension
        screenDimension = (sw * width, sh * height)
        self.canvas = pygame.Surface(screenDimension, pygame.SRCALPHA)

    def _scale(self, position: Point) -> Point:
        x, y = position
        width, height = self.pixelsUnit
        return Point(x * width, y * height)

    def _getArea(self, position: Point):
        x, y = self._scale(position)
        width, height = self.pixelsUnit
        area = pygame.Rect(x, y, width, height)
        return area

    def clear(
        self, position: Point, color: Color = (0, 0, 0)
    ) -> None:
        area = self._getArea(position)
        self.canvas.fill(color, area)

    def shadow(self, position: Point, dark: int = 127) -> None:
        area = self._getArea(position)
        image = pygame.Surface((area.width, area.height)).convert_alpha()
        image.set_alpha(dark)
        self.canvas.blit(image, area)

    def draw(self, position: Point) -> None:
        position = self._scale(position)
        self.device.drawImage(self.toImage(), position)

    def drawAtCanvas(self, image: Image, position: Point) -> None:
        position = self._scale(position)
        x, y = position
        self.canvas.blit(image.image, (x, y))

    def drawAtScreen(self, screenPosition: Point) -> None:
        self.device.drawImageAtScreen(self.toImage(), screenPosition)

    def toImage(self):
        return Image(self.device, self.canvas)
