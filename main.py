from enum import Enum
from algorithms import Random, Point
from component import BlocksTile, CombatStats, GUIDescription, Glyph, Monster, Name, Player, Position, Renderable, Viewshed
from core import ECS, Scene
from device import Device, Font
from map import drawMap, Map
from player import playerInput
from system.damage import damageSystem, deleteTheDead
from system.guiSystem import guiSystem
from system.mapIndexSystem import mapIndexSystem
from system.meleeCombatSystem import meleeCombatSystem
from system.monsterAI import monsterAISystem
from system.visibility import visibilitySystem


class RunState(Enum):
    Paused = 0,
    Running = 1

runState = RunState.Running

def update():
    global runState

    logger:list[str] = ECS.scene.retrieve("logger")
    if runState == RunState.Running:
        if logger:
            logger.pop()
        visibilitySystem()
        monsterAISystem()
        mapIndexSystem()
        meleeCombatSystem()
        damageSystem()
        deleteTheDead()
        runState = RunState.Paused

    drawMap()
    map: Map = ECS.scene.retrieve("map")
    width, height = ECS.scene.retrieve("pixels unit")
    entities = ECS.scene.filter(Position.id | Renderable.id)
    for entity in entities:
        position: Position = entity[Position.id]
        if Point(position.x, position.y) in map.visibleTiles:
            render: Renderable = entity[Renderable.id]
            render.glyph.draw(position.x * width, position.y * height)
    guiSystem()

    font:Font = ECS.scene.retrieve("font")
    font.background = (0, 0, 0, 0)
    font.foreground = (200, 200, 200, 255)
    size = len(logger)
    if size > 10:
        logger = logger[-10:]
        ECS.scene.store("logger", logger)
    msg = "\n".join(logger)
    font.drawAtScreen(msg, 10, 300)    



def processInput(keys:set[str]):
    global runState
    if runState == RunState.Paused and playerInput(keys):
        runState = RunState.Running


def main():
    device = Device("Picnic in the Dungeon", tick=12, width=1280, height=640)

    background = device.loadImage("./_resources/_roguelike/background.png")
    font = device.loadFont("./_resources/_roguelike/gadaj.otf", 16)
    rand = Random(6)
    glyphWall = Glyph(background, font, "#")
    glyphWall.foreground = (0, 255, 0, 255)
    glyphFloor = Glyph(background, font, ".")
    glyphFloor.foreground = (127, 127, 127, 255)
    width, height = 80, 40
    pixelsUnit = 16

    map = Map(width, height)
    map.newMapRoomsAndCorridors(rand)
    xplayer, yplayer = map.rooms[0].center()
    logger:list[str] = []

    scene = Scene()
    scene.store("background", background)
    scene.store("font", font)
    scene.store("rand", rand)
    
    scene.store("map", map)
    scene.store("glyph wall", glyphWall)
    scene.store("glyph floor", glyphFloor)
    scene.store("pixels unit", (pixelsUnit, pixelsUnit))
    scene.store("logger", logger)

    player = scene.create()
    player.add(Position(xplayer, yplayer))
    player.add(Renderable(Glyph(background, font, "@")))
    player.add(Player())
    player.add(Viewshed(8))
    player.add(CombatStats(30, 2, 5))
    player.add(Name("Player"))
    player.add(GUIDescription())

    scene.store("player", player)

    count = 1
    for room in map.rooms[1:]:
        x, y = room.center()
        monsterType = "g" if rand.nextBool() else "o"
        monsterName = "Goblin" if monsterType == "g" else "Orc"
        monsterName = f"{monsterName} #{count}"
        count += 1
        render = Renderable(Glyph(background, font, monsterType))
        render.glyph.foreground = (255, 0, 0, 255)
        monster = scene.create()
        monster.add(Position(x,y))
        monster.add(render)
        monster.add(Viewshed(8))
        monster.add(Monster())
        monster.add(Name(monsterName))
        monster.add(BlocksTile())
        monster.add(CombatStats(16, 1, 4))
        monster.add(GUIDescription())

    device.onLoop.append(update)
    device.onPressed.append(processInput)

    ECS.scene = scene

    while device.running:
        device.clear()
        device.loop()
        device.draw()


if __name__ == "__main__":
    main()
