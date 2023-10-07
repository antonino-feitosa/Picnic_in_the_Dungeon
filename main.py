from algorithms import Dimension
from core import GameLoop
from device import Device
from game.main_screen import createMainScreenGame


def main():
    screenDimension = Dimension(1280, 640)
    device = Device("Picnic in the Dungeon", screenDimension, tick=30)
    gameLoop = GameLoop(device)
    game = createMainScreenGame(gameLoop)
    game.setActive()
    gameLoop.forever()


if __name__ == "__main__":
    main()
