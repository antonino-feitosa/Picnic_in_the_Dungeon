

from algorithms import Point
from component import ParticleLifetime, Position, Renderable
from core import ECS
from glyphScreen import GlyphScreen
from device import Font
from glyphScreen import GlyphScreen
from map import Map


def cullDeadParticles() -> None:
    entities = ECS.scene.filter(ParticleLifetime.id)
    for entity in entities:
        particle:ParticleLifetime = entity[ParticleLifetime.id]
        particle.frames -= 1
        if particle.frames <= 0:
            ECS.scene.destroy(entity)


def drawParticles(screen: GlyphScreen) -> None:
    map: Map = ECS.scene.retrieve("map")
    entities = ECS.scene.filter(Position.id | Renderable.id | ParticleLifetime.id)
    for entity in entities:
        position: Position = entity[Position.id]
        if Point(position.x, position.y) in map.visibleTiles:
            render: Renderable = entity[Renderable.id]
            screen.setGlyph(position.x, position.y, render.glyph, render.foreground, render.background)
