
from typing import Callable

from core import Game
from core import Entity

from device import SpriteSheet

from systems import ViewSystem
from systems import WorldRenderComponent


class AnimationControllerComponent:
    def __init__(self, entity: Entity):
        self.entity = entity
        self.animations: dict[str, SpriteSheet] = dict()
        self._shooting = False
        self._enabled = True
        self._idleAnimation: SpriteSheet

    def playAnimation(self, name: str) -> None:
        if name in self.animations:
            sheet = self.animations[name]
            animationComponent = self.entity[AnimationComponent]
            self._idleAnimation = animationComponent.animation
            animationComponent.animation = sheet
        else:
            raise ValueError("There is no animation " + name)

    def shootAnimation(self, name: str) -> None:
        if name in self.animations:
            animationComponent = self.entity[AnimationComponent]
            if not self._shooting:
                self._shooting = True
                self._idleAnimation = animationComponent.animation
            sheet = self.animations[name]
            animationComponent.animation = sheet
            animationComponent.reload()
            animationComponent.callback.add(self._restoreIdleAnimation)
        else:
            raise ValueError("There is no animation " + name)

    def _restoreIdleAnimation(self):
        self._shooting = False
        animationComponent = self.entity[AnimationComponent]
        animationComponent.animation = self._idleAnimation
        animationComponent.callback.remove(self._restoreIdleAnimation)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self._enabled = True
        if not value and self._enabled:
            self._restoreIdleAnimation()
            self._enabled = False
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return self.entity.__str__()


class AnimationComponent:
    def __init__(self, system: "AnimationSystem", entity: Entity, sheet: SpriteSheet):
        self.tickWait = 4
        self.loop = True
        self._tickCount = 0
        self._frameIndex = 0
        self.system = system
        self.animation = sheet
        self.entity = entity
        self._enabled = True
        self.system.components.add(self)
        self.callback: set[Callable[[], None]] = set()

    @property
    def finished(self):
        return not self.loop and self._frameIndex == len(self.animation.images) - 1

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self.system.components.add(self)
            self._enabled = True
        if not value and self._enabled:
            self.system.components.remove(self)
            self._enabled = False

    def reload(self):
        self._tickCount = 0
        self._frameIndex = 0

    def tick(self):
        if self._tickCount >= self.tickWait:
            self._tickCount = 0
            nextFrame = self.animation.images[self._frameIndex]
            self.entity[WorldRenderComponent].image = nextFrame
            length = len(self.animation.images)
            if self._frameIndex + 1 < length:
                self._frameIndex += 1
            else:
                for call in self.callback.copy():
                    call()
                if self.loop:
                    self._frameIndex = 0
        else:
            self._tickCount += 1
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return self.entity.__str__()


class AnimationSystem:
    def __init__(self, game: Game):
        self.game = game
        self.components: set[AnimationComponent] = set()
        self.enabled = True
        game.tickSystems.append(self)

    def tick(self):
        view = self.game[ViewSystem]
        for component in self.components:
            if view.isVisible(component):
                component.tick()
