
from enum import Enum

class RunState(Enum):
    MainMenu = 0
    WaitingInput = 1
    PlayerTurn = 2
    MonsterTurn = 3
    ShowInventory = 4
    ShowDropItem = 5
    ShowTargeting = 6
    NextLevel = 7
    GameOver = 8
    ShowRemoveItem = 9