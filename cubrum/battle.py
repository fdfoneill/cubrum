import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import numpy as np

from .weather import Weather
from .exceptions import InvalidActionError, InvalidBattleError
from .decisionpoint import DecisionPoint, BattleResolved


class Battle:
    """Single engagement between Armies

    ***
    Attributes:
        isSiege:bool
        weather:Weather
        belligerents:dict
    Methods:
        addBelligerent() -> None
        getStrengths() -> dict
        getModifiers() -> dict
        generateResult() -> BattleResult
    """
    def __init__(self, weather:Weather, isSiege:bool=False, strongholdType:str=None):
        try:
            self.weather = weather 
            self.isSiege = isSiege 
            self.strongholdType=strongholdType
            if self.isSiege:
                assert self.strongholdType in ["city", "town", "fortress"], "sieges must specify stronghold type"
            self.belligerents = {}
        except AssertionError as e:
            raise InvalidBattleError(e)

    def addBelligerent(self, army, defending:bool=False, surprised:bool=False, outOfFormation:bool=False):
        if len(self.belligerents)>=2:
            raise InvalidActionError("a Battle can have at most two belligerents; consider combining Armies by side")
        new_belligerent = {"army":army, 'defending':defending, "surprised":surprised, "outOfFormation":outOfFormation}
        if army.allegience in self.belligerents.keys():
            raise InvalidBattleError("multiple belligerents cannot have the same allegience")
        self.belligerents[army.allegience] = new_belligerent

    def validate(self):
        try:
            assert len(self.belligerents)==2, "Battle must have exactly 2 belligerents, got {}".format(len(self.belligerents))
        except AssertionError as e:
            raise InvalidBattleError(e)

    def getStrengths(self) -> dict:
        strengths = {}
        for side, belligerent in self.belligerents.items():
            if self.isSiege:
                if belligerent['defending']:
                    setting = "SIEGEDEFEND"
                else:
                    setting = "SIEGEATTACK"
            else:
                setting="FIELD"
            strengths[side] = belligerent['army'].getStrength(setting=setting)
        return strengths
    
    def getModifiers(self) -> dict:
        self.validate()
        modifiers = {}
        strengths = self.getStrengths()
        for allegience, belligerent in self.belligerents.items():
            descriptions = []
            values = []
            # numerical advantage
            strength_self = strengths[allegience]
            strength_other = sum([strengths[a] for a in strengths.keys() if a!=allegience])
            strength_advantage = max(strength_self-strength_other, 0)
            if strength_advantage > 0:
                strength_modifier = strength_advantage//strength_other
                descriptions.append("numerical advantage: +{}".format(strength_modifier))
                values.append(strength_modifier)
            # morale advantage
            morale_self = belligerent['army'].morale
            morale_other = max([self.belligerents[s]['army'].morale for s in self.belligerents.keys() if s!=allegience])
            morale_advantage = max(morale_self-morale_other, 0)
            if morale_advantage > 0:
                morale_modifier = morale_advantage
                descriptions.append("morale advantage: +{}".format(morale_modifier))
                values.append(morale_modifier)
            # surprise 
            if belligerent['surprised']:
                descriptions.append("surprised: -1")
                values.append(-1)
            # out of formation 
            if belligerent['outOfFormation']:
                descriptions.append("out of formation: -2")
                values.append(-2)
            # undersupplied 
            if belligerent['army'].isSupplyLow():
                descriptions.append("supplies low: -1")
                values.append(-1)
            # siege attacker
            if self.isSiege and not belligerent.defending:
                descriptions.append("siege attacker: -1")
                values.append(-1)
            # siege defender
            if self.isSiege and belligerent.defending:
                siege_bonus = {"town":3,"city":4,"fortress":5}.get(self.strongholdType, 0)
                descriptions.append("siege defender ({}): +{}".format(self.strongholdType, siege_bonus))
                values.append(siege_bonus)
            modifiers[allegience] = {
                'value':int(np.array(values).sum()),
                'descriptions':descriptions
            }
        return modifiers
    
    def generateResult(self) -> "BattleResult":
        self.validate()
        modifiers = self.getModifiers()
        side1, side2 = list(modifiers.keys())
        rolls = {side:np.random.randing(1,7)+np.random.randint(1,7)+modifiers[side] for side in modifiers.key()}
        margin = abs(rolls[side1]-rolls[side2])
        consequences = {side1:{}, side2:{}}
        if rolls[side1]>rolls[side2]:
            victoriousSide=side1 
            defeatedSide=side2
        elif rolls[side2]>rolls[side1]:
            victoriousSide=side2
            defeatedSide=side1
        else: # equal rolls
            if self.belligerents[side1]['defending'] and not self.belligerents[side2]['defending']:
                victoriousSide=side1
                defeatedSide=side2
                consequences[side2]['moraleChange']=-1
            elif self.belligerents[side2]['defending'] and not self.belligerents[side1]['defending']:
                victoriousSide=side2
                defeatedSide=side1
                consequences[side1]['moraleChange']=-1
            else:
                victoriousSide=None
                defeatedSide=None
            consequences[side1]['casualtyPercent']=5
            consequences[side2]['casualtyPercent']=5
        if defeatedSide:
            consequences[defeatedSide]['retreatDistance']=1
            # check rout
            if self.belligerents[defeatedSide].checkMorale()>0:
                consequences[defeatedSide]['rout']=True
                consequences[defeatedSide]['retreatDistance']=2
                supplyLostPercent=int(np.random.randint(1,7)*10)
                consequences[defeatedSide]['supplyLostPercent'] = supplyLostPercent
            # table of consequences
            if margin==0: # already resolved above 
                pass
            elif margin <= 1:
                consequences[defeatedSide]['casualtyPercent']=10
                consequences[victoriousSide]['casualtyPercent']=10
                consequences[defeatedSide]['moraleChange']=-1
            elif margin <= 3:
                consequences[victoriousSide]['casualtyPercent']=5
                consequences[defeatedSide]['casualtyPercent']=10
                consequences[victoriousSide]['moraleChange']=1
                consequences[defeatedSide]['moraleChange']=-2
            elif margin <= 5:
                consequences[victoriousSide]['casualtyPercent']=5
                consequences[defeatedSide]['casualtyPercent']=15
                consequences[victoriousSide]['moraleChange']=2
                consequences[defeatedSide]['moraleChange']=-2
            else:
                consequences[victoriousSide]['casualtyPercent']=5
                consequences[defeatedSide]['casualtyPercent']=20
                consequences[victoriousSide]['moraleChange']=2
                consequences[defeatedSide]['moraleChange']=-2
        return BattleResult(victoriousSide=victoriousSide, consequences=consequences, belligerents=self.belligerents, isSiege=self.isSiege)


class BattleResult:
    """Results of a violent engagement
    
    ***

    Attributes:
        victoriousSide:str
        consequences:dict
        belligerents:dict

    Methods:
        apply() -> None
    """
    def __init__(self, victoriousSide:str, consequences:dict, belligerents:dict, isSiege:bool):
        self.victoriousSide=victoriousSide
        self.consequences = consequences 
        self.belligerents = belligerents 
        self.isSiege = isSiege
        self.rout=False
        for side, consequence_dict in self.consequences.items():
            self.rout = self.rout or consequence_dict.get("rout", False)
        self.validate()

    def __repr__(self):
        repr_string = "Battle("
        repr_string += " vs. ".join(v['army'].name for v in self.belligerents.values())
        if self.victoriousSide:
            repr_string+=("; {} victory")
        else:
            repr_string+=("; draw")
        if self.rout:
            repr_string+=("; losers routed")
        repr_string+=(")")
        return repr_string

    def validate(self):
        try:
            assert set(self.consequences.keys())==set(self.belligerents.keys()), "mismatch between belligerents and consequences"
            if self.victoriousSide is not None:
                assert self.victoriousSide in self.belligerents.keys(), "victor '{}' not in belligerents {}".format(self.victoriousSide, list(self.belligerents.keys()))
        except AssertionError as e:
            raise InvalidBattleError(e)

    def apply(self) -> DecisionPoint:
        for side, consequence_dict in self.consequences.items():
            # casualties 
            self.belligerents[side]['army'].applyCasualties(percent=consequence_dict.get("casualtyPercent", 0))
            # morale
            morale_change = consequence_dict.get("moraleChange", 0)
            if morale_change > 0:
                self.belligerents[side]['army'].raiseMorale(morale_change)
            elif morale_change < 0:
                self.belligerents[side]['army'].lowerMorale(-1*morale_change)
            # lost supply
            supplyLostPercent = consequence_dict.get("supplyLostPercent", 0)
            if supplyLostPercent > 0:
                supplyRemainingPercent = 100-supplyLostPercent
                self.belligerents[side]['army'].supply = int(self.belligerents[side]['army'].supply * (supplyRemainingPercent/100))

            # retreat
            retreat_distance = consequence_dict.get("retreatDistance", 0)
            if retreat_distance > 0:
                try:
                    enemy_army = [self.belligerents[enemy_side]['army'] for enemy_side in self.belligerents.keys() if enemy_side!=side][0]
                except IndexError:
                    raise InvalidBattleError("unable to find enemy army for side '{}' among belligerents".format(side))
                self.belligerents[side]['army'].retreat(distance=retreat_distance, awayFrom=enemy_army)
        return BattleResolved(belligerents=self.belligerents, victoriousSide=self.victoriousSide, rout=self.rout, consequences=self.consequences, isSiege=self.isSiege)