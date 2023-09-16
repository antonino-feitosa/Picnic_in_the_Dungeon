
from game import RogueLike

def main():
    game = RogueLike()
    game.draw()
    while game.device.running:
        game.device.update()

if __name__ == "__main__":
    main()