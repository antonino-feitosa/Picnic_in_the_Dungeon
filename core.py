from typing import Any, List, Type, Dict, TypeVar
from algorithms import Dimension, Random

from device import Device, Image, SpriteSheet



class Entity:
    countId = 0

    def __init__(self):
        Entity.countId += 1
        self.id = Entity.countId
        self.typeToComponent: Dict[Type, Any] = dict()
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            for comp in self.typeToComponent.values():
                comp.enabled = True
            self._enabled = True
        if not value and self._enabled:
            for comp in self.typeToComponent.values():
                comp.enabled = False
            self._enabled = False

    def add(self, component) -> "Entity":
        self.typeToComponent[type(component)] = component
        return self

    T = TypeVar("T")

    def __getitem__(self, typeOfComponent: Type[T]) -> T:
        return self.typeToComponent[typeOfComponent]

    def __contains__(self, typeOfComponent: Type) -> bool:
        return typeOfComponent in self.typeToComponent

    def __delitem__(self, typeOfComponent: Type) -> None:
        self.typeToComponent.pop(typeOfComponent, None)

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if other.__class__ is self.__class__:
            return self.id != other.id
        return NotImplemented

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return f"Entity({self.id})"


class Game(Entity):
    def __init__(self, device:'Device', random:Random):
        super().__init__()
        self.rand = random
        self.device = device
        self.tickSystems = []
        self.drawSystems = []
        self.updateSystems = []
        self._loadedImages:Dict[str,Image] = dict()
        self._loadedSpriteSheets:Dict[str,SpriteSheet] = dict()

        self.loadTiledCanvas = device.loadTiledCanvas
        self.loadFont = device.loadFont
        self.loadSound = device.loadSound
        self.loadMusic = device.loadMusic
    
    def tick(self) -> None:
        active = filter(lambda system: system.enabled, self.tickSystems)
        for system in active:
            system.tick()

    def draw(self) -> None:
        self.device.clear()
        active = filter(lambda system: system.enabled, self.drawSystems)
        for system in active:
            system.draw()
        self.device.draw()

    def update(self) -> None:
        active = filter(lambda system: system.enabled, self.updateSystems)
        for system in active:
            system.update()

    def loadImage(self, path:str) -> Image:
        if path not in self._loadedImages:
            image = self.device.loadImage(path)
            self._loadedImages[path] = image
        return self._loadedImages[path]

    def loadSpriteSheet(self, path:str, dimension:Dimension) -> SpriteSheet:
        if path not in self._loadedImages:
            sheet = self.device.loadSpriteSheet(path, dimension)
            self._loadedSpriteSheets[path] = sheet
        return self._loadedSpriteSheets[path]

    @property
    def isRunning(self) -> bool:
        return self.device.running
    
    def loop(self) -> None:
        self.tick()
        self.device.loop()
        self.draw()
