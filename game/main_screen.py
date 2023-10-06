from typing import Callable, List
from algorithms import Direction, Random
from algorithms import PathFinding
from algorithms.dimension import Dimension
from algorithms.rectangle import Rectangle
from core import Game, GameLoop
from core import Entity


from algorithms import Position
from entities.animation import GuiSimpleAnimation, GuiSimpleImage

from systems import ControlSystem
from systems import ControlComponent

from systems.gui_animation_system import GuiAnimationComponent, GuiAnimationSystem
from systems.gui_render_system import GuiRenderSystem
from systems.timer_system import TimerComponent, TimerSystem


class SelectButton(ControlComponent):
    def __init__(self, system:ControlSystem, position:Position, callback:Callable[[bool],None]):
        super().__init__(system)
        self.rect = Rectangle(position.x, position.y, position.x + 60, position.y + 80)
        self.callback = callback
    
    def mouseClick(self, screenPosition: Position, worldPosition: Position) -> bool:
        if screenPosition in self.rect:
            self.callback(True)
            return True
        return False
    
    def mouseClickRight(self, screenPosition: Position, worldPosition: Position) -> bool:
        if screenPosition in self.rect:
            self.callback(False)
            return True
        return False

class ActionButton(ControlComponent):
    def __init__(self, game:Game, position:Position, callback:Callable[[bool],None]):
        super().__init__(game[ControlSystem])
        self.rect = Rectangle(position.x, position.y, position.x + 200, position.y + 50)
        self.callback = callback
        pressed = game.loadImage('image.gui.button.action.pressed.png')
        self.pressedImage = GuiSimpleImage(game, pressed, position)
        
    
    def mouseClick(self, screenPosition: Position, worldPosition: Position) -> bool:
        if screenPosition in self.rect:
            self.callback(True)
            return True
        return False
    
    def mouseClickRight(self, screenPosition: Position, worldPosition: Position) -> bool:
        if screenPosition in self.rect:
            self.callback(False)
            return True
        return False
    
    def mousePosition(self, screenPosition: Position, worldPosition: Position) -> None:
        if self.system.buttonLeftDown and screenPosition in self.rect:
            self.pressedImage.enabled = True
        else:
            self.pressedImage.enabled = False


def createMainScreenControls(game:Game, dimension:Dimension) -> Entity:
    entity = Entity()

    backgroundImage = game.loadImage("image.gui.background.mainScreen.png")

    w, h = dimension
    x, y = backgroundImage.dimension
    position = Position((w - x) // 2, (h - y) // 2)

    image = GuiSimpleImage(game, backgroundImage, position)
    image.enabled = True

    actions = [
        'exp 1',
        'exp 2',
        'exp 3',
        'exp 4',
        'exp 5',
        'party 1',
        'party 2',
        'party 3',
        'party 4',
        'party 5',
        'quest 1',
        'quest 2',
        'quest 3',
        'quest 4',
        'quest 5',
    ]

    def closure(message):
        def callback(value:bool):
            print(message,  value)
        return callback

    for j in range(3):
        for i in range(5):
            message = actions[j * 5 + i]
            callback = closure(message)
            position = Position(300 + i * 100, 50 + 150 * j)
            component = SelectButton(game[ControlSystem], position, callback)
            entity.add(component)
    
    actions = ['options', 'reserach', 'start']
    for i in range(3):
        callback = closure(actions[i])
        position = Position(50 + 250 * i, 500)
        component = ActionButton(game, position, callback)
        entity.add(component)
    
    callback = lambda isRight: game.exit() if isRight else None
    position = Position(50, 575)
    component = ActionButton(game, position, callback)
    entity.add(component)
    
    return entity



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

    entity = Entity()
    entity.add(TimerComponent(game[TimerSystem], 40))
    
    playSound = TimerComponent(game[TimerSystem], 10)
    playSound.callback = lambda: sound.play()
    entity.add(playSound)

    forceTransition = TimerComponent(game[TimerSystem], 200)
    entity.add(forceTransition)

    entity.add(ControlComponent(game[ControlSystem]))

    def activate():
        animation.enabled = True

    def loadGame(screenPosition: Position, worldPosition: Position) -> bool:
        sound.stop()
        entity.enabled = False
        image.enabled = False
        createMainScreenControls(game, gameLoop.device.dimension)
        return True

    entity[TimerComponent].callback = activate
    entity[ControlComponent].mouseClick = loadGame
    forceTransition.callback = lambda: loadGame(Position(),Position()) # type: ignore

    return game
