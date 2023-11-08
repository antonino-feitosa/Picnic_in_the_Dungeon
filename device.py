import os
from typing import Callable

import pygame
import pygame.freetype

from coordinates import Position, Dimension


Color = tuple[int, int, int]


class DeviceError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Image:
    def __init__(self, device: "Device", image: pygame.Surface):
        self.device = device
        self.image = image
        self.dimension = Dimension(image.get_width(), image.get_height())

    def draw(self, x: int, y: int) -> None:
        self.device.drawImage(self, x, y)

    def clone(self) -> "Image":
        image = self.image.copy()
        return Image(self.device, image)

    def replaceColor(self, source: Color, destination: Color):
        imageDest = self.image.copy()
        pygame.transform.threshold(
            imageDest, self.image, source, set_color=destination, inverse_set=True
        )
        self.image = imageDest


class SpriteSheet:
    def __init__(self, sheet: Image, dimension: Dimension):
        self.device = sheet.device
        self.sheet = sheet
        self.images: list[Image] = []
        width, height = dimension
        for y in range(0, sheet.dimension.height, height):
            for x in range(0, sheet.dimension.width, width):
                rect = pygame.Rect(x, y, width, height)
                image = pygame.Surface(rect.size, pygame.SRCALPHA)
                image.blit(self.sheet.image, (0, 0), rect)
                self.images.append(Image(sheet.device, image))


class Font:
    def __init__(self, device: "Device", font: pygame.freetype.Font):
        self.font = font
        self.device = device
        self.foreground: tuple[int, int, int, int] = (0, 0, 0, 255)
        self.background: tuple[int, int, int, int] = (0, 0, 0, 0)

    def drawAtImage(self, text: str, image: Image, position: Position):
        surface = self._createSurface(text)
        x, y = position
        image.image.blit(surface, (x, y))

    def drawAtImageCenter(self, text: str, image: Image, offset: Position = Position()):
        surface = self._createSurface(text)
        w, h = image.dimension
        x = (w - surface.get_width()) // 2 + offset.x
        y = (h - surface.get_height()) // 2 + offset.y
        image.image.blit(surface, (x, y))

    def drawAtScreen(self, text: str, x: int, y: int):
        textSurface = self._createSurface(text)
        image = Image(self.device, textSurface)
        self.device.drawImage(image, x, y)

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


class Sound:
    def __init__(self, sound: pygame.mixer.Sound):
        self.sound = sound

    def play(self):
        self.sound.play()

    def stop(self):
        self.sound.stop()

    @property
    def volume(self) -> float:
        return self.sound.get_volume()

    @volume.setter
    def volume(self, value) -> None:
        self.sound.set_volume(value)


class Music:
    def __init__(self, path: str, format: str):
        self.path = path
        self.format = format
        self.fadeIn = 0

    def play(self, fadeInMillis=0):
        self.fadeIn = fadeInMillis
        pygame.mixer.music.unload()
        pygame.mixer.music.load(self.path, self.format)
        pygame.mixer.music.play(1, fade_ms=self.fadeIn)

    def loop(self):
        pygame.mixer.music.play(-1, fade_ms=self.fadeIn)

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def fade(self, millis=1000):
        pygame.mixer.music.fadeout(millis)

    def stop(self):
        pygame.mixer.music.unload()
        pygame.mixer.music.stop()

    @property
    def isPlaying(self):
        return pygame.mixer.music.get_busy()

    @property
    def volume(self) -> float:
        return pygame.mixer.music.get_volume()

    @volume.setter
    def volume(self, value) -> None:
        pygame.mixer.music.set_volume(value)


class Device:
    def __init__(self, title: str = "", dimension=Dimension(800, 600), tick=60):
        pygame.init()
        pygame.display.set_caption(title)
        self.dimension: Dimension = dimension
        dim = (dimension.width, dimension.height)
        flags = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(dim, vsync=1)
        self.running = True
        self.tick = tick
        self.clock = pygame.time.Clock()
        self.onClick: list[Callable[[bool, Position], None]] = []
        self.onClickRight: list[Callable[[bool, Position], None]] = []
        self.onMove: list[Callable[[Position], None]] = []
        self.onPressed: list[Callable[[str], None]] = []
        self.onLoop: list[Callable[[], None]] = []

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

    def drawImage(self, image: Image, x: int, y: int) -> None:
        self.screen.blit(image.image, (x, y))

    def draw(self) -> None:
        pygame.display.flip()

    def clear(self, color=(0, 0, 0)) -> None:
        dim = (self.dimension.width, self.dimension.height)
        self.screen.fill(color, pygame.Rect((0, 0), dim))

    def loop(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEMOTION:
                position = Position(*pygame.mouse.get_pos())
                for callback in self.onMove:
                    callback(position)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                position = Position(*pygame.mouse.get_pos())
                for callback in self.onClick:
                    callback(True, position)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                position = Position(*pygame.mouse.get_pos())
                for callback in self.onClickRight:
                    callback(True, position)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                position = Position(*pygame.mouse.get_pos())
                for callback in self.onClick:
                    callback(False, position)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                position = Position(*pygame.mouse.get_pos())
                for callback in self.onClickRight:
                    callback(False, position)

            if event.type == pygame.KEYUP and event.key:
                keyName = pygame.key.name(event.key)
                for callback in self.onPressed:
                    callback(keyName)
        
        for callback in self.onLoop:
            callback()
        
        self.clock.tick(self.tick)

        
