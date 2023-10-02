import json
from algorithms.rectangle import Rectangle

from core import Game
from core import Entity

from device import Device
from device import TiledCanvas

from algorithms import Random
from algorithms import Position
from algorithms import Dimension
from device.image import Image
from gui.messages import MessageInfoComponent
from gui.visualization import DragCameraComponent, MoveCameraComponent

from systems import MapSystem
from systems import CollisionSystem
from systems import CollisionComponent
from systems import PositionComponent
from systems import MapViewComponent
from systems import MapViewSystem
from systems import PositionSystem
from systems import ViewSystem
from systems import RenderSystem
from systems import RenderComponent
from systems import AnimationSystem
from systems import AnimationComponent
from systems import ControlSystem
from systems import AnimationControllerComponent
from systems import MotionSystem
from systems import MotionComponent
from systems import GuiRenderSystem

from gui import SelectEntityComponent
from gui import SelectPathComponent
from systems.render_id_system import RenderIdComponent, RenderIdSystem

def loadAvatarDataSet(game:Game, entity:Entity, units:Dimension, colorId = 1):
    path = "_resources/_datasets/data.sprite.avatar.white.json"

    paths = []
    with open(path) as load_file:
        paths = json.load(load_file)
    
    colors = [
        # Armas, Poderes, Aleatórios
        (200,200,200), # 1 0 0
        (20,200,200),  # 2 0 0
        (20,200,20),   # 4 1 0
        (20,20,200),   # 8 2 0
        (200,20,200),  # 8 4 1
        (200,200,20),  # 8 8 2
        (255,200,20),  # 8 8 4
        (200,20,20),   # 8 8 8
    ]

    animationControl = entity[AnimationControllerComponent]
    color = colors[colorId]
    entity[RenderComponent].image.replaceColor((255,255,255), color)
    for path in paths:
        key:str = path
        key = key.removeprefix("sprite.avatar.white.")
        key = key.removesuffix('.png')
        sheet = game.loadSpriteSheet(path, units)
        for image in sheet.images:
            image.replaceColor((255,255,255), color)
        animationControl.animations[key] = sheet
    animationControl.playAnimation('idle.right')
    

def main():
    random = Random(1)
    units = Dimension(32, 32)
    dimension = Dimension(20,15)
    screenDimension = Dimension(dimension.width * units.width, dimension.height * units.height)
    device = Device("Picnic in the Dungeon", screenDimension, tick=40)

    game = Game(device, random)

    game.add(MapSystem(dimension, random))
    game.add(PositionSystem(game))
    game.add(CollisionSystem(game))
    game.add(ViewSystem(game))
    game.add(MapViewSystem(game))
    game.add(RenderSystem(game, units))
    game.add(AnimationSystem(game))
    game.add(ControlSystem(game, units))
    game.add(MotionSystem(game, units))
    game.add(GuiRenderSystem(game))
    game.add(RenderIdSystem(game, units))

    game[MapSystem].makeBlack()
    # game[MapSystem].makeIsland()
    game[MapSystem].calculateWalls()

    path = "sprite.avatar.white.idle.right.png"
    playerSheet = game.loadSpriteSheet(path, units)
    playerImage = playerSheet.images[0]

    for i in range(0, 4):
        entity = Entity()
        entity.add(PositionComponent(game[PositionSystem], entity, Position(10 + i//2, 7 + i % 2)))
        entity.add(CollisionComponent(game[CollisionSystem], entity))
        entity.add(RenderComponent(game[RenderSystem], entity, playerImage))
        entity.add(AnimationComponent(game[AnimationSystem], entity, playerSheet))
        entity.add(RenderIdComponent(game, entity, 'A'))
        entity.add(AnimationControllerComponent(entity))
        entity.add(MotionComponent(game[MotionSystem], entity))
        loadAvatarDataSet(game, entity, units, i)


    canvas = TiledCanvas(device, units, game[MapSystem].dimension)
    path = "sprite.map.ground.basic.png"
    groundSheet = game.loadSpriteSheet(path, Dimension(32, 32))
    path = "sprite.map.walls.basic.png"
    groundWalls = game.loadSpriteSheet(path, Dimension(32, 32))

    mapViewSystem = game[MapViewSystem]
    groundPaint = MapViewComponent(mapViewSystem, canvas, groundSheet, groundWalls)
    mapEntity = Entity()
    mapEntity.add(groundPaint)

    path = "sprite.gui.select.unit.png"
    selectUnit = game.loadSpriteSheet(path, Dimension(32, 32))
    path = "sprite.gui.select.path.png"
    selectPath = game.loadSpriteSheet(path, Dimension(32, 32))
    controlSystem = game[ControlSystem]
    mapEntity.add(SelectEntityComponent(game, controlSystem, selectUnit))
    mapEntity.add(SelectPathComponent(game, controlSystem, mapEntity, selectPath))
    #mapEntity.add(MoveCameraComponent(game, controlSystem, screenDimension))
    mapEntity.add(DragCameraComponent(game, controlSystem, screenDimension))
    mapEntity.add(MessageInfoComponent(game, controlSystem))

    selectUnit = mapEntity[SelectEntityComponent]
    selectPath = mapEntity[SelectPathComponent]

    selectUnit.callback = lambda e: selectPath.startSelection(e)

    def reset(path):
        if path:
            position = selectUnit.selectedEntity[PositionComponent].position
            direction = position.relativeDirection(path[0])
            selectUnit.selectedEntity[CollisionComponent].move(direction)
            selectUnit.selectedEntity[MotionComponent].move(direction)
        selectUnit.dropSelection()
        game.update()
        mapEntity[MessageInfoComponent].showMessage("Texto Longo para comparacao " + str(path))


    selectPath.callback = reset

    game.update()
    game.draw()
    while game.isRunning:
        game.loop()


if __name__ == "__main__":
    main()
