from game import RogueLike


def main():
    game = RogueLike(33)
    game.draw()
    while game.device.running:
        game.device.update()


if __name__ == "__main__":
    main()
