import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime

from .gamestate import GameState
from .exceptions import InvalidActionError


class PlayerAction:
    """Class representing an action taken by a player

    ***

    Attributes:
        player: relevant player 
        actionName: name of chosen action 
        startDate: date action was taken
    """
    def __init__(self, playerID:int, actionName:str):
        self.id = playerID
        self.actionName = str(actionName)

    def apply(self, state:GameState):
        pass

    def isValid(self, state:GameState) -> bool:
        if self.id not in state.getPlayers():
            return False 
        return True


class AbandonStronghold(PlayerAction):
    pass


class AssaultStronghold(PlayerAction):
    pass


class BesiegeStronghold(PlayerAction):
    pass


class ChallengeCommander(PlayerAction):
    pass


class ChangeDestination(PlayerAction):
    pass


class ConstructSiegeEngines(PlayerAction):
    pass


class DeconstructSiegeEngines(PlayerAction):
    pass


class FleeBattle(PlayerAction):
    pass


class Forage(PlayerAction):
    pass


class GiveBattle(PlayerAction):
    pass


class HoldPosition(PlayerAction):
    pass


class HonorFormation(PlayerAction):
    pass


class LevyTroops(PlayerAction):
    pass


class MakeCamp(PlayerAction):
    pass


class OccupyStronghold(PlayerAction):
    pass


class PillageStronghold(PlayerAction):
    pass


class Proceed(PlayerAction):
    pass


class ReconstructSiegeEngines(PlayerAction):
    pass


class RestArmy(PlayerAction):
    pass


class SendLetter(PlayerAction):
    pass


class SplitArmy(PlayerAction):
    pass


class TaxStronghold(PlayerAction):
    pass


class TorchPosition(PlayerAction):
    pass