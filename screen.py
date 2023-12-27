
import pygame

from enum import IntEnum
from algorithms.point import Point
from component import Renderable
from device import Font

TRANSPARENT = pygame.color.Color((255, 255, 255, 0))
BLACK = (0, 0, 0)


class ScreenLayer(IntEnum):
    BackgroundRevealed = 0
    FogRevealed = 1
    BackgroundVisible = 2
    FogVisible = 3
    BackgroundEffects = 4
    Items = 5
    Entities = 6
    ForegroundEffects = 7
    Interface = 8


class Screen:
    def __init__(self, width: int, height: int, font: Font) -> None:
        self.width = width
        self.height = height
        self.font = font
        self.camera = Point(0, 0)
        self.dx = (self.font.size + 4)//2
        self.dy = self.font.size + 3
        self.enableFOG = True
        self.layers: list[pygame.Surface] = list()
        self.tmp = pygame.Surface((width * self.dx, height * self.dy), pygame.SRCALPHA)
        for _ in ScreenLayer:
            surface = pygame.Surface((width * self.dx, height * self.dy), pygame.SRCALPHA)
            surface.fill(BLACK)
            self.layers.append(surface)
        self.revealed: list[list[bool]] = list()
        for y in range(height):
            self.revealed.append(list())
            for _ in range(width):
                self.revealed[y].append(False)

    def clear(self):
        for layer in [ScreenLayer.Items, ScreenLayer.Entities, ScreenLayer.ForegroundEffects, ScreenLayer.Interface]:
            self.layers[layer].fill(BLACK)

    def reset(self):
        for layer in ScreenLayer:
            self.layers[layer].fill(BLACK)
        for y in range(self.height):
            for x in range(self.width):
                self.revealed[y][x] = False

    def screenPositionToGrid(self, x: int, y: int) -> tuple[int, int]:
        return (x // self.dx - self.camera.x, y // self.dy - self.camera.y)

    def gridPositionToScreen(self, x: int, y: int) -> tuple[int, int]:
        return ((self.camera.x + x) * self.dx, (self.camera.y + y) * self.dy + 6)

    def setGlyph(self, layer: ScreenLayer, point: Point, render: Renderable) -> None:
        surface = self.layers[layer]
        fg = pygame.color.Color(render.foreground)
        bg = pygame.color.Color(render.background)

        textSurface, rect = self.font.font.render(render.glyph, fg, bg)
        rect.x += point.x * self.dx
        rect.y = point.y * self.dy + (self.dy - rect.y)

        area = pygame.rect.Rect(point.x * self.dx, point.y * self.dy, self.dx, self.dy)
        surface.fill(bg, area, special_flags=pygame.BLEND_RGBA_MAX)
        surface.blit(textSurface, rect, special_flags=pygame.BLEND_RGBA_MAX)

    def setVisible(self, points: set[Point]) -> None:
        if self.enableFOG:
            self.layers[ScreenLayer.FogVisible].fill((0, 0, 0))
            for p in points:
                area = pygame.rect.Rect(p.x * self.dx, p.y * self.dy, self.dx, self.dy)
                self.layers[ScreenLayer.FogVisible].fill(TRANSPARENT, area)
                if not self.revealed[p.y][p.x]:
                    self.revealed[p.y][p.x] = True
                    self.layers[ScreenLayer.FogRevealed].fill(TRANSPARENT, area)
    
    def setRevealed(self, points: set[Point]) -> None:
        if self.enableFOG:
            for p in points:
                if not self.revealed[p.y][p.x]:
                    self.revealed[p.y][p.x] = True
                    area = pygame.rect.Rect(p.x * self.dx, p.y * self.dy, self.dx, self.dy)
                    self.layers[ScreenLayer.FogRevealed].fill(TRANSPARENT, area)

    def draw(self):
        screen = self.font.device.screen
        screen.fill((0, 0, 0))
        point = (self.camera.x * self.dx, self.camera.y * self.dy)

        tmp = self.tmp
        tmp.fill((0, 0, 0))

        layer = self.layers[ScreenLayer.BackgroundRevealed]
        screen.blit(layer, point)
        layer = self.layers[ScreenLayer.FogRevealed]
        screen.blit(layer, point, special_flags=pygame.BLEND_MIN)

        layer = self.layers[ScreenLayer.BackgroundVisible]
        tmp.blit(layer, (0, 0))
        layer = self.layers[ScreenLayer.FogVisible]
        tmp.blit(layer, (0, 0), special_flags=pygame.BLEND_MIN)
        screen.blit(tmp, point, special_flags=pygame.BLEND_ADD)

        tmp.fill((0, 0, 0))
        layer = self.layers[ScreenLayer.BackgroundEffects]
        tmp.blit(layer, (0, 0))
        layer = self.layers[ScreenLayer.FogVisible]
        tmp.blit(layer, (0, 0), special_flags=pygame.BLEND_MIN)
        screen.blit(tmp, point, special_flags=pygame.BLEND_ADD)

        for current in [ScreenLayer.Items, ScreenLayer.Entities, ScreenLayer.ForegroundEffects]:
            layer = self.layers[current]
            screen.blit(layer, point, special_flags=pygame.BLEND_MAX)

    def drawInterface(self):
        screen = self.font.device.screen
        point = (self.camera.x * self.dx, self.camera.y * self.dy)
        layer = self.layers[ScreenLayer.Interface]
        screen.blit(layer, point, special_flags=pygame.BLEND_MAX)
