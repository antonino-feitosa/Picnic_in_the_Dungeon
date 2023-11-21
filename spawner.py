
from algorithms import Point
from core import ECS, Entity, Scene
from algorithms import Random
from component import AreaOfEffect, BlocksTile, CombatStats, Confusion, Consumable, GUIDescription, Glyph, InflictsDamage, Item, Monster, Name, Player, Position, ProvidesHealing, Ranged, Renderable, Viewshed
from map import Rect


MAP_WIDTH = 80
MAP_HEIGHT = 40
MAX_MONSTERS = 1
MAX_ITENS = 5


def spawnRoom(scene:Scene, room:Rect):
    rand:Random = ECS.scene.retrieve('rand')
    numMonsters = rand.nextInt(MAX_MONSTERS + 1)
    numItens = rand.nextInt(MAX_ITENS + 1)
    positions:set[Point] = set()
    errors = 10
    while(len(positions) < numMonsters + numItens and errors > 0):
        x = (room.x1 + 1) + rand.nextInt((room.x2 - room.x1) - 1)
        y = (room.y1 + 1) + rand.nextInt((room.y2 - room.y1) - 1)
        point = Point(x,y)
        if point not in positions:
            positions.add(point)
    count = 0
    for point in positions:
        if count < numMonsters:
            createRandomMonster(scene, point.x, point.y)
        else:
            createRandomItem(scene, point.x, point.y)
        count += 1


def createPlayer(scene:Scene, x:int, y:int) -> Entity:
    background = scene.retrieve("background")
    font = scene.retrieve("font")
    player = scene.create()
    player.add(Position(x, y))
    player.add(Renderable(Glyph(background, font, "@"), 0))
    player.add(Player())
    player.add(Viewshed(8))
    player.add(BlocksTile())
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
    render = Renderable(Glyph(background, font, glyph), 1)
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


def createRandomItem(scene:Scene, x:int, y:int) -> Entity:
    rand:Random = scene.retrieve("rand")
    index = rand.nextInt(4)
    match index:
        case 0:
            return createHealthPotion(scene, x, y)
        case 1:
            return createMagicMissileScroll(scene, x, y)
        case 2:
            return createFireballScroll(scene, x, y)
        case 3:
            return createConfusionScroll(scene, x, y)
    raise Exception()


def createHealthPotion(scene:Scene, x:int, y:int) -> Entity:
    background = scene.retrieve("background")
    font = scene.retrieve("font")
    render = Renderable(Glyph(background, font, 'i'), 2)
    render.glyph.foreground = (255, 0, 0, 255)
    potion = scene.create()
    potion.add(Position(x,y))
    potion.add(render)
    potion.add(Name('Health Potion'))
    potion.add(Item())
    potion.add(Consumable())
    potion.add(ProvidesHealing(8))
    potion.add(GUIDescription())
    return potion


def createMagicMissileScroll(scene:Scene, x:int, y:int) -> Entity:
    background = scene.retrieve("background")
    font = scene.retrieve("font")
    render = Renderable(Glyph(background, font, ')'), 2)
    render.glyph.foreground = (255, 0, 0, 255)
    scroll = scene.create()
    scroll.add(Position(x,y))
    scroll.add(render)
    scroll.add(Name('Magic Missile Scroll'))
    scroll.add(Item())
    scroll.add(Consumable())
    scroll.add(Ranged(6))
    scroll.add(InflictsDamage(8))
    scroll.add(GUIDescription())
    return scroll


def createFireballScroll(scene:Scene, x:int, y:int) -> Entity:
    background = scene.retrieve("background")
    font = scene.retrieve("font")
    render = Renderable(Glyph(background, font, ')'), 2)
    render.glyph.foreground = (255, 0, 0, 255)
    scroll = scene.create()
    scroll.add(Position(x,y))
    scroll.add(render)
    scroll.add(Name('Fireball Scroll'))
    scroll.add(Item())
    scroll.add(Consumable())
    scroll.add(Ranged(6))
    scroll.add(InflictsDamage(20))
    scroll.add(AreaOfEffect(3))
    scroll.add(GUIDescription())
    return scroll

def createConfusionScroll(scene:Scene, x:int, y:int) -> Entity:
    background = scene.retrieve("background")
    font = scene.retrieve("font")
    render = Renderable(Glyph(background, font, ')'), 2)
    render.glyph.foreground = (255, 0, 0, 255)
    scroll = scene.create()
    scroll.add(Position(x,y))
    scroll.add(render)
    scroll.add(Name('Confusion Scroll'))
    scroll.add(Item())
    scroll.add(Consumable())
    scroll.add(Ranged(6))
    scroll.add(Confusion(4))
    scroll.add(GUIDescription())
    return scroll

