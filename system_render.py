
<<<<<<< HEAD
from device import Image
from core import Entity, Game, System, Component
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
=======

class WorldRenderComponent(ScreenRenderComponent):
    def __init__(self, system: "WorldRenderSystem", entity: Entity, image: Image):
        super().__init__(system, entity, image)
        self.enabled = True

    def draw(self):
        width, height = self.entity[PositionComponent].position
        uw, uh = self.system.pixelsUnit
        dx, dy = self.offset
        position = Position(width * uw + dx, height * uh + dy)
        self.image.draw(position)


class WorldRenderSystem(ScreenRenderSystem):
    def __init__(self, game: Game, pixelsUnit: Dimension):
        super().__init__(game, set())
        self.pixelsUnit = pixelsUnit
        game.drawSystems.append(self)

    def draw(self):
        view = self.game[ViewSystem]
        for component in self.components:
            if view.isVisible(component):
                component.draw()
>>>>>>> a79b17861c8d96ab73819066d208ac0b19202da8
