
from coordinates import Dimension
from device import Device


def main():
    screenDimension = Dimension(1280, 640)
    device = Device("Picnic in the Dungeon", screenDimension, tick=30)
    device.draw()
    while device.running:
        device.loop()


if __name__ == "__main__":
    main()
