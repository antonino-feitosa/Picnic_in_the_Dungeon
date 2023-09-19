from game import RogueLike


def main():
    game = RogueLike(seed=1,enableFOV=False)
    game.draw()
    while game.isRunning():
        game.loop()


if __name__ == "__main__":
    main()
