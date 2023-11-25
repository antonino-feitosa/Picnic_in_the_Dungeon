
import os.path

from enum import Enum
from algorithms.point import Point
from component import CombatStats, GUIDescription, InBackpack, Item, Name, Player, Position, Renderable, Viewshed
from core import ECS, Entity
from device import Font


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


def guiSystem():
    entities = ECS.scene.filter(GUIDescription.id | Position.id)
    player: Entity = ECS.scene.retrieve("player")
    font: Font = ECS.scene.retrieve("font")
    (ux, uy) = ECS.scene.retrieve("pixels unit")

    font.background = (0, 0, 0, 255)
    font.foreground = (200, 200, 200, 255)

    messages = []
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
                stats = ''
                if entity.has(CombatStats.id):
                    combatStats: CombatStats = entity[CombatStats.id]
                    stats += ' ' + str(combatStats)
                messages.append(name.name + stats)

            desc: GUIDescription = entity[GUIDescription.id]
            for msg in desc.description:
                messages.append(space + msg)
    
    for i in range(len(messages)):
        message = messages[i]
        font.drawAtScreen(message, 10, 10 + i * uy)
    drawTooltips()


# TODO item and monster at same position
def drawTooltips():
    entities = ECS.scene.filter(Position.id | Name.id | Renderable.id)
    (ux, uy) = ECS.scene.retrieve("pixels unit")
    font: Font = ECS.scene.retrieve("font")
    position = ECS.context.mousePosition
    point = Point(position.x // ux, position.y // uy)
    for entity in sorted(entities, key=lambda entity: entity[Renderable.id].render_order, reverse=True):
        entityPosition: Position = entity[Position.id]
        if point.x == entityPosition.x and point.y == entityPosition.y:
            component: Name = entity[Name.id]
            name = ' ' + component.name + ' '
            font.background = (255, 255, 255, 255)
            font.foreground = (0, 200,   0, 255)
            font.drawAtScreen(name, (point.x + 2) * ux, point.y * uy)




def showInventory(keys: set[str]) -> tuple[ItemMenuResult, Entity | None]:
    ux, uy = ECS.scene.retrieve("pixels unit")
    player: Entity = ECS.scene.retrieve('player')
    font: Font = ECS.scene.retrieve('font')
    items = ECS.scene.filter(InBackpack.id | Item.id)
    items = [item for item in items if item[InBackpack.id].owner == player]
    index = ord('a')
    y = 200
    x = 400
    font.background = (255, 255, 255, 255)
    font.foreground = (127, 0, 127, 255)
    font.drawAtScreen('  Inventory (ESC to cancel)', x, y)
    y += uy
    y += uy
    for item in items:
        itemName: Name = item[Name.id]
        font.drawAtScreen(f' ({chr(index)}): {itemName.name}', x, y)
        index += 1
        y += uy

    if 'escape' in keys:
        return (ItemMenuResult.Cancel, None)

    index = ord('a')
    for item in items:
        if chr(index) in keys:
            return (ItemMenuResult.Selected, item)

    return (ItemMenuResult.NoResponse, None)


def dropItemMenu(keys: set[str]) -> tuple[ItemMenuResult, Entity | None]:
    ux, uy = ECS.scene.retrieve("pixels unit")
    player: Entity = ECS.scene.retrieve('player')
    font: Font = ECS.scene.retrieve('font')
    items = ECS.scene.filter(InBackpack.id | Item.id)
    items = [item for item in items if item[InBackpack.id].owner == player]
    index = ord('a')
    y = 200
    x = 400
    font.background = (255, 255, 255, 255)
    font.foreground = (127, 0, 127, 255)
    font.drawAtScreen('  Drop Which Item? (ESC to cancel)', x, y)
    y += uy
    y += uy
    for item in items:
        itemName: Name = item[Name.id]
        font.drawAtScreen(f' ({chr(index)}): {itemName.name}', x, y)
        index += 1
        y += uy

    if 'escape' in keys:
        return (ItemMenuResult.Cancel, None)

    index = ord('a')
    for item in items:
        if chr(index) in keys:
            return (ItemMenuResult.Selected, item)

    return (ItemMenuResult.NoResponse, None)


def rangedTarget(range: int) -> tuple[ItemMenuResult, Point | None]:
    player = ECS.scene.retrieve("player")
    font: Font = ECS.scene.retrieve('font')
    playerPosition: Position = player[Position.id]
    playerPoint = Point(playerPosition.x, playerPosition.y)
    viewshed: Viewshed = player[Viewshed.id]
    (ux, uy) = ECS.scene.retrieve("pixels unit")
    mousePosition = ECS.context.mousePosition
    mousePoint = Point(mousePosition.x // ux, mousePosition.y // uy)
    if mousePoint in viewshed.visibleTiles and mousePoint.distanceSquare(playerPoint) <= range:
        font.background = (0, 255, 0, 100)
        font.drawAtScreen('@', mousePoint.x * ux, mousePoint.y * uy)
        if ECS.context.mouseLeftPressed:
            return (ItemMenuResult.Selected, mousePoint)
    else:
        font.background = (255, 0, 0, 100)
        font.drawAtScreen('@', mousePoint.x * ux, mousePoint.y * uy)
        if ECS.context.mouseLeftPressed:
            return (ItemMenuResult.Cancel, None)
    return (ItemMenuResult.NoResponse, None)



waiting = 0
menuState = 0
def showMenu(keys: set[str]) -> MainMenuResult:
    font: Font = ECS.scene.retrieve('font')
    if "escape" in keys:
        return MainMenuResult.Quit
    else:
        global menuState
        if "return" in keys:
            match menuState:
                case 0: return MainMenuResult.NewGame
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
        for i in range(0,4):
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
            font.drawAtScreen("Font: GNU Unifont Glyphs (GNU GPLv2+)", 400, 260)
            font.drawAtScreen("https://unifoundry.com/unifont/index.html", 400, 280)
            font.drawAtScreen("Images: Antonino Feitosa", 400, 320)
            
    return MainMenuResult.NoResponse
