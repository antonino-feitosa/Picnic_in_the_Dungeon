
import os
import pickle

from algorithms import Random, Point
from component import CombatStats, Equipped, Hidden, HungerClock, InBackpack, Player, Position, Ranged, Renderable, Name, Viewshed, WantsToRemoveItem, WantsToUseItem, WantsToDropItem
from core import ECS, Context, Entity, Scene
from device import Device, Font
from glyphScreen import GlyphScreen
from map import TileType, drawMap, Map
from map_builders.mapBuilder import MapBuilder
from player import getItem, tryMovePlayer
from runState import RunState
from spawner import createPlayer
from system.hungerSystem import hungerSystem
from system.damageSystem import damageSystem, deleteTheDead
from system.guiSystem import GameOverResult, ItemMenuResult, MainMenuResult, dropItemMenu, guiSystem, rangedTarget, removeItemMenu, showGameOver, showInventory, showMenu
from system.inventorySystem import itemCollectionSystem, itemDropSystem, itemRemoveSystem, itemUseSystem
from system.mapIndexSystem import mapIndexSystem
from system.meleeCombatSystem import meleeCombatSystem
from system.monsterAI import monsterAISystem
from system.particleSystem import cullDeadParticles, drawParticles
from system.triggerSystem import triggerSystem
from system.visibilitySystem import visibilitySystem
from utils import Logger

SAVE_DATA_FILE_NAME = "./save.data"


def tryNextLevel() -> bool:
    map: Map = ECS.scene.retrieve("map")
    player: Entity = ECS.scene.retrieve("player")
    position: Position = player.get(Position.id)
    point = Point(position.x, position.y)
    if point in map.tiles and map.tiles[point] == TileType.DownStairs:
        return True
    return False


def skipTurn() -> None:
    player: Entity = ECS.scene.retrieve("player")
    map: Map = ECS.scene.retrieve("map")
    canHeal = True
    for pos in map.visibleTiles:
        if pos in map.tileContent:
            for entity in map.tileContent[pos]:
                if not entity.has(Player.id) and entity.has(CombatStats.id):
                    canHeal = False
    
    hunger:HungerClock = player[HungerClock.id]
    if hunger.hungerState == HungerClock.STARVING or hunger.hungerState == HungerClock.HUNGRY:
        canHeal = False

    if canHeal:
        stats: CombatStats = player.get(CombatStats.id)
        stats.HP = min(stats.maxHP, stats.HP + 1)


def gotoNextLevel() -> None:
    rand:Random = ECS.scene.retrieve("random")
    player: Entity = ECS.scene.retrieve("player")
    equips = ECS.scene.filter(Equipped.id)
    entities = ECS.scene.filter(InBackpack.id)
    entities.add(player)
    entities.update(equips)
    ECS.scene.entities = entities

    map:Map = ECS.scene.retrieve("map")
    builder = MapBuilder()
    builder.build(map.depth + 1)
    builder.spawn()
    ECS.scene.store("map", builder.map)

    position: Position = player.get(Position.id)
    position.x = builder.startPosition.x
    position.y = builder.startPosition.y
    viewshed: Viewshed = player.get(Viewshed.id)
    viewshed.dirty = True

    logger: Logger = ECS.scene.retrieve("logger")
    logger.log("You descend to the next level, and take a moment to heal.")
    stats: CombatStats = player.get(CombatStats.id)
    stats.HP = max((stats.maxHP + 1) // 2, stats.HP)


def cleanupGameOver():
    ECS.scene.entities.clear()

    builder = MapBuilder()
    builder.build(1)
    builder.spawn()
    ECS.scene.store("map", builder.map)
    player = createPlayer(ECS.scene, builder.startPosition.x, builder.startPosition.y)
    ECS.scene.store("player", player)
    
    logger: Logger = ECS.scene.retrieve("logger")
    logger.clear()

    os.remove(SAVE_DATA_FILE_NAME)
    ECS.scene.store("turn", 1)
    


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
        ECS.context.clear()
        if not getItem():
            logger: Logger = ECS.scene.retrieve("logger")
            logger.log("There is nothing here to pick up.")
    elif "i" in keys:
        ECS.context.clear()
        return RunState.ShowInventory
    elif "d" in keys:
        ECS.context.clear()
        return RunState.ShowDropItem
    elif "r" in keys:
        ECS.context.clear()
        return RunState.ShowRemoveItem
    elif '.' in keys:
        ECS.context.clear()
        if tryNextLevel():
            return RunState.NextLevel
        else:
            logger: Logger = ECS.scene.retrieve("logger")
            logger.log("There is no way down from here.")
            return RunState.WaitingInput
    elif 'space' in keys:
        ECS.context.clear()
        skipTurn()
        logger: Logger = ECS.scene.retrieve("logger")
        logger.log("Turn skipped.")
    else:
        return RunState.WaitingInput
    return RunState.PlayerTurn


def runSystems():
    runState: RunState = ECS.scene.retrieve("state")
    visibilitySystem()
    if runState == RunState.MonsterTurn:
        monsterAISystem()
    mapIndexSystem()
    triggerSystem()
    itemCollectionSystem()
    itemUseSystem()
    itemDropSystem()
    itemRemoveSystem()
    meleeCombatSystem()
    damageSystem()
    hungerSystem()
    deleteTheDead()


def processBeforeDraw():
    runState: RunState = ECS.scene.retrieve("state")
    if runState == RunState.MainMenu:
        response = showMenu(ECS.context.keys)
        if response == MainMenuResult.Quit:
            exit(0)
        elif response == MainMenuResult.NewGame:
            runState = RunState.PlayerTurn
        elif response == MainMenuResult.Continue:
            loadState()
            runState = ECS.scene.retrieve("state")
    elif runState == RunState.PlayerTurn:
        runSystems()
        runState = RunState.MonsterTurn
    elif runState == RunState.MonsterTurn:
        runSystems()
        player: Entity = ECS.scene.retrieve("player")
        stats: CombatStats = player.get(CombatStats.id)
        if stats.HP <= 0:
            ECS.context.clear()
            runState = RunState.GameOver
        else:
            turn: int = ECS.scene.retrieve("turn")
            ECS.scene.store("turn", turn + 1)
            runState = RunState.WaitingInput
        ECS.scene.store("state", runState)
        saveState()
    elif runState == RunState.WaitingInput:
        runState = playerInput(ECS.context.keys)
    elif runState == RunState.NextLevel:
        gotoNextLevel()
        runSystems()
        runState = RunState.WaitingInput
    ECS.scene.store("state", runState)


def processAfterDraw(screen: GlyphScreen):
    runState: RunState = ECS.scene.retrieve("state")

    if runState == RunState.ShowInventory:
        result, entity = showInventory(ECS.context.keys)
        if result == ItemMenuResult.Cancel:
            runState = RunState.WaitingInput
        elif result == ItemMenuResult.Selected and entity is not None:
            if entity.has(Ranged.id):
                ECS.scene.store("targeting element", entity)
                runState = RunState.ShowTargeting
            else:
                player: Entity = ECS.scene.retrieve('player')
                player.add(WantsToUseItem(entity))
                runState = RunState.PlayerTurn
    elif runState == RunState.ShowDropItem:
        result, entity = dropItemMenu(ECS.context.keys)
        if result == ItemMenuResult.Cancel:
            runState = RunState.WaitingInput
        elif result == ItemMenuResult.Selected and entity is not None:
            player: Entity = ECS.scene.retrieve('player')
            player.add(WantsToDropItem(entity))
            runState = RunState.PlayerTurn
    elif runState == RunState.ShowRemoveItem:
        result, entity = removeItemMenu(ECS.context.keys)
        if result == ItemMenuResult.Cancel:
            runState = RunState.WaitingInput
        elif result == ItemMenuResult.Selected and entity is not None:
            player: Entity = ECS.scene.retrieve('player')
            player.add(WantsToRemoveItem(entity))
            runState = RunState.PlayerTurn
        pass
    elif runState == RunState.ShowTargeting:
        targeting: Entity = ECS.scene.retrieve("targeting element")
        result, point = rangedTarget(targeting, screen)
        if result == ItemMenuResult.Cancel:
            runState = RunState.WaitingInput
        elif result == ItemMenuResult.Selected and point is not None:
            player: Entity = ECS.scene.retrieve('player')
            player.add(WantsToUseItem(targeting, point))
            runState = RunState.PlayerTurn
    elif runState == RunState.GameOver:
        if showGameOver(ECS.context.keys) == GameOverResult.QuitToMenu:
            cleanupGameOver()
            runState = RunState.MainMenu
    ECS.scene.store("state", runState)


def update():
    processBeforeDraw()
    runState: RunState = ECS.scene.retrieve("state")
    if runState == RunState.MainMenu:
        return
    
    
    font: Font = ECS.scene.retrieve('font')
    cx, cy = ECS.scene.retrieve("camera")
    screen = GlyphScreen(80,40, font)
    screen.xoff = cx
    screen.yoff = cy
    map: Map = ECS.scene.retrieve("map")
    entities = ECS.scene.filter(Position.id | Renderable.id)

    drawMap(screen)
    for entity in sorted(entities, key=lambda entity: entity[Renderable.id].render_order, reverse=True):
        if not entity.has(Hidden.id):
            position: Position = entity[Position.id]
            if Point(position.x, position.y) in map.visibleTiles:
                render: Renderable = entity[Renderable.id]
                screen.setGlyph(position.x, position.y, render.glyph, render.foreground, render.background)
    drawParticles(screen)
    screen.draw()
    screen.clear()
    processAfterDraw(screen)
    guiSystem(screen)
    drawParticles(screen)
    cullDeadParticles()
    screen.draw()

    logger: Logger = ECS.scene.retrieve("logger")
    logger.print()


def saveState():
    data = dict()
    logger: Logger = ECS.scene.retrieve("logger")
    data["state"] = ECS.scene.retrieve("state")
    data["turn"] = ECS.scene.retrieve("turn")
    data["map"] = ECS.scene.retrieve("map")
    data["logger messages"] = logger.messages
    data["entitities"] = ECS.scene.entities
    with open(SAVE_DATA_FILE_NAME, "wb") as outfile:
        pickle.dump(data, outfile)


def loadState():
    logger: Logger = ECS.scene.retrieve("logger")
    with open(SAVE_DATA_FILE_NAME, "rb") as infile:
        data = pickle.load(infile)
        logger.messages = data["logger messages"]
        ECS.scene.store("state", data["state"])
        ECS.scene.store("turn", data["turn"])
        ECS.scene.store("map", data["map"])
        ECS.scene.entities = data["entitities"]
        player = ECS.scene.filter(Player.id)
        player = list(player)[0]
        ECS.scene.store("player", player)
        viewshed: Viewshed = player[Viewshed.id]
        viewshed.dirty = True


def main():
    rand = Random(0)
    device = Device("Picnic in the Dungeon", tick=32, width=1280, height=640)

    background = device.loadImage("./_resources/_roguelike/background.png")
    font = device.loadFont("./art/DejaVuSansMono-Bold.ttf", 16)
    logger = Logger(font, 10, 10, 300)

    scene = Scene()
    scene.store("state", RunState.MainMenu)
    scene.store("background", background)
    scene.store("font", font)
    scene.store("random", rand)
    scene.store("camera", (40, 0))
    scene.store("logger", logger)
    scene.store("turn", 1)

    ECS.scene = scene
    ECS.context = Context()

    builder = MapBuilder()
    builder.build(1)
    builder.spawn()
    player = createPlayer(scene, builder.startPosition.x, builder.startPosition.y)
    scene.store("player", player)
    scene.store("map", builder.map)

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
