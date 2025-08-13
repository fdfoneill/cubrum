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
    def __init__(self, playerID:int, hours:int, actionName:str):
        self.playerID = playerID
        self.actionName = str(actionName)
        self.hours=int(hours)

    def apply(self, state:GameState):
        pass

    def isValid(self, state:GameState) -> bool:
        if self.playerID not in state.getPlayers(): # check player exists
            return False 
        if self.hours>0: # only active player can take actions with a nonzero time
            if not state.clock.getActivePlayer()==self.playerID:
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
    def __init__(self, playerID:int, hours:int=1):
        super().__init__(playerID=playerID, hours=hours, actionName="Proceed")

    def __repr__(self):
        return "player={} proceed in present course of action for {} hours".format(self.playerID, self.hours)

    def isValid(self, state):
        if not super().isValid(state):
            return False 
        army_geometries = state.getArmyGeometries()[state.playerToArmy[self.playerID]]
        if len(army_geometries['touching']) > 0:
            return False 
        if len(army_geometries['intersecting']) > 0:
            return False
        return True

        
    def apply(self, state) -> list:
        decision_points = []
        army = state.armies[state.playerToArmy[self.playerID]]
        if army.position.getMotion()!="holding":
            res_march = army.march(hours=self.hours)
            if res_march:
                res_march.updateContext(playerID=self.playerID)
                decision_points.append(res_march)
        res_clock = state.clock.incrementPlayerTime(self.playerID, self.hours)
        if res_clock:
            res_clock.updateContext(playerID=self.playerID)
            decision_points.append(res_clock)
        return decision_points
        


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