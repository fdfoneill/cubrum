import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import numpy as np
from collections import Counter

from .map import Map
from .commander import Commander
from .formation import Formation
from .position import PointPosition, ColumnPosition
from .decisionpoint import DecisionPoint
from .exceptions import InvalidActionError

class Army:
    """Defines a force of formations led by a commander
    
    ***
    
    Attributes:
        name:str
        allegience:str
        commander:cubrum.commander.Commander
        formations:list
        morale:int
        supply:int
        noncombattantPercent:int
        position:cubrum.position.ColumnPosition
        isGarrison:bool
        
    Methods:
        getForces() -> dict
        countInfantry() -> int
        countCavalry() -> int
        getStrength() -> int
        getTravelDistance() -> float
        getLength() -> float
        getSupplyMax() -> int
        getSupplyConsumption() -> int
        isSupplyLow() -> bool
        getNoncombattantCount() -> int
        getValidDestinations() -> list[str]
        getDestination() -> str
        setDestination() -> None
        march() -> DecisionPoint
        getValidBypasses() -> list[str]
        applyCasualties() -> None
        raiseMorale() -> None
        lowerMorale() -> None 
        checkMorale() -> int
        toGarrison() -> dict
    """
    @staticmethod 
    def fromGarrison(garrison:dict, map:Map, stronghold:str, allegience:str=None) -> "Army":
        """Parse stronghold garrison to Army object"""
        name = garrison['name']
        infantryCount = garrison.get("infantryCount", 0)
        cavalryCount = garrison.get("cavalryCount", 0) 
        garrisonAllegience = allegience or ""
        garrisonCommander = Commander(name=name, age=30, title="commander of the", culture=None)
        garrisonFormations = []
        if infantryCount > 0:
            garrisonFormations.append(Formation("{} infantry".format(name),infantryCount,wagonCount=0,cavalry=False,heavy=False))
        if cavalryCount > 0:
            garrisonFormations.append(Formation("{} cavalry".format(name),cavalryCount,wagonCount=0,cavalry=True,heavy=False))
        garrisonArmy = Army(name, garrisonAllegience, garrisonFormations, garrisonCommander, supply=0, startingStronghold=stronghold, map=map, noncombattantPercent=0, isGarrison=True)
        return garrisonArmy


    def __init__(self, name:str, allegience:str, formations:list, commander:Commander, supply:int, startingStronghold:str, map:Map, morale:int=7, noncombattantPercent:int=25, isGarrison=False):
        self.name = str(name)
        self.allegience=allegience
        self.map = map
        self.commander = commander
        self.formations = list(formations)
        self.supply=int(supply)
        self.morale=int(morale)
        self.noncombattantPercent = int(noncombattantPercent)
        assert startingStronghold in self.map.nodes, "stronghold '{}' not found".format(startingStronghold)
        van_position = PointPosition(startingStronghold, map)
        rear_position = PointPosition(startingStronghold, map)
        self.position = ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=self.getLength())
        self.isGarrison=isGarrison
        
    def __repr__(self) -> str:
        repr_string = "Army("
        for unit_type, unit_count in self.getForces().items():
            repr_string += "{} {}, ".format(unit_count, unit_type)
        repr_string = repr_string[:-2]+")"
        return repr_string
        
    def getForces(self) -> dict:
        """Return dictionary counting each type of troop within army"""
        forces = Counter()
        for formation in self.formations:
            forces[formation.getDescription()] += formation.warriorCount
            forces["wagons"] += formation.wagonCount
        return dict(forces)
    
    def countInfantry(self) -> int:
        count_infantry = 0
        for formation in self.formations:
            if not formation.cavalry:
                count_infantry += formation.warriorCount 
        return count_infantry

    def countCavalry(self) -> int:
        count_cavalry = 0
        for formation in self.formations:
            if formation.cavalry:
                count_cavalry += formation.warriorCount
        return count_cavalry
    
    def getStrength(self, setting:str="FIELD") -> int:
        """Calculate effective strength of this army in a given setting"""
        assert setting in ["FIELD", "SIEGEATTACK", "SIEGEDEFEND"], "'setting' must be one of FIELD, SIEGEATTACK, or SIEGEDEFEND, got '{}'".format(setting)
        strength_total = 0
        for formation in self.formations:
            strength_total += formation.getStrength(setting=setting)
        return strength_total
    
    def getTravelDistance(self, hours:int, forced:bool=False) -> float:
        """Returns the travel diatance for the slowest formation in the army over a number of hours"""
        leagues = -1
        for formation in self.formations:
            formation_leagues = formation.getTravelDistance(hours, forced)
            if leagues==-1:
                leagues=formation_leagues
            elif formation_leagues < leagues:
                leagues = formation_leagues
        if self.getLength()>2: # armies longer than 2 leagues move slower
            if forced:
                slow_speed = 12/18
            else:
                slow_speed = 6/18
            if (slow_speed*hours)<leagues:
                leagues = (slow_speed*hours)
        return round(leagues, 2)
    
    def getLength(self) -> float:
        """Calculate length in leagues of the army on the march"""
        length_warriors = 0
        for formation in self.formations:
            length_warriors += formation.getLength()
        length_noncombattants = (self.getNoncombattantCount()/5000)/3
        army_length = length_warriors + length_noncombattants
        return round(army_length, 2)
    
    def getSupplyMax(self) -> int:
        """Calculate maximum quantity of supply the army can carry"""
        capacity_warriors = 0
        for formation in self.formations:
            capacity_warriors += formation.getSupplyMax()
        capacity_noncombattants = self.getNoncombattantCount() * 15
        return capacity_warriors + capacity_noncombattants
        
    def getSupplyConsumption(self, days:int=1) -> int:
        total_consumption = 0
        for formation in self.formations:
            total_consumption += formation.getSupplyConsumption(days=days)
        return total_consumption
    
    def isSupplyLow(self, days_threshold:int=1) -> bool:
        """Returns True if the army has less than 1 day of supply"""
        current_supply = self.supply 
        days_supply = self.getSupplyConsumption(days=days_threshold)
        if days_supply >= current_supply:
            return True 
        else:
            return False
        
    def getNoncombattantCount(self) -> int:
        """Calculate current number of noncombattants attached to the army"""
        count_warriors = 0
        for formation in self.formations:
            count_warriors += formation.warriorCount
        count_noncombattants = int(count_warriors * (self.noncombattantPercent/100))
        return count_noncombattants
    
    def getValidDestinations(self) -> list[str]:
        return self.position.getValidOrientations()
    
    def getDestination(self) -> str:
        return self.position.getOrientation()
    
    def setDestination(self, new_destination) -> None:
        try:
            assert new_destination in self.getValidDestinations()
            self.position.setOrientation(new_destination)
        except Exception as e:
            raise InvalidActionError(e)
    
    def march(self, hours:int=None, distance:float=None, forced:bool=False, destination:str=None, gather_at_gates:bool=False) -> DecisionPoint:
        """March army for a set number of hours or leagues
        
        ***
        
        Parameters:
            hours: default None. How long to march. Exactly one of hours or 
                leagues must be set
            distance: default None. How far to march, in leagues. Exactly one 
                of hours or leagues must be set
            forced: default False. Whether this is a forced march
            destination: default None. If provided, the army's destination is 
                updated to the value of destination
            gather_at_gates: default False. Whether to gather forces outside 
                a stronghold rather than entering it.
        """
        assert (hours is None) ^ (distance is None), "exactly one of hours or leagues must be set"
        try:
            if destination is not None:
                if destination in self.getValidDestinations():
                    self.setDestination(destination)
                elif destination in self.getValidBypasses():
                    self.bypassTo(destination)
                else:
                    raise InvalidActionError("'{}' is not a valid destination for this march".format(destination))
            leagues = distance or self.getTravelDistance(hours=hours, forced=forced)
            return self.position.move(leagues, gather_at_gates=gather_at_gates)
        except AssertionError as e:
            raise InvalidActionError(e)
            
    def getValidBypasses(self) -> list:
        return self.position.getValidBypasses()
    
    def bypassTo(self, bypass_name) -> None:
        self.position.bypassTo(bypass_name)
    
    def applyCasualties(self, count:int=None, percent:int=None) -> None:
        try:
            assert (count is None) ^ (percent is None), "exactly one of count or percent must be set"
            if count is None:
                count = int((self.countInfantry()+self.countCavalry())*(percent/100))
            weights = []
            for formation in self.formations:
                # TODO: more sophisticated weighting
                weights.append(formation.warriorCount)
            indices = np.random.choice(len(weights), size=count, p = np.array(weights)/sum(weights))
            counts_by_formation = np.bincount(indices, minlength=len(weights))
            for i in range(len(self.formations)):
                self.formations[i].applyCasualties(count=counts_by_formation[i])
        except AssertionError as e:
            raise ValueError(e)
        
    def raiseMorale(self, amount:int=1):
        self.morale = min(self.morale+amount, 12)

    def lowerMorale(self, amount:int=1):
        self.morale = max(self.morale-amount, 0)
        
    def checkMorale(self) -> int:
        """Returns 0 on a success, else roll result"""
        die_result = np.random.randint(1,7)+np.random.randint(1,7)
        if die_result <= self.morale:
            return 0
        else:
            return die_result
        
    def toGarrison(self):
        if not self.isGarrison:
            raise ValueError("cannot convert to garrison when isGarrison is False")
        g = {}
        g['name'] = self.name
        g['infantryCount'] = self.countInfantry()
        g['cavalryCount'] = self.countCavalry()
        return g