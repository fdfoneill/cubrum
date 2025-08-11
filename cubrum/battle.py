import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import numpy as np

from .weather import Weather
from .exceptions import InvalidActionError, InvalidBattleError


class Battle:
    """Single engagement between Armies

    ***
    Attributes:
        isSiege:bool
        weather:Weather
        belligerents:list
    Methods:
        addBelligerent() -> None
        getStrengths() -> dict
        getModifiers() -> dict
        getResult() -> BattleResult
    """
    def __init__(self, weather:Weather, isSiege:bool=False):
        self.weather = weather 
        self.isSiege = isSiege 
        self.belligerents = []

    def addBelligerent(self, army, defending:bool=False, surprised:bool=False, outOfFormation:bool=False):
        if len(self.belligerents)>=2:
            raise InvalidActionError("a Battle can have at most two belligerents; consider combining Armies by side")
        new_belligerent = {"army":army, 'defending':defending, "surprised":surprised, "outOfFormation":outOfFormation}
        self.belligerents.append(new_belligerent)

    def validate(self):
        try:
            assert len(self.belligerents)==2, "Battle must have exactly 2 belligerents, got {}".format(len(self.belligerents))
            assert self.belligerents[0]['army'].allegience != self.belligerents[1]['army'].allegience, "belligerents cannot have the same allegience"
        except AssertionError as e:
            raise InvalidBattleError(e)

    def getStrengths(self) -> dict:
        strengths = {}
        for belligerent in self.belligerents:
            if self.isSiege:
                if belligerent['defending']:
                    setting = "SIEGEDEFEND"
                else:
                    setting = "SIEGEATTACK"
            else:
                setting="FIELD"
            strengths[belligerent['army'].allegience] = belligerent['army'].getStrength(setting=setting)
        return strengths
    
    def getModifiers(self) -> dict:
        self.validate()
        modifiers = {}
        strengths = self.getStrengths()
        for belligerent in self.belligerents:
            allegience = belligerent['army'].allegience
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
            morale_other = max([b['army'].morale for b in self.belligerents if b['army'].allegience!=allegience])
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
            modifiers[allegience] = {
                'value':int(np.array(values).sum()),
                'descriptions':descriptions
            }
        return modifiers


class BattleResult:
    """Results of a violent engagement
    
    ***

    Attributes:
        victoriousSide:str
        consequences:dict

    Methods:
        apply() -> None
    """