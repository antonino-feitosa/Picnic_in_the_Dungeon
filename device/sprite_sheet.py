import pygame

from typing import List

from device import Image

from algorithms import Dimension


class SpriteSheet:
    def __init__(self, sheet: Image, dimension: Dimension):
        self.device = sheet.device
        self.sheet = sheet
        self.images: List[Image] = []
        width, height = dimension
        for y in range(0, sheet.dimension.height, height):
            for x in range(0, sheet.dimension.width, width):
                rect = pygame.Rect(x, y, width, height)
                image = pygame.Surface(rect.size, pygame.SRCALPHA)
                image.blit(self.sheet.image, (0, 0), rect)
                self.images.append(Image(sheet.device, image))
