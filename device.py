
import os
import pygame

from typing import Set
from typing import List
from typing import Tuple
from typing import Callable


class DeviceError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Rectangle:
    def __init__(self, x: int, y: int, x2: int, y2: int):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.position = (x, y)
        self.endPosition = (x2, y2)
        self.dimension = (x2 - x, y2 - y)

    def contains(self, x: int, y: int):
        return not (x < self.x or x >= self.x2 or y < self.y or y >= self.y2)


class Camera:
    def __init__(self):
        self.translateVector = (0, 0)

    def position(self) -> Tuple[int, int]:
        return self.translateVector

    def translate(self, x: int, y: int) -> None:
        self.translateVector = (x, y)


class Image:
    def __init__(self, device: 'Device', image: pygame.Surface):
        self.device = device
        self.image = image
        self.dimension = (image.get_width(), image.get_height())

    def draw(self, position: Tuple[int, int] = (0, 0)) -> None:
        self.device.drawImage(self, position, self.dimension)

    def drawAtScreen(self, position: Tuple[int, int] = (0, 0)) -> None:
        self.device.drawImageAtScreen(self, position, self.dimension)


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
    
    def clearRegion(self, rect: Rectangle) -> None:
        area = pygame.Rect(rect.position[0], rect.position[1], rect.dimension[0], rect.dimension[1])
        self.canvas.fill((0,0,0), area)

    def drawAtCanvas(self, image: Image, dest: Tuple[int,int]) -> None:
        self.canvas.blit(image.image, dest)

    def draw(self, position: Tuple[int, int], dimension: Tuple[int, int] | None = None) -> None:
        dimension = dimension or self.dimension
        self.device.drawImage(self.toImage(), position, dimension)

    def drawAtScreen(self, position: Tuple[int, int], dimension: Tuple[int, int] | None = None) -> None:
        dimension = dimension or self.dimension
        self.device.drawImageAtScreen(self.toImage(), position, dimension)

    def toImage(self):
        return Image(self.device, self.canvas)


class InputListener:
    def __init__(self):
        self.device: 'Device'

    def update(self, event) -> None: pass


class UpdateListener(InputListener):
    def __init__(self):
        self.onUpdate: Callable[[], None] = lambda: None

    def update(self, event) -> None:
        self.onUpdate()


class KeyboardListener(InputListener):
    def __init__(self, keys: Set[str]):
        self.onKeyUp: Callable[[str], None] = lambda _: None
        self.onKeyDown: Callable[[str], None] = lambda _: None
        self.keys = keys
        self.keys_code = set()
        for key_name in keys:
            self.keys_code.add(pygame.key.key_code(key_name))

    def update(self, event) -> None:
        if event.type == pygame.KEYUP and event.key in self.keys_code:
            key_name = pygame.key.name(event.key)
            self.onKeyUp(key_name)
        if event.type == pygame.KEYDOWN and event.key in self.keys_code:
            key_name = pygame.key.name(event.key)
            self.onKeyDown(key_name)


class MouseClickListener(InputListener):
    def __init__(self):
        self.onMouseUp: Callable[[Tuple[int, int]], None] = lambda _: None
        self.onMouseDown: Callable[[Tuple[int, int]], None] = lambda _: None

    def update(self, event):
        # left(1), middle(2), right(3)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            position = pygame.mouse.get_pos()
            translate = self.device.camera.translateVector
            self.onMouseUp((position[0] + translate[0],
                           position[1] + translate[1]))
        # left(1), middle(2), right(3)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            position = pygame.mouse.get_pos()
            translate = self.device.camera.translateVector
            self.onMouseDown(
                (position[0] + translate[0], position[1] + translate[1]))


class MouseDragListener(InputListener):
    def __init__(self):
        self.mouseDown = False
        self.lastPosition = (0, 0)
        self.onMouseDrag: Callable[[
            Tuple[int, int], Tuple[int, int]], None] = lambda source, dest: None

    def update(self, event):
        if self.mouseDown and event.type == pygame.MOUSEMOTION:
            position = pygame.mouse.get_pos()
            if position != self.lastPosition:
                self.onMouseDrag(self.lastPosition, position)
                self.lastPosition = position

        if self.mouseDown and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouseDown = False
            position = pygame.mouse.get_pos()
            if position != self.lastPosition:
                self.onMouseDrag(self.lastPosition, position)
                self.lastPosition = position

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.mouseDown:
                self.mouseDown = True
                self.lastPosition = pygame.mouse.get_pos()


class Device:
    def __init__(self, title: str = '', dimension=(800, 600), tick=60):
        pygame.init()
        pygame.display.set_caption(title)
        self.dimension = dimension
        self.screen = pygame.display.set_mode(dimension)
        self.running = True
        self.camera = Camera()
        self.listeners: Set[InputListener] = set()
        self.tick = tick
        self.clock = pygame.time.Clock()

    def addListener(self, listener: InputListener) -> None:
        listener.device = self
        self.listeners.add(listener)

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

    def drawImage(self, image: Image, position: Tuple[int, int], dimension: Tuple[int, int]) -> None:
        translate = self.camera.translateVector
        translatedPosition = (
            position[0] - translate[0], position[1] - translate[1])
        self.drawImageAtScreen(image, translatedPosition, dimension)

    def drawImageAtScreen(self, image: Image, position: Tuple[int, int], dimension: Tuple[int, int]) -> None:
        dest = pygame.Rect(position, dimension)
        self.screen.blit(image.image, dest)

    def reload(self) -> None:
        pygame.display.flip()

    def clear(self, color=(0, 0, 0)) -> None:
        self.screen.fill(color, pygame.Rect((0, 0), self.dimension))

    def update(self) -> None:
        self.clock.tick(self.tick)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for listener in self.listeners:
                listener.update(event)
