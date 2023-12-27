

from algorithms import Point
from component import ParticleLifetime, Position, Renderable
from core import ECS
from screen import Screen, ScreenLayer
from map import Map


def cullDeadParticles() -> None:
    entities = ECS.scene.filter(ParticleLifetime.id)
    for entity in entities:
        particle:ParticleLifetime = entity[ParticleLifetime.id]
        particle.frames -= 1
        if particle.frames <= 0:
            ECS.scene.destroy(entity)


def drawParticles(screen: Screen) -> None:
    map: Map = ECS.scene.retrieve("map")
    entities = ECS.scene.filter(Position.id | Renderable.id | ParticleLifetime.id)
    for entity in entities:
        position: Position = entity[Position.id]
        if Point(position.x, position.y) in map.visibleTiles:
            render: Renderable = entity[Renderable.id]
            screen.setGlyph(ScreenLayer.ForegroundEffects, Point(position.x, position.y), render)
