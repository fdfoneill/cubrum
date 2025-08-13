import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime


class DecisionPoint:
    """Signals need for player input

    ***

    Attributes:
        trigger:str

    Methods:
        updateContext() -> None
    """
    def __init__(self, trigger:str, **kwargs):
        self.trigger = str(trigger)
        self.context = {**kwargs}
        self.context['trigger'] = self.trigger

    def __getattr__(self, name):
        return self.context.get(name, None)
    
    def __repr__(self):
        repstring = "{}(".format(self.trigger)
        for k, v in self.context.items():
            repstring += "{}={}, ".format(k, v)
        return repstring[:-2]+")"
    
    def updateContext(self, **kwargs) -> None:
        self.context.update(kwargs)


class ArmyGathered(DecisionPoint):
    def __init__(self, strongholdName:str, roadFrom:str, heldBy:str, **kwargs):
        kwargs['strongholdName'] = strongholdName
        kwargs['heldBy'] = heldBy
        kwargs['roadFrom'] = roadFrom
        super().__init__(trigger="ArmyGathered", **kwargs)


class ArmySighted(DecisionPoint):
    pass


class ArmyEngaged(DecisionPoint):
    pass


class BattleResolved(DecisionPoint):
    def __init__(self, belligerents:dict, **kwargs):
        kwargs['belligerents'] = belligerents
        super().__init__(trigger="BattleResolved", **kwargs)


class CrossroadsReached(DecisionPoint):
    def __init__(self, crossroadsName:str, **kwargs):
        kwargs['crossroadsName']= crossroadsName
        super().__init__(trigger="CrossroadsReached", **kwargs)
        

class DayBreaks(DecisionPoint):
    def __init__(self, date:datetime.datetime, playerID:int, **kwargs):
        super().__init__(trigger="DayBreaks", date=date, playerID=playerID, **kwargs)



class LetterRecieved(DecisionPoint):
    pass


class NightFalls(DecisionPoint):
    def __init__(self, date:datetime.datetime, playerID:int, **kwargs):
        super().__init__(trigger="NightFalls", date=date, playerID=playerID, **kwargs)


class NodeOccupied(DecisionPoint):
    def __init__(self, nodeName:str, **kwargs):
        kwargs['nodeName'] = nodeName
        kwargs['nodeType'] = kwargs.get("strongholdType", "crossroads")
        super().__init__(trigger="NodeOccupied", **kwargs)


class RumorRecieved(DecisionPoint):
    pass
    

class StrongholdConquered(DecisionPoint):
    pass


class StrongholdReached(DecisionPoint):
    def __init__(self, strongholdName:str, heldBy:str, **kwargs):
        kwargs['strongholdName'] = strongholdName
        kwargs['heldBy'] = heldBy
        super().__init__(trigger="StrongholdReached", **kwargs)


class StrongholdSighted(DecisionPoint):
    pass


class SuppliesExpended(DecisionPoint):
    pass 


class SuppliesLow(DecisionPoint):
    pass