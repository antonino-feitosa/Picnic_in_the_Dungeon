from typing import TypeVar, Any


class Component:
    __slots__ = "signature"

    def __init__(self, signature: int):
        self.signature = signature


class EntityComponentSystem:
    def __init__(self):
        self.signature: int = 1
        self.id: int = 0
        self.scene: Scene

    def nextSignature(self):
        current = self.signature
        self.signature = self.signature << 1
        return current

    def nextId(self):
        self.id += 1
        return self.id

    def run(self, scene):
        self.scene = scene


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
        self.signature = signature & ~self.signature
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
