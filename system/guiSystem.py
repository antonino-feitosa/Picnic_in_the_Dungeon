
from enum import Enum
from algorithms.point import Point
from component import CombatStats, GUIDescription, InBackpack, Item, Name, Player, Position, Viewshed
from core import ECS, Entity
from device import Font
from map import Map


def guiSystem():
    entities = ECS.scene.filter(GUIDescription.id)
    player:Entity = ECS.scene.retrieve("player")
    font:Font = ECS.scene.retrieve("font")

    font.background = (0, 0, 0, 255)
    font.foreground = (200, 200, 200, 255)
    
    message = ''
    for entity in sorted(entities, key = lambda e: 0 if e.has(Player.id) else e.id):
        space = ''
        showing = True
        if entity.has(Position.id):
            position:Position = entity[Position.id]
            viewshed:Viewshed = player[Viewshed.id]
            showing = Point(position.x, position.y) in viewshed.visibleTiles
        if showing:
            if entity.has(Name.id):
                space = '  '
                name = entity[Name.id]
                stats = ''
                if entity.has(CombatStats.id):
                    combatStats:CombatStats = entity[CombatStats.id]
                    stats += ' ' + str(combatStats)
                message += name.name + stats + '\n'
                
            desc: GUIDescription = entity[GUIDescription.id]
            for msg in desc.description:
                message += space + msg + '\n'
            message += '\n'
    font.drawAtScreen(message, 10, 10)
    drawTooltips()


def drawTooltips():
    (ux, uy) = ECS.scene.retrieve("pixels unit")
    map:Map = ECS.scene.retrieve("map")
    font:Font = ECS.scene.retrieve("font")
    position = ECS.context.mousePosition
    point = Point(position.x // ux, position.y // uy)
    content = map.tileContent
    if point in content and content[point]:
        entity = content[point][0]
        if entity.has(Name.id):
            component:Name = entity[Name.id]
            name = ' ' + component.name + ' '
            font.background = (255, 255, 255, 255)
            font.foreground = (  0, 200,   0, 255)
            font.drawAtScreen(name, (point.x + 2) * ux, point.y * uy)

class ItemMenuResult(Enum):
    NoResponse = 0,
    Cancel = 1
    Selected = 2

def showInventory(keys: set[str]) -> tuple[ItemMenuResult, Entity | None]:
    ux, uy = ECS.scene.retrieve("pixels unit")
    player:Entity = ECS.scene.retrieve('player')
    font:Font = ECS.scene.retrieve('font')
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
        itemName:Name = item[Name.id]
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
    player:Entity = ECS.scene.retrieve('player')
    font:Font = ECS.scene.retrieve('font')
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
        itemName:Name = item[Name.id]
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
