
from core import Game


class TurnComponent:
    def __init__(self, system:'TurnSystem', team:int):
        self.team = team
        self.system = system
        self._enabled = True
        self.system.teams[self.team].add(self)
    
    def processTurn(self, turn:int):
        pass
    
    def endOfTurn(self):
        self.system._count += 1
    
    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value and not self._enabled:
            self.system.teams[self.team].add(self)
            self._enabled = True
        if not value and self._enabled:
            self.system.teams[self.team].remove(self)
            self._enabled = False

class TurnSystem:
    def __init__(self, game:Game, numOfteams = 2):
        self.numOfTeams = numOfteams
        self.numOfTurns = 0
        self.teams:list[set[TurnComponent]] = []
        self.enabled = True
        self.game = game
        self.game.updateSystems.append(self)
        self._count = 0
        self._expectedCount = 0
        self._nextTurn = 0
        for _ in range(numOfteams):
            self.teams.append(set())
    
    def update(self):
        if self._count >= self._expectedCount:
            self._count = 0
            self._expectedCount = len(self.teams[self._nextTurn])
            for component in self.teams[self._nextTurn]:
                component.processTurn(self.numOfTurns)
            self._nextTurn = (self._nextTurn + 1) % len(self.teams)
            if self._nextTurn == 0:
                self.numOfTurns += 1
