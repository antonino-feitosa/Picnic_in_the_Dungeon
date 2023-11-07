import json

from algorithms import Dimension, Position, Random
from algorithms.direction import Direction
from core import Entity, Game, GameLoop
from device import TiledCanvas
from gui import (
    DragCameraComponent,
    MessageInfoComponent,
    MoveCameraComponent,
    SelectEntityComponent,
    SelectPathComponent,
)
from gui.selection import ButtonEndOfTurn
from systems import (
    AnimationComponent,
    AnimationControllerComponent,
    AnimationSystem,
    CollisionComponent,
    CollisionSystem,
    ControlSystem,
    MapSystem,
    MapViewComponent,
    MapViewSystem,
    MotionComponent,
    MotionSystem,
    PositionComponent,
    PositionSystem,
    RenderIdComponent,
    RenderIdSystem,
    ScreenRenderSystem,
    ViewSystem,
    WorldRenderComponent,
    WorldRenderSystem,
)
from systems.camera_system import CameraComponent, CameraSystem
from systems.control_system import ControlComponent
from systems.player_system import PlayerComponent, PlayerSystem
from systems.turn_system import TurnComponent, TurnSystem


def loadAvatarDataSet(game: Game, entity: Entity, units: Dimension, colorId=1):
    path = "_resources/_datasets/data.sprite.avatar.white.json"

    paths = []
    with open(path) as load_file:
        paths = json.load(load_file)

    colors = [
        # Armas, Poderes, Aleatórios
        (255, 255, 255),  # white
        (50, 50, 50),  # 
        (100, 100, 100),  # 
        (200, 200, 200),  #  grey
        
        (20, 200, 200),  # 2 0 0 cyan

        (20, 200, 20),  # 4 1 0 green

        (20, 20, 200),  # 8 2 0 blue


        (200, 20, 200),  # 8 4 1 purple
        (200, 200, 20),  # 8 8 2 yellow
        
        (255, 100, 20),  # 8 8 4 orange
        (255, 20, 100),  # 8 8 4 
        (200, 20, 20),  # 8 8 8 red
    ]

    animationControl = entity[AnimationControllerComponent]
    color = colors[colorId]
    entity[WorldRenderComponent].image.replaceColor((255, 255, 255), color)
    for path in paths:
        key: str = path
        key = key.removeprefix("sprite.avatar.white.")
        key = key.removesuffix(".png")
        sheet = game.loadSpriteSheet(path, units)
        for image in sheet.images:
            image.replaceColor((255, 255, 255), color)
        animationControl.animations[key] = sheet
    animationControl.playAnimation("idle.right")


class RandomIA(TurnComponent):
    def __init__(self, system:TurnSystem, entity:Entity, turn:int, random:Random):
        super().__init__(system, turn)
        self.entity = entity
        self.random = random
    
    def processTurn(self, turn: int):
        entity = self.entity
        dir = self.random.choice(Direction.All)
        entity[CollisionComponent].move(dir)
        entity[MotionComponent].move(dir)
        self.endOfTurn()


def createRogueLike(gameLoop: GameLoop) -> Game:
    random = Random(1)
    units = Dimension(32, 32)
    dimension = Dimension(20, 20)

    device = gameLoop.device
    screenDimension = device.dimension
    game = Game(gameLoop, random)

    game.add(TurnSystem(game))
    game.add(MapSystem(dimension, random))
    game.add(PositionSystem(game))
    game.add(CollisionSystem(game))
    game.add(ViewSystem(game))
    game.add(MapViewSystem(game))
    game.add(WorldRenderSystem(game, units))
    game.add(AnimationSystem(game))
    game.add(ControlSystem(game, units))
    game.add(MotionSystem(game, units))
    game.add(RenderIdSystem(game, units))
    game.add(ScreenRenderSystem(game, []))
    game.add(CameraSystem(device.camera, random, units))
    game.add(PlayerSystem(game))

    #game[MapSystem].makeBlack()
    game[MapSystem].makeIsland()
    #game[MapSystem].calculateWalls()

    path = "sprite.avatar.white.idle.right.png"
    playerSheet = game.loadSpriteSheet(path, units)
    playerImage = playerSheet.images[0]

    #center = game[MapSystem].startPosition
    count = 0
    for position in game[MapSystem].ground:
        if random.nextDouble() < 0.9:
            entity = Entity()
            entity.add(PositionComponent(game[PositionSystem], entity, position))
            entity.add(CollisionComponent(game[CollisionSystem], entity))
            entity.add(WorldRenderComponent(game[WorldRenderSystem], entity, playerImage))
            entity.add(AnimationComponent(game[AnimationSystem], entity, playerSheet))
            entity.add(AnimationControllerComponent(entity))
            entity.add(MotionComponent(game[MotionSystem], entity))
            if count == 0:
                entity.add(PlayerComponent(game[PlayerSystem], entity))
                entity.add(CameraComponent(game[CameraSystem], entity))
                entity[CameraComponent].centralize()
                loadAvatarDataSet(game, entity, units, 0)
            else:
                entity.add(RenderIdComponent(game, entity, "A"))
                entity.add(RandomIA(game[TurnSystem], entity, 1, random))
                loadAvatarDataSet(game, entity, units, count)
            loadAvatarDataSet(game, entity, units, count)
            count = (count + 1) % 4

    canvas = TiledCanvas(device, units, game[MapSystem].dimension)
    path = "sprite.map.ground.basic.png"
    groundSheet = game.loadSpriteSheet(path, Dimension(32, 32))
    path = "sprite.map.walls.basic.png"
    groundWalls = game.loadSpriteSheet(path, Dimension(32, 32))

    w, h = screenDimension
    mapViewSystem = game[MapViewSystem]
    groundPaint = MapViewComponent(mapViewSystem, canvas, groundSheet, groundWalls)
    mapEntity = Entity()
    mapEntity.add(groundPaint)
    mapEntity.add(TurnComponent(game[TurnSystem], 0))
    mapEntity.add(ButtonEndOfTurn(game, mapEntity, Position(w - 80, h - 80)))

    path = "sprite.gui.select.unit.png"
    selectUnit = game.loadSpriteSheet(path, Dimension(32, 32))
    path = "sprite.gui.select.path.png"
    selectPath = game.loadSpriteSheet(path, Dimension(32, 32))
    controlSystem = game[ControlSystem]
    mapEntity.add(SelectEntityComponent(game, controlSystem, selectUnit))
    mapEntity.add(SelectPathComponent(game, controlSystem, mapEntity, selectPath))
    # mapEntity.add(MoveCameraComponent(game, controlSystem, screenDimension))
    mapEntity.add(DragCameraComponent(game, controlSystem, screenDimension))
    mapEntity.add(MessageInfoComponent(game, controlSystem))

    selectUnit = mapEntity[SelectEntityComponent]
    selectPath = mapEntity[SelectPathComponent]

    def newSelectionEvent(entity:Entity):
        if PlayerComponent in entity:
            selectPath.startSelection(entity)

    selectUnit.callback = newSelectionEvent

    def reset(path):
        if path:
            position = selectUnit.selectedEntity[PositionComponent].position
            direction = position.relativeDirection(path[0])
            selectUnit.selectedEntity[CollisionComponent].move(direction)
            selectUnit.selectedEntity[MotionComponent].move(direction)
        selectUnit.dropSelection()
        game.update()

    selectPath.callback = reset

    game.update()
    return game
