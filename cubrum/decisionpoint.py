import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)


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
            repstring.append("{}={}, ".format(k, v))
        return repstring[:-2]+")"
    
    def updateContext(self, **kwargs) -> None:
        self.context.update(kwargs)


class ArmySighted(DecisionPoint):
    pass


class BattleResolved(DecisionPoint):
    pass


class LetterRecieved(DecisionPoint):
    pass


class CrossroadsReached(DecisionPoint):
    def __init__(self, crossroadsName:str, **kwargs):
        super().__init__(trigger="CrossroadsReached", crossroadsName=crossroadsName, **kwargs)



class RumorRecieved(DecisionPoint):
    pass
    

class StrongholdConquered(DecisionPoint):
    pass


class StrongholdReached(DecisionPoint):
    def __init__(self, strongholdName:str, heldBy:str, **kwargs):
        super().__init__(trigger="StrongholdReached", strongholdName=strongholdName, heldBy=heldBy, **kwargs)


class StrongholdSighted(DecisionPoint):
    pass


class SuppliesExpended(DecisionPoint):
    pass 


class SuppliesLow(DecisionPoint):
    pass