from typing import Callable, List
from algorithms import Direction, Random
from algorithms import PathFinding
from algorithms.dimension import Dimension
from core import Game, GameLoop
from core import Entity


from algorithms import Position
from entities.animation import GuiSimpleAnimation, GuiSimpleImage

from systems import ControlSystem
from systems import ControlComponent

from systems.gui_animation_system import GuiAnimationComponent, GuiAnimationSystem
from systems.gui_render_system import GuiRenderSystem
from systems.timer_system import TimerComponent, TimerSystem


def createMainScreenGame(gameLoop: GameLoop) -> Game:
    game = Game(gameLoop, Random(0))
    game.add(GuiRenderSystem(game))
    game.add(GuiAnimationSystem(game))
    game.add(TimerSystem(game))
    game.add(ControlSystem(game))

    backgroundImage = game.loadImage("image.gui.background.mainTitle.png")
    animationSheet = game.loadSpriteSheet(
        "sprite.gui.mainTitle.png", Dimension(646, 88)
    )
    sound = game.loadSound("sound.gui.mainTitle.mp3")

    w, h = gameLoop.device.dimension
    x, y = backgroundImage.dimension
    position = Position((w - x) // 2, (h - y) // 2)

    image = GuiSimpleImage(game, backgroundImage, position)
    image.enabled = True

    x, y = animationSheet.images[0].dimension
    position = Position((w - x) // 2, (h - y) // 2)

    animation = GuiSimpleAnimation(game, animationSheet, position)
    animation[GuiAnimationComponent].loop = False

    def activate():
        print('Activate')
        animation.enabled = True

    def loadGame(screenPosition: Position, worldPosition: Position) -> bool:
        print("Load Game")
        return True

    entity = Entity()
    entity.add(TimerComponent(game[TimerSystem], 40))
    entity[TimerComponent].callback = activate

    playSound = TimerComponent(game[TimerSystem], 10)
    playSound.callback = lambda: sound.play()
    entity.add(playSound)

    entity.add(ControlComponent(game[ControlSystem]))
    entity[ControlComponent].mouseClick = loadGame

    return game
