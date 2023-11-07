from typing import Callable, List, Set
from algorithms import Direction, Random
from algorithms import PathFinding
from algorithms.dimension import Dimension
from algorithms.rectangle import Rectangle
from core import Game, GameLoop
from core import Entity


from algorithms import Position
from entities.animation import GuiSimpleAnimation, GuiSimpleImage
from gui.messages import MessageInfoComponent

from systems import ControlSystem
from systems import ControlComponent

from systems.gui_animation_system import GuiAnimationComponent, GuiAnimationSystem
from systems.screen_render_system import ScreenRenderSystem
from systems.timer_system import TimerComponent, TimerSystem

from game.roguelike import createRogueLike

class GameMenuComponent(ControlComponent):
    def __init__(self, game:Game, mainScreen:Game):
        super().__init__(game[ControlSystem])
        menuImage = game.loadImage("image.gui.background.gameScreen.png")
        w, h = game.device.dimension
        x, y = menuImage.dimension
        offset = Position((w - x) // 2,(h - y) // 2)
        self.pressedImage = GuiSimpleImage(game, menuImage, offset)
        self.enabled = True

        messageComp = MessageInfoComponent(game, game[ControlSystem])

        def escapeAction(_):
            nonlocal mainScreen
            #createMainScreenGame(mainScreen.gameLoop).setActive()
            mainScreen.setActive()

        position = Position(50, 50) + offset
        escapeButton = ActionButton(game, position, escapeAction)
        escapeButton.enabled = False
        self.pressedImage.add(escapeButton)

        optionsAction = lambda _: messageComp.showMessage('Options')
        position = Position(50, 125) + offset
        optionsButton = ActionButton(game, position, optionsAction)
        optionsButton.enabled = False
        self.pressedImage.add(optionsButton)

        exitAction = lambda isRight: game.exit() if isRight else None
        position = Position(50, 200) + offset
        exitButton = ActionButton(game, position, exitAction)
        exitButton.enabled = False
        self.pressedImage.add(exitButton)

        self.pressedImage.add(messageComp)
    
    def keyPressed(self, keys: Set[str]) -> bool:
        if 'escape' in keys:
            if self.pressedImage.enabled:
                self.pressedImage.enabled = False
                self.lock = False
            else:
                self.pressedImage.enabled = True
                self.lock = True
            return True
        return False


class SelectButton(ControlComponent):
    def __init__(
        self,
        system: ControlSystem,
        position: Position,
        callback: Callable[[bool], None],
    ):
        super().__init__(system)
        self.rect = Rectangle(position.x, position.y, position.x + 60, position.y + 80)
        self.callback = callback

    def mouseClick(self, screenPosition: Position, worldPosition: Position) -> bool:
        if screenPosition in self.rect:
            self.callback(True)
            return True
        return False

    def mouseClickRight(
        self, screenPosition: Position, worldPosition: Position
    ) -> bool:
        if screenPosition in self.rect:
            self.callback(False)
            return True
        return False


class ActionButton(ControlComponent):
    def __init__(
        self, game: Game, position: Position, callback: Callable[[bool], None]
    ):
        super().__init__(game[ControlSystem])
        self.rect = Rectangle(position.x, position.y, position.x + 200, position.y + 50)
        self.callback = callback
        pressed = game.loadImage("image.gui.button.action.pressed.png")
        self.pressedImage = GuiSimpleImage(game, pressed, position)
        self.buttonLeftDown = False

    def mouseClick(self, screenPosition: Position, worldPosition: Position) -> bool:
        if screenPosition in self.rect:
            self.callback(True)
            return True
        return False

    def mouseClickRight(
        self, screenPosition: Position, worldPosition: Position
    ) -> bool:
        if screenPosition in self.rect:
            self.callback(False)
            return True
        return False

    def mouseLeft(self, down: bool, screenPosition: Position, worldPosition: Position) -> bool:
        if down and screenPosition in self.rect:
            self.buttonLeftDown = True
        else:
            self.buttonLeftDown = False
        return super().mouseLeft(down, screenPosition, worldPosition)

    def mousePosition(self, screenPosition: Position, worldPosition: Position) -> None:
        if self.buttonLeftDown and screenPosition in self.rect:
            self.pressedImage.enabled = True
        else:
            self.pressedImage.enabled = False


def createMainScreenControls(game: Game, screenDimension: Dimension) -> Entity:
    dimension = Dimension(800, 640)
    if screenDimension.width < dimension.width:
        raise ValueError("The minimum width is 800 pixels")

    if screenDimension.height < dimension.height:
        raise ValueError("The minimum height is 640 pixels")

    offset = Position(
        (screenDimension.width - dimension.width) // 2,
        (screenDimension.height - dimension.height) // 2
    )

    backgroundImage = game.loadImage("image.gui.background.mainScreen.png")
    image = GuiSimpleImage(game, backgroundImage, offset)
    image.enabled = True

    actions = [
        "exp 1",
        "exp 2",
        "exp 3",
        "exp 4",
        "exp 5",
        "party 1",
        "party 2",
        "party 3",
        "party 4",
        "party 5",
        "quest 1",
        "quest 2",
        "quest 3",
        "quest 4",
        "quest 5",
    ]

    entity = Entity()
    entity.add(MessageInfoComponent(game, game[ControlSystem]))

    def closure(message):
        nonlocal entity

        def callback(value: bool):
            nonlocal entity
            entity[MessageInfoComponent].showMessage(
                message + " Right Button: " + str(value)
            )

        return callback

    for j in range(3):
        for i in range(5):
            message = actions[j * 5 + i]
            callback = closure(message)
            position = Position(300 + i * 100, 50 + 150 * j) + offset
            component = SelectButton(game[ControlSystem], position, callback)
            entity.add(component)

    position = Position(50, 500) + offset
    component = ActionButton(game, position, closure("options"))
    entity.add(component)

    position = Position(300, 500) + offset
    component = ActionButton(game, position, closure("research"))
    entity.add(component)

    def startNewGame(isRight) -> None:
        nonlocal game
        gameLoop = game.gameLoop
        newgame = createRogueLike(gameLoop)
        GameMenuComponent(newgame, game)
        newgame.setActive()

    position = Position(550, 500) + offset
    component = ActionButton(game, position, startNewGame)
    entity.add(component)

    callback = lambda isRight: game.exit() if isRight else None
    position = Position(50, 575) + offset
    component = ActionButton(game, position, callback)
    entity.add(component)

    return entity


def createMainScreenGame(gameLoop: GameLoop) -> Game:
    dimension = Dimension(800, 640)
    screenDimension = gameLoop.device.dimension
    if screenDimension.width < dimension.width:
        raise ValueError("The minimum width is 800 pixels")

    if screenDimension.height < dimension.height:
        raise ValueError("The minimum height is 640 pixels")

    offset = Position(
        (screenDimension.width - dimension.width) // 2,
        (screenDimension.height - dimension.height) // 2
    )

    game = Game(gameLoop, Random(0))
    game.add(ScreenRenderSystem(game, []))
    game.add(GuiAnimationSystem(game))
    game.add(TimerSystem(game))
    game.add(ControlSystem(game))

    backgroundImage = game.loadImage("image.gui.background.mainTitle.png")
    animationSheet = game.loadSpriteSheet(
        "sprite.gui.mainTitle.png", Dimension(646, 88)
    )
    sound = game.loadSound("sound.gui.mainTitle.mp3")

    image = GuiSimpleImage(game, backgroundImage, offset)
    image.enabled = True

    w, h = gameLoop.device.dimension
    x, y = animationSheet.images[0].dimension
    position = Position((w - x) // 2, (h - y) // 2)

    animation = GuiSimpleAnimation(game, animationSheet, position)
    animation[GuiAnimationComponent].loop = False

    entity = Entity()
    entity.add(TimerComponent(game[TimerSystem], entity, 40))

    playSound = TimerComponent(game[TimerSystem], entity, 10)
    playSound.callback = lambda: sound.play()
    entity.add(playSound)

    forceTransition = TimerComponent(game[TimerSystem], entity, 200)
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
    forceTransition.callback = lambda: loadGame(Position(), Position())  # type: ignore

    return game
