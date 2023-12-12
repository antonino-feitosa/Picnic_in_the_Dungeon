import os
from typing import Callable

import pygame
import pygame.freetype


Color = tuple[int, int, int, int]


class DeviceError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Image:
    def __init__(self, device: "Device", image: pygame.Surface):
        self.device = device
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()

    def draw(self, x: int, y: int) -> None:
        self.device.drawImage(self, x, y)

    def fill(self, color: Color) -> None:
        self.image.fill(color)

    def clone(self) -> "Image":
        image = self.image.copy()
        return Image(self.device, image)

    def replaceColor(self, source: Color, destination: Color) -> None:
        imageDest = self.image.copy()
        pygame.transform.threshold(
            imageDest, self.image, source, set_color=destination, inverse_set=True
        )
        self.image = imageDest


class SpriteSheet:
    def __init__(self, sheet: Image, width: int, height: int):
        self.device = sheet.device
        self.sheet = sheet
        self.images: list[Image] = []
        for y in range(0, sheet.height, height):
            for x in range(0, sheet.width, width):
                rect = pygame.Rect(x, y, width, height)
                image = pygame.Surface(rect.size, pygame.SRCALPHA)
                image.blit(self.sheet.image, (0, 0), rect)
                self.images.append(Image(sheet.device, image))


class Font:
    def __init__(self, device: "Device", size: int, font: pygame.freetype.Font):
        self.font = font
        self.size = size
        self.device = device
        self.foreground: Color = (0, 0, 0, 255)
        self.background: Color = (0, 0, 0, 255)

    def _createImage(self, text: str) -> pygame.Surface:
        image, _ = self.font.render(text, self.foreground, self.background)
        return image

    def createImage(self, text: str) -> Image:
        image, _ = self.font.render(text, self.foreground, self.background)
        return Image(self.device, image)

    def drawAtImage(self, text: str, image: Image, x: int = 0, y: int = 0):
        surface = self._createImage(text)
        image.image.blit(surface, (x, y))

    def drawAtImageCenter(self, text: str, image: Image, xoff: int = 0, yoff=0):
        surface = self._createImage(text)
        x = (image.width - surface.get_width()) // 2 + xoff
        y = (image.height - surface.get_height()) // 2 + yoff
        image.image.blit(surface, (x, y))

    def drawAtScreen(self, text: str, x: int, y: int):
        textSurface = self._createImage(text)
        image = Image(self.device, textSurface)
        self.device.drawImage(image, x, y)

    def drawGlyph(self, glyph: str, x: int, y: int, size: int = 16) -> None:
        surface, rect = self.font.render(glyph, pygame.color.Color(self.foreground), pygame.color.Color(self.background))
        dx = (size+4)//2
        rect.x += x * dx
        rect.y = y * size + ((size - rect.y) if rect.h < size else 0)
        self.font.fgcolor = pygame.color.Color(self.foreground)
        self.device.screen.blit(surface, rect)

    def drawGlyphCenter(self, glyph: str, x: int, y: int, size: int = 16) -> None:
        surface, rect = self.font.render(glyph, pygame.color.Color(self.foreground), pygame.color.Color(self.background))
        dx = (size+4)//2
        rect.x += x * dx
        rect.y = y * size + (size - rect.h + 6)//2
        self.device.screen.blit(surface, rect)

    def screenGlyphPositionToIndex(self, x: int, y: int) -> tuple[int, int]:
        return (x // ((self.size+4)//2),  y // self.size)


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
    # TODO context
    def __init__(self, title: str = "", tick=60, width=800, height=600):
        pygame.init()
        pygame.display.set_caption(title)
        self.width = width
        self.height = height
        # flags = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((width, height), vsync=1)
        self.running = True
        self.tick = tick
        self.clock = pygame.time.Clock()
        self.onClick: list[Callable[[bool, int, int], None]] = []
        self.onClickRight: list[Callable[[bool, int, int], None]] = []
        self.onMove: list[Callable[[int, int], None]] = []
        self.onKeyPressed: list[Callable[[set[str]], None]] = []
        self.onLoop: list[Callable[[], None]] = []
        self._keys: set[str] = set()

    def loadImage(self, path: str) -> Image:
        try:
            image = pygame.image.load(path)
            return Image(self, image)
        except pygame.error as err:
            raise DeviceError(err)

    def loadSpriteSheet(self, path: str, width: int, height: int) -> SpriteSheet:
        image = self.loadImage(path)
        sheet = SpriteSheet(image, width, height)
        return sheet

    def loadFont(self, path: str, size: int) -> Font:
        try:
            font = pygame.freetype.Font(path, size)
            return Font(self, size, font)
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
        dim = (self.width, self.height)
        self.screen.fill(color, pygame.Rect((0, 0), dim))

    def loop(self) -> None:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                for callback in self.onMove:
                    callback(x, y)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                for callback in self.onClick:
                    callback(True, x, y)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                x, y = pygame.mouse.get_pos()
                for callback in self.onClickRight:
                    callback(True, x, y)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                x, y = pygame.mouse.get_pos()
                for callback in self.onClick:
                    callback(False, x, y)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                x, y = pygame.mouse.get_pos()
                for callback in self.onClickRight:
                    callback(False, x, y)

            if event.type == pygame.KEYDOWN and event.key:
                keyName = pygame.key.name(event.key)
                self._keys.add(keyName)

            if event.type == pygame.KEYUP and event.key:
                keyName = pygame.key.name(event.key)
                if keyName in self._keys:
                    self._keys.remove(keyName)

        if self._keys:
            for callback in self.onKeyPressed:
                callback(self._keys)

        for callback in self.onLoop:
            callback()

        self.clock.tick(self.tick)
