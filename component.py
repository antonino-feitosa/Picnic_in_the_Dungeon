
from algorithms import Point
from core import ECS, Component, Entity
from device import Color, Font, Image


class Position(Component):
    id = ECS.nextSignature()
    __slots__ = "x", "y"

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(Position.id)
        self.x = x
        self.y = y

    def __hash__(self) -> int:  # grid (-4096, -4096) x (4096, 4096)
        return 4096 * (4096 + self.y) + (4096 + self.x)

    def __eq__(self, other: "Position"):
        return other is not None and self.x == other.x and self.y == other.y


class Renderable(Component):
    id = ECS.nextSignature()
    __slots__ = ["render_order", "glyph", "foreground", "background"]

    def __init__(self, glyph: str, render_order: int = 0, foreground: Color = (255, 255, 255, 255)):
        super().__init__(Renderable.id)
        self.glyph: str = glyph
        self.render_order: int = render_order
        self.foreground: Color = foreground
        self.background: Color = (0, 0, 0, 255)


class Player(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(Player.id)


class Viewshed(Component):
    id = ECS.nextSignature()
    __slots__ = ["range", "visibleTiles", "dirty"]

    def __init__(self, range: int):
        super().__init__(Viewshed.id)
        self.dirty = True
        self.range = range
        self.visibleTiles: set[Point] = set()


class Monster(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(Monster.id)


class Name(Component):
    id = ECS.nextSignature()
    __slots__ = 'name'

    def __init__(self, name: str):
        super().__init__(Name.id)
        self.name = name


class BlocksTile(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(BlocksTile.id)


class CombatStats(Component):
    id = ECS.nextSignature()
    __slots__ = ["maxHP", "HP", "defense", "power"]

    def __init__(self, maxHP: int, defense: int, power: int):
        super().__init__(CombatStats.id)
        self.maxHP = maxHP
        self.HP = maxHP
        self.defense = defense
        self.power = power


class WantsToMelee(Component):
    id = ECS.nextSignature()
    __slots__ = ["target"]

    def __init__(self, target: Entity):
        super().__init__(WantsToMelee.id)
        self.target = target


class SufferDamage(Component):
    id = ECS.nextSignature()
    __slots__ = ["amount"]

    def __init__(self, amount: int):
        super().__init__(SufferDamage.id)
        self.amount = amount


class GUIDescription(Component):
    id = ECS.nextSignature()
    __slots__ = ["description"]

    def __init__(self, description: str = ""):
        super().__init__(GUIDescription.id)
        self.description = description


class Item(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(Item.id)


class ProvidesHealing(Component):
    id = ECS.nextSignature()
    __slots__ = 'heal_amount'

    def __init__(self, amount: int):
        super().__init__(ProvidesHealing.id)
        self.heal_amount = amount


class InBackpack(Component):
    id = ECS.nextSignature()
    __slots__ = 'owner'

    def __init__(self, owner: Entity):
        super().__init__(InBackpack.id)
        self.owner = owner


class WantsToPickupItem(Component):
    id = ECS.nextSignature()
    __slots__ = ['collectedBy', 'item']

    def __init__(self, collectedBy: Entity, item: Entity):
        super().__init__(WantsToPickupItem.id)
        self.collectedBy = collectedBy
        self.item = item


class WantsToUseItem(Component):
    id = ECS.nextSignature()
    __slots__ = ['item', 'target']

    def __init__(self, potion: Entity, target:Point|None = None):
        super().__init__(WantsToUseItem.id)
        self.item = potion
        self.target = target


class WantsToDropItem(Component):
    id = ECS.nextSignature()
    __slots__ = ['item']

    def __init__(self, item: Entity):
        super().__init__(WantsToDropItem.id)
        self.item = item


class Consumable(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(Consumable.id)


class Ranged(Component):
    id = ECS.nextSignature()
    __slots__ = ['range']

    def __init__(self, range: int):
        super().__init__(Ranged.id)
        self.range = range


class InflictsDamage (Component):
    id = ECS.nextSignature()
    __slots__ = ['damage']

    def __init__(self, damage: int):
        super().__init__(InflictsDamage .id)
        self.damage = damage


class AreaOfEffect(Component):
    id = ECS.nextSignature()
    __slots__ = ['radius']

    def __init__(self, radius: int):
        super().__init__(AreaOfEffect.id)
        self.radius = radius

class Confusion(Component):
    id = ECS.nextSignature()
    __slots__ = ['turns']

    def __init__(self, turns: int):
        super().__init__(Confusion.id)
        self.turns = turns


class Equippable(Component):
    id = ECS.nextSignature()
    MELEE = "weapon"
    SHIELD = "shield"
    __slots__ = ['slot']
    
    def __init__(self, slot: str):
        super().__init__(Equippable.id)
        self.slot = slot


class Equipped(Component):
    id = ECS.nextSignature()
    __slots__ = ['owner', 'slot']

    def __init__(self, owner: Entity, slot:str):
        super().__init__(Equipped.id)
        self.owner = owner
        self.slot:str = slot


class MeleePowerBonus(Component):
    id = ECS.nextSignature()
    __slots__ = ['power']

    def __init__(self, power: int):
        super().__init__(MeleePowerBonus.id)
        self.power = power


class DefenseBonus(Component):
    id = ECS.nextSignature()
    __slots__ = ['defense']

    def __init__(self, defense: int):
        super().__init__(DefenseBonus.id)
        self.defense = defense


class WantsToRemoveItem(Component):
    id = ECS.nextSignature()
    __slots__ = ['item']

    def __init__(self, item: Entity):
        super().__init__(WantsToRemoveItem.id)
        self.item = item


class ParticleLifetime(Component):
    id = ECS.nextSignature()
    __slots__ = ['frames']

    def __init__(self, frames: int):
        super().__init__(ParticleLifetime.id)
        self.frames = frames


class HungerClock(Component):
    id = ECS.nextSignature()
    WELL_FED = "well fed"
    NORMAL = "normal"
    HUNGRY = "hungry"
    STARVING = "starving"
    __slots__ = ["hungerState", "duration"]

    def __init__(self, hungerState: str, duration:int):
        super().__init__(HungerClock.id)
        self.hungerState:str = hungerState
        self.duration:int = duration


class ProvidesFood(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(ProvidesFood.id)


class MagicMapper(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(MagicMapper.id)


class Hidden(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(Hidden.id)


class EntryTrigger(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(EntryTrigger.id)


class EntityMoved(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(EntityMoved.id)


class SingleActivation(Component):
    id = ECS.nextSignature()

    def __init__(self):
        super().__init__(SingleActivation.id)


def sufferDamage(victim: Entity, amount: int):
    if victim.has(SufferDamage.id):
        sufferDamage: SufferDamage = victim[SufferDamage.id]
        sufferDamage.amount += amount
    else:
        victim.add(SufferDamage(amount))

