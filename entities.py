
from device import Image
from device import SpriteSheet

from systems import PositionSystem
from systems import PositionComponent
from systems import MotionSystem
from systems import MotionComponent
from systems import RenderSystem
from systems import RenderComponent
from systems import AnimationSystem
from systems import AnimationComponent
from systems import FieldOfViewSystem
from systems import FieldOfViewComponent
from systems import CameraSystem
from systems import CameraComponent
from systems import AnimationControllerSystem
from systems import AnimationControllerComponent
from systems import MessageSystem
from systems import MessageComponent

from algorithms import Point
from algorithms import Random
from algorithms import Dimension
from algorithms import Direction
from algorithms import Composition
from algorithms import PathFinding
from algorithms import DIRECTIONS
from algorithms import distanceEuclidean
from algorithms import distanceSquare



class SimpleAnimation(Composition):
    def __init__(self, game:Composition, spriteSheet: SpriteSheet, position:Point):
        super().__init__()
        self.spriteSheet: SpriteSheet = spriteSheet
        image = spriteSheet.images[0]
        self.add(PositionComponent(game[PositionSystem], self, position))
        self.add(RenderComponent(game[RenderSystem], self, image))
        self.add(AnimationComponent(game[AnimationSystem], self[RenderComponent], spriteSheet))
        self[RenderComponent].enabled = False

    def play(self) -> None:
        self[RenderComponent].enabled = True
        self[AnimationComponent].enabled = True
    
    def stop(self) -> None:
        self[RenderComponent].enabled = False
        self[AnimationComponent].enabled = False
