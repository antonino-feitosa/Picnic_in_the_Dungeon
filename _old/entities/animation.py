
from core import Entity
from core import Game

from algorithms import Point

from device import Image
from device import SpriteSheet

from systems import AnimationSystem
from systems import AnimationComponent
from systems import PositionSystem
from systems import PositionComponent
from systems import WorldRenderSystem
from systems import WorldRenderComponent
from systems import ScreenRenderComponent
from systems import ScreenRenderSystem
from systems import GuiAnimationSystem
from systems import GuiAnimationComponent

class GuiSimpleImage(Entity):
    def __init__(self, game: Game, image: Image, position: Point):
        super().__init__()
        self.add(ScreenRenderComponent(game[ScreenRenderSystem], self, image))
        self[ScreenRenderComponent].offset = position
        self.enabled = False
    
    @property
    def image(self) -> Image:
        return self[ScreenRenderComponent].image

    @image.setter
    def image(self, image:Image) -> None:
        self[ScreenRenderComponent].image = image
    
    @property
    def position(self) -> Point:
        return self[ScreenRenderComponent].offset
    
    @position.setter
    def position(self, position:Point) -> None:
        self[ScreenRenderComponent].offset = position
        

class SimpleImage(Entity):
    def __init__(self, game: Game, image: Image, position: Point):
        super().__init__()
        self.image = image
        self.add(PositionComponent(game[PositionSystem], self, position))
        self.add(WorldRenderComponent(game[WorldRenderSystem], self, image))
        self.enabled = False


class SimpleAnimation(Entity):
    def __init__(self, game: Game, spriteSheet: SpriteSheet, position: Point):
        super().__init__()
        self.spriteSheet: SpriteSheet = spriteSheet
        image = spriteSheet.images[0]
        self.add(PositionComponent(game[PositionSystem], self, position))
        self.add(WorldRenderComponent(game[WorldRenderSystem], self, image))
        self.add(AnimationComponent(game[AnimationSystem], self, spriteSheet))
        self[WorldRenderComponent].enabled = False
        self.enabled = False

class GuiSimpleAnimation(Entity):
    def __init__(self, game: Game, spriteSheet: SpriteSheet, position: Point):
        super().__init__()
        self.spriteSheet: SpriteSheet = spriteSheet
        image = spriteSheet.images[0]
        self.add(ScreenRenderComponent(game[ScreenRenderSystem], self, image))
        self.add(GuiAnimationComponent(game[GuiAnimationSystem], self, spriteSheet))
        self[ScreenRenderComponent].offset = position
        self[ScreenRenderComponent].enabled = False
        self.enabled = False
