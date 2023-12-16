

import os.path

from enum import Enum
from algorithms.point import Point
from component import AreaOfEffect, CombatStats, Equippable, Equipped, GUIDescription, InBackpack, Item, Name, Player, Position, Ranged, Renderable, Viewshed
from core import ECS, Entity
from device import Color, Font
from glyphScreen import GlyphScreen
from map import Map
from system.meleeCombatSystem import getDefensiveBonus, getOffensiveBonus
from utils import Logger


class ItemMenuResult(Enum):
    NoResponse = 0
    Cancel = 1
    Selected = 2


class MainMenuResult(Enum):
    NoResponse = 0
    Quit = 1
    NewGame = 2
    Continue = 3
    About = 4


class GameOverResult(Enum):
    NoResponse = 0
    QuitToMenu = 1


def guiSystem(screen: GlyphScreen):
    entities = ECS.scene.filter(GUIDescription.id | Position.id)
    player: Entity = ECS.scene.retrieve("player")
    font: Font = ECS.scene.retrieve("font")
    map: Map = ECS.scene.retrieve("map")

    font.background = (0, 0, 0, 255)
    font.foreground = (200, 200, 200, 255)

    messages = [f"Depth: {map.depth}"]
    for entity in sorted(entities, key=lambda e: 0 if e.has(Player.id) else e.id):
        space = ''
        showing = True
        if entity.has(Position.id):
            position: Position = entity[Position.id]
            viewshed: Viewshed = player[Viewshed.id]
            showing = Point(position.x, position.y) in viewshed.visibleTiles
        if showing:
            if entity.has(Name.id):
                space = '  '

                name = entity[Name.id]
                statsMsg = ""
                if entity.has(CombatStats.id):
                    stats: CombatStats = entity[CombatStats.id]
                    offensiveBonus = getOffensiveBonus(entity)
                    defensiveBonus = getDefensiveBonus(entity)
                    statsMsg = f" HP:{stats.HP}/{stats.maxHP}"
                    statsMsg += f" P:{stats.power + offensiveBonus} D:{stats.defense + defensiveBonus}"
                
                hungerMsg = ""
                if entity.has(HungerClock.id):
                    hunger:HungerClock = entity[HungerClock.id]
                    hungerMsg = f" ({hunger.hungerState}  {hunger.duration})"

                messages.append(name.name + statsMsg + hungerMsg)

                equips = ECS.scene.filter(Name.id | Equipped.id)
                for equippedEntity in equips:
                    equipped: Equipped = equippedEntity[Equipped.id]
                    equippedName: Name = equippedEntity[Name.id]
                    if equipped.owner == entity:
                        msg = f"    {equipped.slot}: {equippedName.name}"
                        messages.append(msg)

                if entity.has(GUIDescription.id):
                    desc: GUIDescription = entity[GUIDescription.id]
                    messages.append(space + desc.description)

    for i in range(len(messages)):
        message = messages[i]
        font.drawAtScreen(message, 10, 10 + i * font.size)
    drawTooltips(screen)


# TODO item and monster at same position
def drawTooltips(screen: GlyphScreen):
    map: Map = ECS.scene.retrieve("map")
    entities = ECS.scene.filter(Position.id | Name.id | Renderable.id)
    position = ECS.context.mousePosition
    x, y = screen.screenPositionToGrid(position.x, position.y)
    point = Point(x, y)
    for entity in sorted(entities, key=lambda entity: entity[Renderable.id].render_order, reverse=True):
        entityPosition: Position = entity[Position.id]
        if point in map.visibleTiles and point.x == entityPosition.x and point.y == entityPosition.y:
            component: Name = entity[Name.id]
            name = ' ' + component.name + ' '
            screen.setGlyph(point.x + 1, point.y, name, bgColor= (100, 100, 100, 155))


def showInventory(keys: set[str]) -> tuple[ItemMenuResult, Entity | None]:
    player: Entity = ECS.scene.retrieve('player')
    font: Font = ECS.scene.retrieve('font')
    items = ECS.scene.filter(InBackpack.id | Item.id)
    items = [item for item in items if item[InBackpack.id].owner == player]
    index = ord('a')
    y = 200
    x = 400
    font.background = (255, 255, 255, 255)
    font.foreground = (127, 0, 127, 255)
    font.drawAtScreen('Inventory (ESC to cancel)'.center(40), x, y)

    y += font.size
    for item in items:
        itemName: Name = item[Name.id]
        font.drawAtScreen(f' ({chr(index)}): {itemName.name}'.ljust(40), x, y)
        index += 1
        y += font.size

    if 'escape' in keys:
        return (ItemMenuResult.Cancel, None)

    index = ord('a')
    for item in items:
        if chr(index) in keys:
            return (ItemMenuResult.Selected, item)
        index += 1

    return (ItemMenuResult.NoResponse, None)


def dropItemMenu(keys: set[str]) -> tuple[ItemMenuResult, Entity | None]:
    player: Entity = ECS.scene.retrieve('player')
    font: Font = ECS.scene.retrieve('font')
    items = ECS.scene.filter(InBackpack.id | Item.id)
    items = [item for item in items if item[InBackpack.id].owner == player]
    index = ord('a')
    y = 200
    x = 400
    font.background = (255, 255, 255, 255)
    font.foreground = (127, 0, 127, 255)
    font.drawAtScreen('  Drop Which Item? (ESC to cancel)'.center(40), x, y)
    y += font.size
    for item in items:
        itemName: Name = item[Name.id]
        font.drawAtScreen(f' ({chr(index)}): {itemName.name}'.ljust(40), x, y)
        index += 1
        y += font.size

    if 'escape' in keys:
        return (ItemMenuResult.Cancel, None)

    index = ord('a')
    for item in items:
        if chr(index) in keys:
            return (ItemMenuResult.Selected, item)

    return (ItemMenuResult.NoResponse, None)


def removeItemMenu(keys: set[str]) -> tuple[ItemMenuResult, Entity | None]:
    player: Entity = ECS.scene.retrieve('player')
    font: Font = ECS.scene.retrieve('font')
    items = ECS.scene.filter(Equipped.id | Item.id)
    items = [item for item in items if item[Equipped.id].owner == player]
    index = ord('a')
    y = 200
    x = 400
    font.background = (255, 255, 255, 255)
    font.foreground = (127, 0, 127, 255)
    font.drawAtScreen('  Remove Which Item? (ESC to cancel)'.center(40), x, y)
    y += font.size
    for item in items:
        itemName: Name = item[Name.id]
        font.drawAtScreen(f' ({chr(index)}): {itemName.name}'.ljust(40), x, y)
        index += 1
        y += font.size

    if 'escape' in keys:
        return (ItemMenuResult.Cancel, None)

    index = ord('a')
    for item in items:
        if chr(index) in keys:
            return (ItemMenuResult.Selected, item)

    return (ItemMenuResult.NoResponse, None)


def rangedTarget(targetingEntity: Entity, screen: GlyphScreen) -> tuple[ItemMenuResult, Point | None]:
    ranged:Ranged = targetingEntity[Ranged.id]
    itemRange: int = ranged.range
    player = ECS.scene.retrieve("player")
    playerPosition: Position = player[Position.id]
    playerPoint = Point(playerPosition.x, playerPosition.y)
    viewshed: Viewshed = player[Viewshed.id]
    mousePosition = ECS.context.mousePosition
    x, y = screen.screenPositionToGrid(mousePosition.x, mousePosition.y)
    mousePoint = Point(x, y)
    if mousePoint in viewshed.visibleTiles and mousePoint.distanceSquare(playerPoint) <= itemRange:
        for x in range(playerPoint.x - itemRange, playerPoint.x + itemRange + 1):
            for y in range(playerPoint.y - itemRange, playerPoint.y + itemRange + 1):
                if Point(x,y) in viewshed.visibleTiles:
                    screen.setBackground(x, y, (20, 50, 20, 10))
        
        if targetingEntity.has(AreaOfEffect.id):
            areaOfEffect:AreaOfEffect = targetingEntity[AreaOfEffect.id]
            area = areaOfEffect.radius
            for x in range(mousePoint.x - area, mousePoint.x + area + 1):
                for y in range(mousePoint.y - area, mousePoint.y + area + 1):
                    if Point(x,y) in viewshed.visibleTiles:
                        screen.setBackground(x, y, (30, 0, 0, 10))

        screen.setGlyph(mousePoint.x, mousePoint.y, '⊙', (176, 255, 55, 200), (20, 50, 20, 10))
        if ECS.context.mouseLeftPressed:
            return (ItemMenuResult.Selected, mousePoint)
    else:
        screen.setGlyph(mousePoint.x, mousePoint.y, '⊗', (255, 0, 0, 255))

        if ECS.context.mouseLeftPressed:
            return (ItemMenuResult.Cancel, None)
    if "escape" in ECS.context.keys:
        return (ItemMenuResult.Cancel, None)
    return (ItemMenuResult.NoResponse, None)


waiting = 0
menuState = 0
countFrames = 0


def showMenu(keys: set[str]) -> MainMenuResult:
    font: Font = ECS.scene.retrieve('font')
    if "escape" in keys:
        return MainMenuResult.Quit
    else:
        global menuState
        if "return" in keys:
            match menuState:
                case 0:
                    global countFrames
                    countFrames = 100
                    return MainMenuResult.NewGame
                case 1: return MainMenuResult.Continue
                case 3: return MainMenuResult.Quit

        existsSave = os.path.exists('./save.data')

        global waiting
        if waiting == 0:
            waiting = 2
            if "down" in keys or "[2]" in keys:
                menuState = min(menuState + 1, 3)
                if menuState == 1 and not existsSave:
                    menuState = 2
            if "up" in keys or "[8]" in keys:
                menuState = max(menuState - 1, 0)
                if menuState == 1 and not existsSave:
                    menuState = 0
        else:
            waiting -= 1

        text = ["New Game", "Continue", "About", "Quit"]
        for i in range(0, 4):
            font.background = (0, 0, 0, 255)
            font.foreground = (255, 255, 255, 255)
            if menuState == i:
                font.background = (127, 127, 127, 255)
            if i == 1 and not existsSave:
                font.foreground = (127, 127, 127, 255)
            font.drawAtScreen(text[i], 200, 200 + i * 20)

        font.background = (0, 0, 0, 255)
        if menuState == 2:
            font.drawAtScreen("Development: Antonino Feitosa", 400, 200)
            font.drawAtScreen("antonino_feitosa@yahoo.com.br", 400, 220)
            font.drawAtScreen("Font: DejaVu (Free License)", 400, 260)
            font.drawAtScreen("https://dejavu-fonts.github.io/License.html", 400, 280)
            font.drawAtScreen("Images: Antonino Feitosa", 400, 320)

    return MainMenuResult.NoResponse


def showGameOver(keys: set[str]) -> GameOverResult:
    global countFrames
    if keys and countFrames <= 0:
        return GameOverResult.QuitToMenu
    else:
        font: Font = ECS.scene.retrieve('font')
        font.foreground = (255, 255, 0, 255)
        font.drawAtScreen("          Your journey has ended!", 400, 200)
        font.foreground = (255, 255, 255, 255)
        font.drawAtScreen("One day, we'll tell you all about how you did.", 400, 240)
        font.drawAtScreen("That day, sadly, is not in this day..", 400, 255)

        if countFrames <= 0:
            font.foreground = (255, 0, 255, 255)
            font.drawAtScreen("Press any key to return to the menu.", 400, 295)
        else:
            countFrames -= 1

        return GameOverResult.NoResponse
