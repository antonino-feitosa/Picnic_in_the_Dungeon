
from typing import Tuple

from device import Device
from device import KeyboardListener
from device import MouseDragListener
from roguelike import RogueLike
from algorithms import Random
from algorithms import RandomWalker


def main():
    rand = Random(7)
    device = Device()    

    walker = RandomWalker(iterations=10, length=10, rand=rand)
    walker.center = (20, 20)
    positions = walker.run()

    game = RogueLike(gridSize=40, device=device, rand= rand)

    for pos in positions:
        game.ground.addGround(pos)
    game.ground.computeWalls()

    for pos in positions:
        game.minimap.addGround(pos)
    game.minimap.ground.computeWalls()

    game.registerListeners()
    game.redraw()
    while device.running:
        device.update()


if __name__ == "__main__":
    main()
