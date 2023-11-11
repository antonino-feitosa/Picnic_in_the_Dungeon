
from algorithms.point import Point
from component import CombatStats, GUIDescription, Name, Player, Position, Viewshed
from core import ECS, Entity
from device import Font


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
