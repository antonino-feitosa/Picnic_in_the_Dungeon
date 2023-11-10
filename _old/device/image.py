import pygame

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from device import Device, Color

from algorithms import Point
from algorithms import Dimension

class Image:
    def __init__(self, device: "Device", image: pygame.Surface):
        self.device = device
        self.image = image
        self.dimension = Dimension(image.get_width(), image.get_height())

    def draw(self, position: Point = Point(0, 0)) -> None:
        self.device.drawImage(self, position)

    def drawAtScreen(self, position: Point = Point(0, 0)) -> None:
        self.device.drawImageAtScreen(self, position)

    def clone(self) -> "Image":
        image = self.image.copy()
        return Image(self.device, image)

    def replaceColor(self, source: Color, destination: Color):
        imageDest = self.image.copy()
        pygame.transform.threshold(imageDest, self.image, source, set_color=destination, inverse_set=True)
        self.image = imageDest
