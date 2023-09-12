
from algorithms import Random
from algorithms import RandomWalker
from device import Device
from roguelike import Ground


def main():
    pixelsUnit = 32
    gridSize = 20
    rand = Random()

    device = Device()
    groundSheet = device.loadSpriteSheet(
        'Tileset - Ground.png', (pixelsUnit, pixelsUnit), 'resources')
    wallsSheet = device.loadSpriteSheet(
        'Tileset - Walls.png', (pixelsUnit, pixelsUnit), 'resources')

    walker = RandomWalker(iterations=10, length=17, center=(10, 10))
    positions = walker.run(rand)

    canvas = device.loadCanvas((gridSize * pixelsUnit, gridSize * pixelsUnit))
    
    ground = Ground(canvas, pixelsUnit, rand)
    ground.paintGround(positions, groundSheet)
    ground.paintWalls(positions, wallsSheet)

    canvas.toImage().draw()

    #groundSheet.images[3].draw()

    device.reload()
    device.run()
    pass


if __name__ == "__main__":
    main()
