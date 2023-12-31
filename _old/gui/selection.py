from typing import Callable
from algorithms import Direction
from algorithms import PathFinding
from algorithms import Rectangle
from core import Game
from core import Entity

from device import SpriteSheet

from algorithms import Point
from entities.animation import GuiSimpleImage

from systems import ControlSystem
from systems import ControlComponent
from systems import CollisionSystem
from systems import PositionComponent

from entities import SimpleAnimation
from systems.map_system import MapSystem
from systems.player_system import PlayerComponent
from systems.turn_system import TurnComponent


class ButtonEndOfTurn(ControlComponent):
    def __init__(self, game:Game, entity:Entity, position:Point):
        super().__init__(game[ControlSystem])
        self.game = game
        self.entity = entity
        self.imageNextTurn = game.loadImage('image.gui.button.nextturn.png')
        self.imageWaitTurn = game.loadImage('image.gui.button.waitturn.png')
        self.image = GuiSimpleImage(game,self.imageNextTurn, position)
        self.image.enabled = True
        w, h = self.imageNextTurn.dimension
        self.rect = Rectangle(position.x, position.y, position.x + w, position.y + h)
    
    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        if screenPosition in self.rect:
            self.entity[TurnComponent].endOfTurn()
            self.game.update()
            self.game.update()
            return True
        return False

    def tick(self) -> None:
        if self.game[ControlSystem].lockControls:
            self.image.image = self.imageWaitTurn
        else:
            self.image.image = self.imageNextTurn



class SelectEntityComponent(ControlComponent):
    def __init__(self, game: Game, system: ControlSystem, spriteSheet: SpriteSheet):
        super().__init__(system)
        self.game = game
        self.system = system
        self.selectedEntity: Entity
        animation = SimpleAnimation(game, spriteSheet, Point())
        self.selectedAnimation: SimpleAnimation = animation
        self.activeSelection: bool = False
        self.enabled = True
        self.callback:Callable[[Entity],None] = lambda _:None


    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        if self.enabled and not self.activeSelection:
            positionToComponent = self.game[CollisionSystem].actualPosition
            if worldPosition in positionToComponent:
                component = positionToComponent[worldPosition]
                self.selectedEntity = component.entity
                self.selectedAnimation[PositionComponent].position = component.position
                self.selectedAnimation.enabled = True
                self.activeSelection = True
                self.callback(self.selectedEntity)
                return True
        return False

    def dropSelection(self) -> None:
        self.activeSelection = False
        self.selectedAnimation.enabled = False

    @property
    def enabled(self) -> bool:
        return super().enabled

    @enabled.setter
    def enabled(self, value):
        self.selectedAnimation.enabled = value
        super(__class__, self.__class__).enabled.__set__(self, value)  # type: ignore


class SelectPathComponent(ControlComponent):
    def __init__(self, game: Game, system: ControlSystem, entity:Entity, spriteSheet: SpriteSheet):
        super().__init__(system)
        self.system = system
        self.entity = entity
        self.pathSize = 1  # TODO num of moves, turn component
        self.selectedEntity: Entity

        self.callback: Callable[[list[Point]], None] = lambda _: None

        self.path: list[Point] = []
        self.pathFinding = PathFinding(game[MapSystem].ground, Direction.All)
        self.pathAnimations: list[SimpleAnimation] = []
        for _ in range(self.pathSize):
            self.pathAnimations.append(
                SimpleAnimation(game, spriteSheet, Point(0, 0))
            )
        ControlComponent.enabled.fset(self, False)

    @ControlComponent.enabled.setter
    def enabled(self, value):
        ControlComponent.enabled.fset(self, value)
        if not value:
            self.clearPath()
        self.selectedAnimation = value

    def startSelection(self, selectedEntity:Entity) -> None:
        self.selectedEntity = selectedEntity
        self.enabled = True

    def mouseClick(self, screenPosition: Point, worldPosition: Point) -> bool:
        if self.enabled:
            source = self.selectedEntity[PositionComponent].position
            self.updatePath(source, worldPosition)
            self.callback(self.path)
            self.clearPath()
            self.enabled = False
            return True
        return False

    def mousePosition(self, screenPosition: Point, worldPosition: Point) -> bool:
        if self.enabled:
            source = self.selectedEntity[PositionComponent].position
            self.updatePath(source, worldPosition)
            return True
        return False

    def updatePath(self, source: Point, destination: Point) -> None:
        if destination == source:
            self.path = []
        else:
            distance = source.distanceSquare(destination)
            if distance > 0 and distance <= self.pathSize:
                self.path = self.pathFinding.searchPath(source, destination)
                if len(self.path) > 0:
                    self.path = self.path[1:]
                for position, entity in zip(self.path, self.pathAnimations):
                    entity[PositionComponent].position = position
                    entity.enabled = True
            else:
                self.path = []
        for i in range(len(self.path), self.pathSize):
            self.pathAnimations[i].enabled = False

    def clearPath(self):
        self.path = []
        for anim in self.pathAnimations:
            anim.enabled = False
