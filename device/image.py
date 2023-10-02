import pygame

from typing import Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from device import Device

from algorithms import Position
from algorithms import Dimension


class Image:
    def __init__(self, device: "Device", image: pygame.Surface):
        self.device = device
        self.image = image
        self.dimension = Dimension(image.get_width(), image.get_height())

    def draw(self, position: Position = Position(0, 0)) -> None:
        self.device.drawImage(self, position)

    def drawAtScreen(self, position: Position = Position(0, 0)) -> None:
        self.device.drawImageAtScreen(self, position)

    def clone(self) -> "Image":
        image = self.image.copy()
        return Image(self.device, image)

    def replaceColor(self, source: Tuple[int, int, int], destination: Tuple[int, int, int]):
        imageDest = self.image.copy()
        pygame.transform.threshold(imageDest, self.image, source, set_color=destination, inverse_set=True)
        self.image = imageDest
