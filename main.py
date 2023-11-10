from algorithms import Random
from component import Glyph, Player, Position, Renderable, Viewshed
from core import ECS, Scene
from device import Device
from map import drawMap, Map
from player import playerInput
from system.visibility import visibilitySystem


def update():
    visibilitySystem()
    drawMap()

    width, height = ECS.scene.retrieve("pixels unit")
    entities = ECS.scene.filter(Position.id | Renderable.id)
    for entity in entities:
        position: Position = entity[Position.id]
        render: Renderable = entity[Renderable.id]
        render.glyph.draw(position.x * width, position.y * height)


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

    scene = Scene()
    scene.store("background", background)
    scene.store("font", font)
    scene.store("rand", rand)
    
    scene.store("map", map)
    scene.store("glyph wall", glyphWall)
    scene.store("glyph floor", glyphFloor)
    scene.store("pixels unit", (pixelsUnit, pixelsUnit))

    player = scene.create()
    player.add(Position(xplayer, yplayer))
    player.add(Renderable(Glyph(background, font, "@")))
    player.add(Player())
    player.add(Viewshed(8))

    device.onLoop.append(update)
    device.onPressed.append(playerInput)

    ECS.scene = scene

    while device.running:
        device.clear()
        device.loop()
        device.draw()


if __name__ == "__main__":
    main()
