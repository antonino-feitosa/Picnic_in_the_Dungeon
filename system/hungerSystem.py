

from component import HungerClock, Player, sufferDamage
from core import ECS
from runState import RunState
from utils import Logger

HUNGER_DURATION = 200


def hungerSystem():
    logger: Logger = ECS.scene.retrieve("logger")
    runState: RunState = ECS.scene.retrieve("state")
    entities = ECS.scene.filter(HungerClock.id)
    for entity in entities:
        proceed = runState == RunState.PlayerTurn and entity.has(Player.id)
        proceed = proceed or (runState != RunState.PlayerTurn and not entity.has(Player.id))
        if proceed:
            hungerClock:HungerClock = entity[HungerClock.id]
            hungerClock.duration -= 1
            if hungerClock.duration <= 0:
                match hungerClock.hungerState:
                    case HungerClock.WELL_FED:
                        hungerClock.hungerState = HungerClock.NORMAL
                        hungerClock.duration = HUNGER_DURATION
                        if entity.has(Player.id):
                            logger.log(f"You are no longer well fed.")
                    case HungerClock.NORMAL:
                        hungerClock.hungerState = HungerClock.HUNGRY
                        hungerClock.duration = HUNGER_DURATION
                        if entity.has(Player.id):
                            logger.log(f"You are hungry.")
                    case HungerClock.HUNGRY:
                        hungerClock.hungerState = HungerClock.STARVING
                        hungerClock.duration = HUNGER_DURATION
                        if entity.has(Player.id):
                            logger.log(f"You are starving!")
                    case HungerClock.STARVING:
                        sufferDamage(entity, 1)
                        if entity.has(Player.id):
                            logger.log(f"Your hunger pangs are getting painful! You suffer 1 hp damage.")
        

