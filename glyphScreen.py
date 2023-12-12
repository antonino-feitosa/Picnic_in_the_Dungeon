
import pygame
from algorithms.point import Point
from device import Color, Font


class GlyphScreen:

    class Render:
        def __init__(self, glyph: str, fgColor: Color = (255, 255, 255, 255), bgColor: Color = (0, 0, 0, 255)):
            self.glyph = glyph
            self.fgColor = fgColor
            self.bgColor = bgColor

    def __init__(self, width: int, height: int, font: Font) -> None:
        self.font = font
        self.width = width
        self.height = height
        self.xoff = 0
        self.yoff = 0
        self.dx = (self.font.size + 4)//2
        self.dy = self.font.size + 3
        self.screen: dict[Point, GlyphScreen.Render] = dict()

    def clear(self):
        self.screen.clear()

    def setGlyph(self, x: int, y: int, glyph: str, fgColor: Color = (255, 255, 255, 255), bgColor: Color = (0, 0, 0, 255)) -> None:
        point = Point(x, y)
        self.screen[point] = GlyphScreen.Render(glyph, fgColor, bgColor)

    def setForeground(self, x: int, y: int, fgColor: Color):
        point = Point(x, y)
        if point not in self.screen:
            self.screen[point] = GlyphScreen.Render(' ', fgColor)
        else:
            self.screen[point].fgColor = fgColor

    def setBackground(self, x: int, y: int, bgColor: Color):
        point = Point(x, y)
        if point not in self.screen:
            self.screen[point] = GlyphScreen.Render(' ', bgColor=bgColor)
        else:
            self.screen[point].bgColor = bgColor

    def screenPositionToGrid(self, x: int, y: int):
        return (x // self.dx - self.xoff, y // self.dy - self.yoff)

    def draw(self) -> None:
        for point in self.screen:
            render = self.screen[point]
            fg = pygame.color.Color(render.fgColor)
            bg = pygame.color.Color(render.bgColor)
            
            surface, rect = self.font.font.render(render.glyph, fg, bg)
            rect.x += (self.xoff + point.x) * self.dx
            rect.y = (self.yoff + point.y) * self.dy + (self.dy - rect.y)
            
            area = pygame.rect.Rect((self.xoff + point.x) * self.dx, (self.yoff + point.y) * self.dy, self.dx, self.dy )
            self.font.device.screen.fill(bg, area, special_flags = pygame.BLEND_RGBA_MAX)
            self.font.device.screen.blit(surface, rect, special_flags = pygame.BLEND_RGBA_MAX)
