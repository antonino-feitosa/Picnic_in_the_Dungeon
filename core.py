from typing import TypeVar, Any
from algorithms import Point

class Component:
    __slots__ = "signature"

    def __init__(self, signature: int):
        self.signature = signature


class Context:
    def __init__(self):
        self.keys:set[str] = set()
        self.mousePosition:Point = Point()
        self.mouseLeftPressed = False
    
    def clear(self):
        self.keys.clear()
        self.mouseLeftPressed = False



class EntityComponentSystem:
    def __init__(self):
        self.signature: int = 1
        self.id: int = 0
        self.scene: Scene
        self.context: Context

    def nextSignature(self) -> int:
        current = self.signature
        self.signature = self.signature << 1
        return current

    def nextId(self) -> int:
        self.id += 1
        return self.id

    def run(self, scene:'Scene', context:Context) -> None:
        self.scene = scene
        self.context = context



ECS = EntityComponentSystem()


class Entity:
    def __init__(self):
        self.id: int = ECS.nextId()
        self.signature = 0
        self.components: dict[int, Component] = dict()

    def add(self, component: Component) -> "Entity":
        self.signature = component.signature | self.signature
        self.components[component.signature] = component
        return self

    def remove(self, signature: int):
        self.signature = self.signature & ~signature
        self.components.pop(signature)

    def has(self, signature: int) -> bool:
        return (self.signature & signature) > 0

    T = TypeVar("T", bound=Component)

    def get(self, signature: int) -> Any:
        return self.components[signature]

    def __getitem__(self, signature: int) -> Any:
        return self.get(signature)



class Scene:
    def __init__(self):
        self.entities: set[Entity] = set()
        self.memory: dict[str, Any] = dict()

    def create(self):
        entity = Entity()
        self.entities.add(entity)
        return entity

    def destroy(self, entity: Entity):
        self.entities.remove(entity)

    def filter(self, *signatures: int) -> set[Entity]:
        signature = 0
        for sign in signatures:
            signature = signature | sign
        return set(
            filter(lambda e: (e.signature & signature) == signature, self.entities)
        )

    def store(self, label: str, data):
        self.memory[label] = data

    def retrieve(self, label: str) -> Any:
        return self.memory[label]
