
import pickle

from enum import Enum
from algorithms import Random, Point
from component import Player, Position, Ranged, Renderable, Name, Viewshed, WantsToUseItem, WantsToDropItem
from core import ECS, Context, Entity, Scene
from device import Device, Font, Image
from map import drawMap, Map
from player import getItem, tryMovePlayer
from spawner import MAP_HEIGHT, MAP_WIDTH, createPlayer, spawnRoom
from system.damage import damageSystem, deleteTheDead
from system.guiSystem import ItemMenuResult, MainMenuResult, dropItemMenu, guiSystem, rangedTarget, showInventory, showMenu
from system.inventorySystem import itemCollectionSystem, itemDropSystem, itemUseSystem
from system.mapIndexSystem import mapIndexSystem
from system.meleeCombatSystem import meleeCombatSystem
from system.monsterAI import monsterAISystem
from system.visibility import visibilitySystem
from utils import Logger


class RunState(Enum):
    MainMenu = 0
    WaitingInput = 1
    PlayerTurn = 2
    MonsterTurn = 3
    ShowInventory = 4
    DropItem = 5
    ShowTargeting = 6
    NextLevel = 7


def playerInput(keys: set[str]) -> RunState:
    if "k" in keys or "[8]" in keys or "up" in keys:
        tryMovePlayer(0, -1)
    elif "j" in keys or "[2]" in keys or "down" in keys:
        tryMovePlayer(0, +1)
    elif "h" in keys or "[4]" in keys or "left" in keys:
        tryMovePlayer(-1, 0)
    elif "l" in keys or "[6]" in keys or "right" in keys:
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
            logger: Logger = ECS.scene.retrieve("logger")
            logger.log("There is nothing here to pick up.")
            return RunState.WaitingInput
    elif "i" in keys:
        return RunState.ShowInventory
    elif "d" in keys:
        return RunState.DropItem
    elif '.' in keys:
        # TODO
        # Try Next Level
        pass
    else:
        return RunState.WaitingInput
    return RunState.PlayerTurn


def runSystems():
    runState: RunState = ECS.scene.retrieve("state")
    visibilitySystem()
    if runState == RunState.MonsterTurn:
        monsterAISystem()
    mapIndexSystem()
    itemCollectionSystem()
    itemUseSystem()
    itemDropSystem()
    meleeCombatSystem()
    damageSystem()
    deleteTheDead()

def processGameStates():
    runState: RunState = ECS.scene.retrieve("state")
    if runState == RunState.MainMenu:
        response = showMenu(ECS.context.keys)
        if response == MainMenuResult.Quit:
            exit(0)
        elif response == MainMenuResult.NewGame:
            runState = RunState.PlayerTurn
        elif response == MainMenuResult.Continue:
            loadState()
            runState = RunState.WaitingInput
    elif runState == RunState.PlayerTurn:
        runSystems()
        runState = RunState.MonsterTurn
    elif runState == RunState.MonsterTurn:
        runSystems()
        turn:int = ECS.scene.retrieve("turn")
        ECS.scene.store("turn", turn + 1)
        saveState()
        runState = RunState.WaitingInput
    elif runState == RunState.WaitingInput:
        runState = playerInput(ECS.context.keys)
    ECS.scene.store("state", runState)


def processInventoryStates():
    runState: RunState = ECS.scene.retrieve("state")

    if runState == RunState.ShowInventory:
        result, entity = showInventory(ECS.context.keys)
        if result == ItemMenuResult.Cancel:
            runState = RunState.WaitingInput
        elif result == ItemMenuResult.Selected and entity is not None:
            if entity.has(Ranged.id):
                ranged: Ranged = entity[Ranged.id]
                ECS.scene.store("targeting range", ranged.range)
                ECS.scene.store("targeting element", entity)
                runState = RunState.ShowTargeting
            else:
                player: Entity = ECS.scene.retrieve('player')
                player.add(WantsToUseItem(entity))
                runState = RunState.PlayerTurn
    elif runState == RunState.DropItem:
        result, entity = dropItemMenu(ECS.context.keys)
        if result == ItemMenuResult.Cancel:
            runState = RunState.WaitingInput
        elif result == ItemMenuResult.Selected and entity is not None:
            player: Entity = ECS.scene.retrieve('player')
            player.add(WantsToDropItem(entity))
            runState = RunState.PlayerTurn
    elif runState == RunState.ShowTargeting:
        range: int = ECS.scene.retrieve("targeting range")
        result, point = rangedTarget(range)
        if result == ItemMenuResult.Cancel:
            runState = RunState.WaitingInput
        elif result == ItemMenuResult.Selected and point is not None:
            targeting: Entity = ECS.scene.retrieve("targeting element")
            player: Entity = ECS.scene.retrieve('player')
            player.add(WantsToUseItem(targeting, point))
            runState = RunState.PlayerTurn
    ECS.scene.store("state", runState)


def update():
    processGameStates()
    runState: RunState = ECS.scene.retrieve("state")
    if runState == RunState.MainMenu:
        return

    drawMap()
    font:Font = ECS.scene.retrieve("font")
    background:Image = ECS.scene.retrieve("background")
    map: Map = ECS.scene.retrieve("map")
    width, height = ECS.scene.retrieve("pixels unit")
    entities = ECS.scene.filter(Position.id | Renderable.id)
    for entity in sorted(entities, key=lambda entity: entity[Renderable.id].render_order, reverse=True):
        position: Position = entity[Position.id]
        if Point(position.x, position.y) in map.visibleTiles:
            render: Renderable = entity[Renderable.id]
            image = background.clone()
            font.foreground = render.foreground
            image.fill(render.background)
            font.drawAtImageCenter(render.glyph, image)
            image.draw(position.x * width, position.y * height)

    processInventoryStates()
    logger: Logger = ECS.scene.retrieve("logger")
    guiSystem()
    logger.print()


def saveState():
    data = dict()
    logger: Logger = ECS.scene.retrieve("logger")
    data["state"] = ECS.scene.retrieve("state")
    data["turn"] = ECS.scene.retrieve("turn")
    data["map"] = ECS.scene.retrieve("map")
    data["logger messages"] = logger.messages
    data["entitities"] = ECS.scene.entities
    with open("./save.data", "wb") as outfile:
        pickle.dump(data, outfile)


def loadState():
    logger: Logger = ECS.scene.retrieve("logger")
    with open("./save.data", "rb") as infile:  
        data = pickle.load(infile)
        logger.messages = data["logger messages"]
        ECS.scene.store("state", data["state"])
        ECS.scene.store("turn", data["turn"])
        ECS.scene.store("map", data["map"])
        ECS.scene.entities = data["entitities"]
        player = ECS.scene.filter(Player.id)
        player = list(player)[0]
        ECS.scene.store("player", player)
        viewshed:Viewshed = player[Viewshed.id]
        viewshed.dirty = True


def main():
    rand = Random(0)
    device = Device("Picnic in the Dungeon", tick=24, width=1280, height=640)

    background = device.loadImage("./_resources/_roguelike/background.png")
    font = device.loadFont("./art/ConsolaMono-Bold.ttf", 16)
    pixelsUnit = 16

    map = Map(MAP_WIDTH, MAP_HEIGHT)
    # map.newMapRoomsAndCorridors(rand)
    map.newTestMap()
    xplayer, yplayer = map.rooms[0].center()
    logger = Logger(font, 10, 10, 300)

    scene = Scene()
    scene.store("state", RunState.MainMenu)

    scene.store("background", background)
    scene.store("font", font)
    scene.store("rand", rand)

    scene.store("map", map)
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
    device.onMove.append(lambda x, y: setattr(
        ECS.context, 'mousePosition', Point(x, y)))
    device.onClick.append(lambda pressed, x, y: setattr(
        ECS.context, 'mouseLeftPressed', pressed))

    while device.running:
        device.clear()
        device.loop()
        device.draw()


if __name__ == "__main__":
    main()
