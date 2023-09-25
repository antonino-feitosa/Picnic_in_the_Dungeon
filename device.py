import os
import pygame
import pygame.freetype

from typing import Set
from typing import List
from typing import Tuple
from typing import Callable

from algorithms import Point
from algorithms import Dimension


class DeviceError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Camera:
    def __init__(self, dimension: Dimension):
        self.dimension = dimension
        self.translate: Point = Point(0, 0)

    def centralize(self, position: Point) -> None:
        self.translate = self.referenceToCenter(position)

    def referenceToCenter(self, position: Point) -> Point:
        width, height = self.dimension
        return Point(position.x - width // 2, position.y - height // 2)


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


class SpriteSheet:
    def __init__(self, sheet: Image, dimension: Dimension):
        self.device = sheet.device
        self.sheet = sheet
        self.images: List[Image] = []
        for y in range(0, sheet.dimension.height, dimension.height):
            for x in range(0, sheet.dimension.width, dimension.width):
                rect = pygame.Rect((x, y), dimension)
                image = pygame.Surface(rect.size, pygame.SRCALPHA)
                image.blit(self.sheet.image, (0, 0), rect)
                self.images.append(Image(sheet.device, image))
        pass


class Font:
    def __init__(self, device: "Device", font: pygame.freetype.Font):
        self.font = font
        self.device = device
        self.foreground: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.background: Tuple[int, int, int, int] = (0, 0, 0, 0)

    def drawAtImage(self, text: str, image: Image, position: Point):
        surface = self._createSurface(text)
        image.image.blit(surface, position)

    def drawAtScreen(self, text: str, position: Point):
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
        dim = Dimension(dimension.width, dimension.height * len(renders))
        canvas = pygame.Surface(dim, pygame.SRCALPHA)
        y = 0
        for render in renders:
            canvas.blit(render, dest=(0, y))
            y += dimension.height
        return canvas


class TiledCanvas:
    def __init__(self, device: "Device", pixelsUnit: Dimension, dimension: Dimension):
        self.device = device
        self.dimension = dimension
        self.pixelsUnit = pixelsUnit
        sw, sh = self.pixelsUnit
        width, height = dimension
        screenDimension = Dimension(sw * width, sh * height)
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

    def clear(self, position: Point, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
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
        self.canvas.blit(image.image, position)

    def drawAtScreen(self, screenPosition: Point) -> None:
        self.device.drawImageAtScreen(self.toImage(), screenPosition)

    def toImage(self):
        return Image(self.device, self.canvas)


class InputListener:
    def __init__(self):
        self.device: "Device"

    def update(self, event) -> None:
        pass


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
        self.onMouseUp: Callable[[Point], None] = lambda _: None
        self.onMouseDown: Callable[[Point], None] = lambda _: None

    def update(self, event):
        if (
            event.type == pygame.MOUSEBUTTONUP and event.button == 1
        ):  # 1 for left button
            x, y = pygame.mouse.get_pos()
            offx, offy = self.device.camera.translate
            self.onMouseUp(Point(x + offx, y + offy))
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            offx, offy = self.device.camera.translate
            self.onMouseDown(Point(x + offx, y + offy))


class MouseDragListener(InputListener):
    def __init__(self):
        self.mouseDown = False
        self.lastPosition: Point = Point(0, 0)
        self.onMouseDrag: Callable[[Point, Point], None] = lambda source, dest: None

    def update(self, event):
        if self.mouseDown and event.type == pygame.MOUSEMOTION:
            position = Point(*pygame.mouse.get_pos())
            if position != self.lastPosition:
                self.onMouseDrag(self.lastPosition, position)
                self.lastPosition = position

        if self.mouseDown and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouseDown = False
            position = Point(*pygame.mouse.get_pos())
            if position != self.lastPosition:
                self.onMouseDrag(self.lastPosition, position)
                self.lastPosition = position

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.mouseDown:
                self.mouseDown = True
                self.lastPosition = Point(*pygame.mouse.get_pos())


class Device:
    def __init__(self, title: str = "", dimension=Dimension(800, 600), tick=60):
        pygame.init()
        pygame.display.set_caption(title)
        self.dimension: Dimension = dimension
        self.screen = pygame.display.set_mode(dimension)
        self.running = True
        self.camera = Camera(dimension)
        self.listeners: Set[InputListener] = set()
        self.tick = tick
        self.clock = pygame.time.Clock()

    def addListener(self, listener: InputListener) -> None:
        listener.device = self
        self.listeners.add(listener)

    def loadTiledCanvas(
        self, pixelsUnit: Dimension, dimension: Dimension
    ) -> TiledCanvas:
        return TiledCanvas(self, pixelsUnit, dimension)

    def loadImage(self, name: str, dir: str = ".") -> Image:
        try:
            path = os.path.join(dir, name)
            image = pygame.image.load(path)
            return Image(self, image)
        except pygame.error as err:
            raise DeviceError(err)

    def loadSpriteSheet(
        self, name: str, dimension: Dimension, dir: str = "."
    ) -> SpriteSheet:
        image = self.loadImage(name, dir)
        sheet = SpriteSheet(image, dimension)
        return sheet

    def loadFont(self, name: str, size: int, dir: str = ".") -> Font:
        try:
            path = os.path.join(dir, name)
            font = pygame.freetype.Font(path, size)
            return Font(self, font)
        except pygame.error as err:
            raise DeviceError(err)

    def drawImage(self, image: Image, position: Point) -> None:
        x, y = self.camera.translate
        translatedPosition = Point(position.x - x, position.y - y)
        self.drawImageAtScreen(image, translatedPosition)

    def drawImageAtScreen(self, image: Image, position: Point) -> None:
        width, height = self.dimension
        rect = pygame.Rect(position.x, position.y, width, height)
        self.screen.blit(image.image, dest=rect)

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
