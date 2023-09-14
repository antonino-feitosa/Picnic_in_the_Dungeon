
from functools import partial

from device import Device
from roguelike import RogueLike
from algorithms import Point
from algorithms import Random
from algorithms import RandomWalker


def main():
    rand = Random(7)
    device = Device()

    walker = RandomWalker(iterations=20, length=50, rand=rand)
    walker.algorithm = walker.starAlgorithm
    walker.center = Point(50, 50)
    positions = walker.run()

    game = RogueLike(gridSize=100, device=device, rand=rand)

    for pos in positions:
        game.ground.addGround(pos)
    game.ground.computeWalls()

    for pos in positions:
        game.minimap.addGround(pos)
    game.minimap.ground.computeWalls()

    game.registerListeners()
    game.initializeSystems()
    game.createPlayer(Point(50,50))
    game.listenerResetCamera()

    game.redraw()
    while device.running:
        device.update()


if __name__ == "__main__":
    main()
