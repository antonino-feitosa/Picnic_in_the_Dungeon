
from device import Device
from roguelike import Ground
from algorithms import Random
from algorithms import RandomWalker

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
    ground.groundSheet = groundSheet
    ground.wallSheet = wallsSheet
    for pos in positions:
        ground.addGround(pos)
    ground.computeWalls()

    #device.camera.translate(400,0)
    canvas.draw((0,0))


    ## Mini map

    minimapUnit = 8
    minimapCanvas = device.loadCanvas((gridSize * minimapUnit, gridSize * minimapUnit))
    minimap = Ground(minimapCanvas, minimapUnit, rand)
    minimap.groundSheet = device.loadSpriteSheet(
        'Tileset - MiniMap - Ground.png', (minimapUnit, minimapUnit), 'resources')
    minimap.wallSheet = device.loadSpriteSheet(
        'Tileset - MiniMap - Walls.png', (minimapUnit, minimapUnit), 'resources')
    for pos in ground.groundPositions:
        minimap.addGround(pos)
    minimap.computeWalls()
    
    minimapCanvas.draw((300,300))

    device.reload()

    while device.running:
        device.update()


if __name__ == "__main__":
    main()
