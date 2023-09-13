
from device import Device
from device import KeyboardListener
from roguelike import Ground
from algorithms import Random
from algorithms import RandomWalker


def main():
    pixelsUnit = 32
    gridSize = 40
    rand = Random(4)

    device = Device()
    groundSheet = device.loadSpriteSheet(
        'Tileset - Ground.png', (pixelsUnit, pixelsUnit), 'resources')
    wallsSheet = device.loadSpriteSheet(
        'Tileset - Walls.png', (pixelsUnit, pixelsUnit), 'resources')

    walker = RandomWalker(iterations=10, length=20, rand=rand)
    walker.center = (20, 20)
    positions = walker.makeTree(2)

    canvas = device.loadCanvas((gridSize * pixelsUnit, gridSize * pixelsUnit))

    ground = Ground(canvas, pixelsUnit, rand)
    ground.groundSheet = groundSheet
    ground.wallSheet = wallsSheet
    for pos in positions:
        ground.addGround(pos)
    ground.computeWalls()

    # device.camera.translate(400,0)
    canvas.draw((0, 0))

    # Mini map

    minimapUnit = 4
    minimapCanvas = device.loadCanvas(
        (gridSize * minimapUnit, gridSize * minimapUnit))
    minimap = Ground(minimapCanvas, minimapUnit, rand)
    minimap.groundSheet = device.loadSpriteSheet(
        'Tileset - MiniMap - Ground.png', (minimapUnit, minimapUnit), 'resources')
    minimap.wallSheet = device.loadSpriteSheet(
        'Tileset - MiniMap - Walls.png', (minimapUnit, minimapUnit), 'resources')
    for pos in ground.groundPositions:
        minimap.addGround(pos)
    minimap.computeWalls()

    showingMinimap = False

    def showMinimap(key: str) -> None:
        nonlocal showingMinimap
        device.clear()
        canvas.draw((0, 0))
        if showingMinimap:
            showingMinimap = False
        else:
            showingMinimap = True
            minimapCanvas.draw((100, 100))
        device.reload()

    listenTap = KeyboardListener({'tab'})
    listenTap.onKeyUp = showMinimap
    device.addListener(listenTap)

    device.reload()

    while device.running:
        device.update()


if __name__ == "__main__":
    main()
