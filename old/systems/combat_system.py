
from typing import Callable

from algorithms import Direction
from core import Component, Entity, System


AttackModifier = Callable[['AttackComponent'],'AttackComponent']

class DefenseComponent(Component['AttackSystem']):
    def __init__(self):
        self.attackModifiers:list[AttackModifier] = []
        self.damage:list[AttackComponent] = []

    def applyDamage(self, attack:'AttackComponent') -> None:
        modified = attack
        for att in self.attackModifiers:
            modified = att(modified)
        self.damage.append(modified)

class AttackComponent:
    def __init__(self):
        self.radius = 0
        self.line:list[Direction] = []
        self.delay = 0
        self.damage = 0
        self.cast = 0
        self.recharge = 0
        self.duration = 0
        self.attackModifiers:list[AttackModifier] = []
    
    def applyEffect(self, entity:Entity) -> None:
        pass
    
    def clone(self) -> 'AttackComponent':
        return AttackComponent()

class AttackSystem(System[AttackComponent]):
    pass