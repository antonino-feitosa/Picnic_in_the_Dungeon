from typing import Tuple
from typing import TYPE_CHECKING

import pygame
import pygame.freetype

from device import Image

if TYPE_CHECKING:
    from device import Device

from algorithms import Position
from algorithms import Dimension


class Font:
    def __init__(self, device: "Device", font: pygame.freetype.Font):
        self.font = font
        self.device = device
        self.foreground: Tuple[int, int, int, int] = (0, 0, 0, 255)
        self.background: Tuple[int, int, int, int] = (0, 0, 0, 0)

    def drawAtImage(self, text: str, image: Image, position: Position):
        surface = self._createSurface(text)
        x, y = position
        image.image.blit(surface, (x, y))
    
    def drawAtImageCenter(self, text: str, image: Image, offset:Position = Position()):
        surface = self._createSurface(text)
        w, h = image.dimension
        x = (w - surface.get_width())//2 + offset.x
        y = (h - surface.get_height())//2 + offset.y
        image.image.blit(surface, (x, y))

    def drawAtScreen(self, text: str, position: Position):
        textSurface = self._createSurface(text)
        image = Image(self.device, textSurface)
        self.device.drawImageAtScreen(image, position)

    def _createSurface(self, text: str):
        messages = text.split("\n")
        renders = []
        dimension = Dimension(0, 0)
        for msg in messages:
            image, rect = self.font.render(msg, self.foreground, self.background)
            renders.append(image)
            if rect.width > dimension.width:
                dimension = Dimension(rect.width, dimension.height)
            if rect.height > dimension.height:
                dimension = Dimension(dimension.width, rect.height)
        dim = (dimension.width, dimension.height * len(renders))
        canvas = pygame.Surface(dim, pygame.SRCALPHA)
        y = 0
        for render in renders:
            canvas.blit(render, dest=(0, y))
            y += dimension.height
        return canvas
