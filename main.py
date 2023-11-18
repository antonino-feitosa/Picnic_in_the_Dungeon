from enum import Enum
from algorithms import Random, Point
from component import BlocksTile, CombatStats, GUIDescription, Glyph, Monster, Name, Player, Position, Renderable, Viewshed
from core import ECS, Context, Scene
from device import Device, Font
from map import drawMap, Map
from player import getItem, tryMovePlayer
from spawner import MAP_HEIGHT, MAP_WIDTH, createPlayer, createRandomMonster, spawnRoom
from system.damage import damageSystem, deleteTheDead
from system.guiSystem import guiSystem
from system.inventorySystem import itemCollectionSystem
from system.mapIndexSystem import mapIndexSystem
from system.meleeCombatSystem import meleeCombatSystem
from system.monsterAI import monsterAISystem
from system.visibility import visibilitySystem
from utils import Logger


class RunState(Enum):
    WaitingInput = 0,
    Running = 1

runState = RunState.Running

def playerInput(keys: set[str]) -> bool:
    if "up" in keys or "k" in keys or "[8]" in keys:
        tryMovePlayer(0, -1)
    elif "down" in keys or "j" in keys or "[2]" in keys:
        tryMovePlayer(0, +1)
    elif "left" in keys or "h" in keys or "[4]" in keys:
        tryMovePlayer(-1, 0)
    elif "right" in keys or "l" in keys or "[6]" in keys:
        tryMovePlayer(+1, 0)
    elif "y" in keys or "[9]" in keys:
        tryMovePlayer(+1, -1)
    elif "u" in keys or "[7]" in keys:
        tryMovePlayer(-1, -1)
    elif "n" in keys or "[3]" in keys:
        tryMovePlayer(+1, +1)
    elif "b" in keys or "[1]" in keys:
        tryMovePlayer(-1, +1)
    elif "g" in keys or "[5]" in keys:
        if not getItem():
            logger:Logger = ECS.scene.retrieve("logger")
            logger.log("There is nothing here to pick up.")
            return False
    else:
        return False
    return True


def update():
    global runState
    logger:Logger = ECS.scene.retrieve("logger")
    
    if runState == RunState.Running:
        visibilitySystem()
        monsterAISystem()
        mapIndexSystem()
        meleeCombatSystem()
        damageSystem()
        deleteTheDead()
        mapIndexSystem()
        itemCollectionSystem()
        logger.turn += 1
        runState = RunState.WaitingInput
    elif runState == RunState.WaitingInput:
        if playerInput(ECS.context.keys):
            runState = RunState.Running

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
    logger.print()
    

def main():
    device = Device("Picnic in the Dungeon", tick=12, width=1280, height=640)

    background = device.loadImage("./_resources/_roguelike/background.png")
    font = device.loadFont("./_resources/_roguelike/gadaj.otf", 16)
    rand = Random(6)
    glyphWall = Glyph(background, font, "#")
    glyphWall.foreground = (0, 255, 0, 255)
    glyphFloor = Glyph(background, font, ".")
    glyphFloor.foreground = (127, 127, 127, 255)
    pixelsUnit = 16

    map = Map(MAP_WIDTH, MAP_HEIGHT)
    map.newMapRoomsAndCorridors(rand)
    xplayer, yplayer = map.rooms[0].center()
    logger = Logger(font, 10, 10, 300)

    scene = Scene()
    scene.store("background", background)
    scene.store("font", font)
    scene.store("rand", rand)
    
    scene.store("map", map)
    scene.store("glyph wall", glyphWall)
    scene.store("glyph floor", glyphFloor)
    scene.store("pixels unit", (pixelsUnit, pixelsUnit))
    scene.store("logger", logger)
    scene.store("turn", 1)

    ECS.scene = scene
    ECS.context = Context()

    player = createPlayer(scene, xplayer, yplayer)
    scene.store("player", player)

    for room in map.rooms[1:]:
        spawnRoom(scene, room)

    device.onLoop.append(update)
    device.onKeyPressed.append(lambda keys: setattr(ECS.context, 'keys', keys))
    device.onMove.append(lambda x, y: setattr(ECS.context, 'mousePosition', Point(x,y)))
    device.onClick.append(lambda pressed, x, y: setattr(ECS.context, 'mouseLeftPressed', pressed))

    while device.running:
        device.clear()
        device.loop()
        device.draw()


if __name__ == "__main__":
    main()
