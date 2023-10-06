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
            for elements in self.typeToComponent.values():
                for component in elements:
                    component.enabled = True
            self._enabled = True
        if not value and self._enabled:
            for elements in self.typeToComponent.values():
                for component in elements:
                    component.enabled = False
            self._enabled = False

    def add(self, component) -> "Entity":
        key = type(component)
        if key not in self.typeToComponent:
            self.typeToComponent[key] = []
        self.typeToComponent[key].append(component)
        return self
    
    T = TypeVar("T")

    def getAll(self, typeOfComponent: Type[T]) -> List[T]:
        return self.typeToComponent[typeOfComponent]

    def __getitem__(self, typeOfComponent: Type[T]) -> T:
        return self.typeToComponent[typeOfComponent][0]

    def __contains__(self, typeOfComponent: Type) -> bool:
        return typeOfComponent in self.typeToComponent

    def __delitem__(self, typeOfComponent: Type) -> None:
        removed = self.typeToComponent.pop(typeOfComponent, [])
        for component in removed:
            component.enabled =  False
        

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
    def __init__(self, gameLoop:'GameLoop', random: Random):
        super().__init__()
        self.gameLoop: 'GameLoop' = gameLoop
        self.rand = random
        self.device = gameLoop.device
        self.tickSystems = []
        self.drawSystems = []
        self.updateSystems = []
        self._loadedImages: Dict[str, Image] = dict()
        self._loadedSpriteSheets: Dict[str, SpriteSheet] = dict()

        self.loadTiledCanvas = self.device.loadTiledCanvas

        pathFonts = "_resources/_fonts/"
        pathSounds = "_resources/_sounds/"
        pathMusics = "_resources/_musics/"

        self.loadFont = lambda path, size: self.device.loadFont(pathFonts + path, size)
        self.loadSound = lambda path: self.device.loadSound(pathSounds + path)
        self.loadMusic = lambda path, f: self.device.loadMusic(pathMusics + path, f)

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

    def loadImage(self, path: str) -> Image:
        path = "_resources/_images/" + path
        if path not in self._loadedImages:
            image = self.device.loadImage(path)
            self._loadedImages[path] = image
        return self._loadedImages[path]

    def loadSpriteSheet(self, path: str, dimension: Dimension) -> SpriteSheet:
        path = "_resources/_sheets/" + path
        if path not in self._loadedImages:
            sheet = self.device.loadSpriteSheet(path, dimension)
            self._loadedSpriteSheets[path] = sheet
        return self._loadedSpriteSheets[path]

    @property
    def isRunning(self) -> bool:
        return self.device.running

    def exit(self) -> None:
        self.device.running = False

    def setActive(self):
        self.gameLoop.game = self



class GameLoop:
    def __init__(self, device:Device):
        self.device = device
        self.game: Game
    
    def forever(self, game:Game):
        self.game = game
        while self.game.isRunning:
            game = self.game
            game.tick()
            self.device.loop()
            game.draw()
