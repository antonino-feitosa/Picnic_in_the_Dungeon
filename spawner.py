
from algorithms import Point
from core import ECS, Entity, Scene
from algorithms import Random
from component import AreaOfEffect, BlocksTile, CombatStats, Confusion, Consumable, DefenseBonus, Equippable, GUIDescription, HungerClock, InflictsDamage, Item, MagicMapper, MeleePowerBonus, Monster, Name, ParticleLifetime, Player, Position, ProvidesFood, ProvidesHealing, Ranged, Renderable, Viewshed
from device import Color, Font, Image
from map import Rect
from randomTable import RandomTable


MAP_WIDTH = 80
MAP_HEIGHT = 30
MAX_MONSTERS = 4


def roomTable(depth:int) -> RandomTable:
    table = RandomTable()
    table.add("Goblin", 10)
    table.add("Orc", 1 + depth)
    table.add("Health Potion", 7)
    table.add("Fireball Scroll", 2 + depth)
    table.add("Confusion Scroll", 2 + depth)
    table.add("Magic Missile Scroll", 4)
    table.add("Dagger", 3)
    table.add("Shield", 3)
    table.add("Long Sword", depth)
    table.add("Tower Shield", depth)
    table.add("Rations", 7)
    table.add("Magic Mapper Scroll", 2)
    return table


def spawnRoom(scene: Scene, room: Rect, depth: int) -> None:
    rand: Random = ECS.scene.retrieve('random')
    numMonsters = rand.nextRange(1, MAX_MONSTERS + 3) + (depth - 1) - 3
    positions: set[tuple[Point, str]] = set()
    spawnTable = roomTable(depth)
    errors = 10

    while (len(positions) < numMonsters and errors > 0):
        x = (room.x1 + 1) + rand.nextInt((room.x2 - room.x1) - 1)
        y = (room.y1 + 1) + rand.nextInt((room.y2 - room.y1) - 1)
        point = Point(x, y)
        if point not in positions:
            spawn = spawnTable.roll(rand)
            positions.add((point, spawn))
        else:
            errors -= 1

    for (point, name) in positions:
        x = point.x
        y = point.y
        match name:
            case "Goblin": createGoblin(scene, x, y)
            case "Orc": createGoblin(scene, x, y)
            case "Health Potion": createHealthPotion(scene, x, y)
            case "Fireball Scroll": createMagicMissileScroll(scene, x, y)
            case "Confusion Scroll": createFireballScroll(scene, x, y)
            case "Magic Missile Scroll": createConfusionScroll(scene, x, y)
            case "Dagger": createDagger(scene, x, y)
            case "Shield": createShield(scene, x, y)
            case "Long Sword": createLongSword(scene, x, y)
            case "Tower Shield": createTowerShield(scene, x, y)
            case "Rations": createRations(scene, x, y)
            case "Magic Mapper Scroll": createMagicMapperScroll(scene, x, y)


def createPlayer(scene: Scene, x: int, y: int) -> Entity:
    player = scene.create()
    player.add(Position(x, y))
    player.add(Renderable("@", 0, (255, 255, 0, 255)))
    player.add(Player())
    player.add(Viewshed(8))
    player.add(BlocksTile())
    player.add(CombatStats(30, 2, 5))
    player.add(Name("Player"))
    player.add(GUIDescription())
    player.add(HungerClock(HungerClock.WELL_FED, 20))
    return player


def createOrc(scene: Scene, x: int, y: int) -> Entity:
    return createMonster(scene, x, y, 'O', 'Orc')


def createGoblin(scene: Scene, x: int, y: int) -> Entity:
    return createMonster(scene, x, y, 'G', 'Goblin')


def createMonster(scene: Scene, x: int, y: int, glyph: str, name: str) -> Entity:
    monster = scene.create()
    monster.add(Position(x, y))
    monster.add(Renderable(glyph, 1, (255, 0, 0, 255)))
    monster.add(Viewshed(8))
    monster.add(Monster())
    monster.add(Name(name))
    monster.add(BlocksTile())
    monster.add(CombatStats(16, 1, 4))
    monster.add(GUIDescription())
    return monster


def createHealthPotion(scene: Scene, x: int, y: int) -> Entity:
    potion = scene.create()
    potion.add(Position(x, y))
    potion.add(Renderable("i", 2, (255, 0, 255, 255)))
    potion.add(Name('Health Potion'))
    potion.add(Item())
    potion.add(Consumable())
    potion.add(ProvidesHealing(8))
    potion.add(GUIDescription())
    return potion


def createMagicMissileScroll(scene: Scene, x: int, y: int) -> Entity:
    scroll = scene.create()
    scroll.add(Position(x, y))
    scroll.add(Renderable(")", 2, (255, 0, 255, 255)))
    scroll.add(Name('Magic Missile Scroll'))
    scroll.add(Item())
    scroll.add(Consumable())
    scroll.add(Ranged(6))
    scroll.add(InflictsDamage(8))
    scroll.add(GUIDescription())
    return scroll


def createFireballScroll(scene: Scene, x: int, y: int) -> Entity:
    scroll = scene.create()
    scroll.add(Position(x, y))
    scroll.add(Renderable(")", 2, (255, 0, 255, 255)))
    scroll.add(Name('Fireball Scroll'))
    scroll.add(Item())
    scroll.add(Consumable())
    scroll.add(Ranged(6))
    scroll.add(InflictsDamage(20))
    scroll.add(AreaOfEffect(3))
    scroll.add(GUIDescription())
    return scroll


def createConfusionScroll(scene: Scene, x: int, y: int) -> Entity:
    scroll = scene.create()
    scroll.add(Position(x, y))
    scroll.add(Renderable(")", 2, (255, 0, 255, 255)))
    scroll.add(Name('Confusion Scroll'))
    scroll.add(Item())
    scroll.add(Consumable())
    scroll.add(Ranged(6))
    scroll.add(Confusion(4))
    scroll.add(GUIDescription())
    return scroll


def createDagger(scene:Scene, x:int, y:int) -> Entity:
    dagger = scene.create()
    dagger.add(Position(x, y))
    dagger.add(Renderable("/", 2, (0, 255, 255, 255)))
    dagger.add(Name('Dagger'))
    dagger.add(Item())
    dagger.add(MeleePowerBonus(2))
    dagger.add(GUIDescription())
    dagger.add(Equippable(Equippable.MELEE))
    return dagger


def createShield(scene:Scene, x:int, y:int) -> Entity:
    shield = scene.create()
    shield.add(Position(x, y))
    shield.add(Renderable("(", 2, (0, 255, 255, 255)))
    shield.add(Name('Shield'))
    shield.add(Item())
    shield.add(DefenseBonus(1))
    shield.add(GUIDescription())
    shield.add(Equippable(Equippable.SHIELD))
    return shield


def createLongSword(scene:Scene, x:int, y:int) -> Entity:
    sword = scene.create()
    sword.add(Position(x, y))
    sword.add(Renderable("/", 2, (0, 255, 255, 255)))
    sword.add(Name('Long Sword'))
    sword.add(Item())
    sword.add(MeleePowerBonus(4))
    sword.add(GUIDescription())
    sword.add(Equippable(Equippable.MELEE))
    return sword

def createTowerShield(scene:Scene, x:int, y:int) -> Entity:
    shield = scene.create()
    shield.add(Position(x, y))
    shield.add(Renderable("(", 2, (0, 255, 255, 255)))
    shield.add(Name('Tower Shield'))
    shield.add(Item())
    shield.add(DefenseBonus(3))
    shield.add(GUIDescription())
    shield.add(Equippable(Equippable.SHIELD))
    return shield


def createParticle(scene:Scene, x:int, y:int, glyph:str, foreground:Color = (255,255,255,255), lifetime:int = 2):
    particle = scene.create()
    particle.add(Position(x,y))
    particle.add(Renderable(glyph, 100, foreground))
    particle.add(ParticleLifetime(lifetime))
    return particle


def createRations(scene:Scene, x:int, y:int) -> Entity:
    rations = scene.create()
    rations.add(Position(x, y))
    rations.add(Renderable("%", 2, (0, 255, 0, 255)))
    rations.add(Name('Rations'))
    rations.add(Item())
    rations.add(ProvidesFood())
    rations.add(GUIDescription())
    rations.add(Consumable())
    return rations


def createMagicMapperScroll(scene: Scene, x: int, y: int) -> Entity:
    scroll = scene.create()
    scroll.add(Position(x, y))
    scroll.add(Renderable(")", 2, (255, 0, 255, 255)))
    scroll.add(Name('Scroll of Magic Mapping'))
    scroll.add(Item())
    scroll.add(Consumable())
    scroll.add(MagicMapper())
    scroll.add(GUIDescription())
    return scroll