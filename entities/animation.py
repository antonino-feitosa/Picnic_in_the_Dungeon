
from core import Entity
from core import Game

from algorithms import Position

from device import Image
from device import SpriteSheet

from systems import AnimationSystem
from systems import AnimationComponent
from systems import PositionSystem
from systems import PositionComponent
from systems import RenderSystem
from systems import RenderComponent
from systems import GuiRenderComponent
from systems import GuiRenderSystem

class SimpleGuiImage(Entity):
    def __init__(self, game: Game, image: Image, position: Position):
        super().__init__()
        self.add(GuiRenderComponent(game[GuiRenderSystem], self, image))
        self[GuiRenderComponent].position = position
        self.enabled = False
    
    @property
    def image(self) -> Image:
        return self[GuiRenderComponent].image

    @image.setter
    def image(self, image:Image) -> None:
        self[GuiRenderComponent].image = image
    
    @property
    def position(self) -> Position:
        return self[GuiRenderComponent].position
    
    @position.setter
    def position(self, position:Position) -> None:
        self[GuiRenderComponent].position = position
        

class SimpleImage(Entity):
    def __init__(self, game: Game, image: Image, position: Position):
        super().__init__()
        self.image = image
        self.add(PositionComponent(game[PositionSystem], self, position))
        self.add(RenderComponent(game[RenderSystem], self, image))
        self.enabled = False


class SimpleAnimation(Entity):
    def __init__(self, game: Game, spriteSheet: SpriteSheet, position: Position):
        super().__init__()
        self.spriteSheet: SpriteSheet = spriteSheet
        image = spriteSheet.images[0]
        self.add(PositionComponent(game[PositionSystem], self, position))
        self.add(RenderComponent(game[RenderSystem], self, image))
        self.add(AnimationComponent(game[AnimationSystem], self, spriteSheet))
        self[RenderComponent].enabled = False
        self.enabled = False
