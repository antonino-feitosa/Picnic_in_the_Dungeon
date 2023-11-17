
from core import ECS, Entity, Scene
from algorithms import Random
from component import BlocksTile, CombatStats, GUIDescription, Glyph, Monster, Name, Player, Position, Renderable, Viewshed


def createPlayer(scene:Scene, x:int, y:int) -> Entity:
    background = scene.retrieve("background")
    font = scene.retrieve("font")
    player = scene.create()
    player.add(Position(x, y))
    player.add(Renderable(Glyph(background, font, "@")))
    player.add(Player())
    player.add(Viewshed(8))
    player.add(CombatStats(30, 2, 5))
    player.add(Name("Player"))
    player.add(GUIDescription())
    return player


def createRandomMonster(scene:Scene, x:int, y:int) -> Entity:
    rand:Random = scene.retrieve("rand")
    index = rand.nextInt(2)
    match index:
        case 0:
            return createOrc(scene, x, y)
        case 1:
            return createGoblin(scene, x, y)
    raise Exception()


def createOrc(scene:Scene, x:int, y:int) -> Entity:
    return createMonster(scene, x, y, 'o', 'Orc')


def createGoblin(scene:Scene, x:int, y:int) -> Entity:
    return createMonster(scene, x, y, 'g', 'Goblin')


def createMonster(scene:Scene, x:int, y:int, glyph:str, name:str) -> Entity:
    background = scene.retrieve("background")
    font = scene.retrieve("font")
    render = Renderable(Glyph(background, font, glyph))
    render.glyph.foreground = (255, 0, 0, 255)
    monster = scene.create()
    monster.add(Position(x,y))
    monster.add(render)
    monster.add(Viewshed(8))
    monster.add(Monster())
    monster.add(Name(name))
    monster.add(BlocksTile())
    monster.add(CombatStats(16, 1, 4))
    monster.add(GUIDescription())
    return monster
