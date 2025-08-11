import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from .weather import Weather


class Battle:
    """Single engagement between Armies

    ***
    Attributes:
        isSiege:bool
        weather:Weather
    Methods:
        addBelligerent() -> None
        getResult() -> BattleResult
    """
    def __init__(self, weather:Weather, isSiege:bool=False):
        self.weather = weather 
        self.isSiege = isSiege 
        self.belligerents = []

    def addBelligerent(self, army, defending:bool=False, surprised:bool=False, inFormation:bool=True):
        new_belligerent = {"army":army, 'defending':defending, "surprised":surprised, "inFormation":inFormation}
        self.belligerents.append(new_belligerent)


class BattleResult:
    pass