

from core import Component, Entity, Game, System


class PlayerComponent(Component['PlayerSystem']):
    def __init__(self, system:'PlayerSystem', entity:Entity):
        super().__init__(system, entity)
        self.enabled = True


class PlayerSystem(System['PlayerComponent']):
    def __init__(self, game:Game):
        super().__init__(game, set())
        self.enabled = True
