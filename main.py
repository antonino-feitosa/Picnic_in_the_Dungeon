from core import Game
from core import Entity

from device import Device
from device import TiledCanvas

from algorithms import Random
from algorithms import Position
from algorithms import Dimension
from gui.selection import ControlComponentSelectionPath

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

from gui import ControlComponentSelectEntity


def main():
    device = Device("Picnic in the Dungeon", Dimension(640, 480), tick=40)

    random = Random(1)
    units = Dimension(32, 32)
    game = Game(device, random)

    game.add(MapSystem(Dimension(20, 15), random))
    game.add(PositionSystem(game))
    game.add(CollisionSystem(game))
    game.add(ViewSystem(game))
    game.add(MapViewSystem(game))
    game.add(RenderSystem(game, units))
    game.add(AnimationSystem(game))
    game.add(ControlSystem(game, units))

    game[MapSystem].makeBlack()
    # game[MapSystem].makeIsland()
    game[MapSystem].calculateWalls()

    playerSheet = game.loadSpriteSheet(
        "_resources/sprite.avatar.white.idle.right.png", units
    )
    playerImage = playerSheet.images[0]

    a = Entity()
    a.add(PositionComponent(game[PositionSystem], a, Position(10, 7)))
    a.add(CollisionComponent(game[CollisionSystem], a))
    a.add(RenderComponent(game[RenderSystem], a, playerImage))
    a.add(AnimationComponent(game[AnimationSystem], a, playerSheet))
    b = Entity()
    b.add(PositionComponent(game[PositionSystem], b, Position(11, 7)))
    b.add(CollisionComponent(game[CollisionSystem], b))
    b.add(RenderComponent(game[RenderSystem], b, playerImage))
    b.add(AnimationComponent(game[AnimationSystem], b, playerSheet))
    c = Entity()
    c.add(PositionComponent(game[PositionSystem], c, Position(11, 8)))
    c.add(CollisionComponent(game[CollisionSystem], c))
    c.add(RenderComponent(game[RenderSystem], c, playerImage))
    c.add(AnimationComponent(game[AnimationSystem], c, playerSheet))
    d = Entity()
    d.add(PositionComponent(game[PositionSystem], d, Position(10, 8)))
    d.add(CollisionComponent(game[CollisionSystem], d))
    d.add(RenderComponent(game[RenderSystem], d, playerImage))
    d.add(AnimationComponent(game[AnimationSystem], d, playerSheet))
    d[AnimationComponent].tickWait = 4

    canvas = TiledCanvas(device, units, game[MapSystem].dimension)
    groundSheet = game.loadSpriteSheet(
        "_resources/sprite.map.ground.basic.png", Dimension(32, 32)
    )
    groundWalls = game.loadSpriteSheet(
        "_resources/sprite.map.walls.basic.png", Dimension(32, 32)
    )

    groundPaint = MapViewComponent(
        game[MapViewSystem], canvas, groundSheet, groundWalls
    )
    mapEntity = Entity()
    mapEntity.add(groundPaint)

    selectUnit = game.loadSpriteSheet(
        "_resources/sprite.gui.select.unit.png", Dimension(32, 32)
    )
    selectPath = game.loadSpriteSheet(
        "_resources/sprite.gui.select.path.png", Dimension(32, 32)
    )
    mapEntity.add(ControlComponentSelectEntity(game, game[ControlSystem], selectUnit))
    mapEntity.add(
        ControlComponentSelectionPath(game, game[ControlSystem], mapEntity, selectPath)
    )

    selectUnit = mapEntity[ControlComponentSelectEntity]
    selectPath = mapEntity[ControlComponentSelectionPath]

    selectUnit.callback = lambda e: selectPath.startSelection(e)

    def reset(path):
        positionComponent = selectUnit.selectedEntity[PositionComponent]
        direction = positionComponent.position.relativeDirection(path[0])
        positionComponent.move(direction)
        selectUnit.dropSelection()
        game.update()
    selectPath.callback = reset


    game.update()
    game.draw()
    while game.isRunning:
        game.loop()


if __name__ == "__main__":
    main()
