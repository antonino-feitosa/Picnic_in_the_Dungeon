
from device import Image
from core2 import Entity, Game, System, Component
from coordinates import Position
from system_position import PositionComponent
from system_camera import CameraSystem

class RenderComponent(Component["RenderSystem"]):
    def __init__(self, system: "RenderSystem", entity: Entity, image: Image):
        super().__init__(system, entity)
        self.system = system
        self.image = image
        self.offset: Position = Position()
        self.enabled = True


class RenderSystem(System[RenderComponent]):
    def __init__(self, game: Game, camera : CameraSystem):
        super().__init__(game, set())
        self.camera = camera
        game.drawSystems.append(self)

    def draw(self):
        uw, uh = self.camera.pixelsUnit
        for component in self.components:
            width, height = component.entity[PositionComponent].position
            dx, dy = component.offset
            position = Position(width * uw + dx, height * uh + dy)
            if(self.camera.isVisible(position, component.image.dimension)):
                component.image.draw(position)
