import pygame

pygame.init()

width = 32
height = 32

screen = pygame.display.set_mode((1200, 200), pygame.SRCALPHA)


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
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
