import os
import pygame
import pygame.freetype

from typing import Callable

from device import Font
from device import Image
from device import Music
from device import Sound
from device import SpriteSheet
from device import TiledCanvas

from algorithms import Point
from algorithms import Dimension


Color = tuple[int,int,int]

class DeviceError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Camera:
    def __init__(self, dimension: Dimension):
        self.dimension = dimension
        self.translate: Point = Point()

    def centralize(self, position: Point) -> None:
        self.translate = self.referenceToCenter(position)

    def referenceToCenter(self, position: Point) -> Point:
        width, height = self.dimension
        return Point(position.x - width // 2, position.y - height // 2)


class Device:
    def __init__(self, title: str = "", dimension=Dimension(800, 600), tick=60):
        pygame.init()
        pygame.display.set_caption(title)
        self.dimension: Dimension = dimension
        dim = (dimension.width, dimension.height)
        flags = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(dim, vsync=1)
        self.running = True
        self.camera = Camera(dimension)
        self.tick = tick
        self.clock = pygame.time.Clock()
        self.onClick: list[Callable[[bool, Point], None]] = []
        self.onClickRight: list[Callable[[bool, Point], None]] = []
        self.onMove: list[Callable[[Point], None]] = []
        self.onPressed: list[Callable[[str], None]] = []

    def loadTiledCanvas(
        self, pixelsUnit: Dimension, dimension: Dimension
    ) -> TiledCanvas:
        return TiledCanvas(self, pixelsUnit, dimension)

    def loadImage(self, path: str) -> Image:
        try:
            image = pygame.image.load(path)
            return Image(self, image)
        except pygame.error as err:
            raise DeviceError(err)

    def loadSpriteSheet(self, path: str, dimension: Dimension) -> SpriteSheet:
        image = self.loadImage(path)
        sheet = SpriteSheet(image, dimension)
        return sheet

    def loadFont(self, path: str, size: int) -> Font:
        try:
            font = pygame.freetype.Font(path, size)
            return Font(self, font)
        except pygame.error as err:
            raise DeviceError(err)

    def loadSound(self, path: str) -> Sound:
        try:
            sound = pygame.mixer.Sound(path)
            return Sound(sound)
        except pygame.error as err:
            raise DeviceError(err)

    def loadMusic(self, path: str, format="wav") -> Music:
        if os.path.isfile(path):
            return Music(path, format)
        else:
            raise DeviceError("Can not find the file: " + path)

    def drawImage(self, image: Image, position: Point) -> None:
        x, y = self.camera.translate
        translatedPosition = Point(position.x - x, position.y - y)
        self.drawImageAtScreen(image, translatedPosition)

    def drawImageAtScreen(self, image: Image, position: Point) -> None:
        width, height = self.dimension
        rect = pygame.Rect(position.x, position.y, width, height)
        self.screen.blit(image.image, dest=rect)

    def draw(self) -> None:
        pygame.display.flip()

    def clear(self, color=(0, 0, 0)) -> None:
        dim = (self.dimension.width, self.dimension.height)
        self.screen.fill(color, pygame.Rect((0, 0), dim))

    def loop(self) -> None:
        self.clock.tick(self.tick)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEMOTION:
                position = Point(*pygame.mouse.get_pos())
                for callback in self.onMove:
                    callback(position)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                position = Point(*pygame.mouse.get_pos())
                for callback in self.onClick:
                    callback(True, position)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                position = Point(*pygame.mouse.get_pos())
                for callback in self.onClickRight:
                    callback(True, position)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                position = Point(*pygame.mouse.get_pos())
                for callback in self.onClick:
                    callback(False, position)
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                position = Point(*pygame.mouse.get_pos())
                for callback in self.onClickRight:
                    callback(False, position)

            if event.type == pygame.KEYUP and event.key:
                keyName = pygame.key.name(event.key)
                for callback in self.onPressed:
                    callback(keyName)
