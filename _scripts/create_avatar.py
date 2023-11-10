import sys

import pygame


sys.path.append("..")

from algorithms import Dimension
from algorithms import Point

from device import Device

color = (255, 255, 255, 255)

units = Dimension(32, 32)

device = Device("Test", Dimension(640, 480), tick=8)

sprite = device.loadSpriteSheet("../_resources/right.png", units)


#sizes = [60, 60, 61, 61, 62, 62, 63, 65, 62, 60]
sizes = [59, 58, 57, 56, 55, 56, 57, 58, 59, 60]
sizes = [24] * 8
#offsets = [3, 6, 5, 4, 3, 2, 1, 0]
for i in range(8):
    #sprite.images[i] = imageBig.clone()
    image = sprite.images[i]
    size = sizes[i]
    #offset = Position(offsets[i], 0)
    #font = device.loadFont("../_resources/_fonts/font.draw.rabaneta.ttf", size)
    font = device.loadFont("../_resources/_fonts/font.write.gadaj.otf", size)
    font.foreground = color
    #font.drawAtImageCenter("G", image, offset)
    font.drawAtImageCenter("G", image)

    pygame.transform.threshold(image.image, image.image, (255,255,255), (0,0,0), (255,66,0), 1, None, True)

count = 0
while device.running:
    device.clear((255, 255, 255))

    sprite.images[count].draw()
    count = (count + 1) % len(sprite.images)

    device.draw()
    device.loop()

"""
def drawAtImageCenter(self, source:pygame.Surface, destination:pygame.Surface):
    w = destination.get_width()
    h = destination.get_height()
    x = (w - source.get_width())//2
    y = (h - source.get_height())//2
    destination.blit(source, (x, y))

width = 32
height = 32

screen = pygame.display.set_mode((1200, 200), pygame.SRCALPHA)


background = game.loadImage('image.tile.background.alpha.png').clone()
font = game.loadFont('font.draw.rabaneta.ttf', 32)
#font.background = (255,255,255,255)
font.drawAtImageCenter('A', background)

pixels = []

for x in range(0, width -1 ):
    pixels.append((x,0))
for x in range(0, width -1):
    pixels.append((width - 1,x))
for x in range(0, width -1):
    pixels.append((width - 1 - x, height - 1))
for x in range(0, width -1):
    pixels.append((0,height -x - 1))

canvas = pygame.Surface((32 * width, height), pygame.SRCALPHA)
canvas = canvas.convert_alpha()
canvas.fill((255, 255, 255, 0))


black = (0, 0, 0, 255)
for index in range(0,32):
    count = 1
    group = 1
    for pixel_index in range(0, len(pixels)):
        pixel = pixels[(pixel_index + index) % len(pixels)]
        position = (32 * index + pixel[0], pixel[1])
        if count == 1 or count == 2 or count == 3:
            canvas.set_at(position, black)
        if group < 6:
            if count == 5:
                group += 1
                count = 0
        if group == 6:
            if count == 6:
                group = 1
                count = 0
        count += 1

    
        


screen.fill((155,155,155))
screen.blit(canvas, (0, 0))
pygame.display.flip()
pygame.image.save(canvas, "image.png")

running = True
while device.r
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

            """
