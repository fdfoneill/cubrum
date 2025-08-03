#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 14:32:05 2025

@author: DanO
"""

import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from collections import Counter

from .position import Position
from .commander import Commander

class Army:
    """Defines a force of formations led by a commander
    
    ***
    
    Attributes:
        name:str
        commander:cubrum.commander.Commander
        formations:list
        morale:int
        supply:int
        noncombattantPercent:int
        position:cubrum.position.Position
        
    Methods:
        getForces() -> dict
        getStrength() -> int
        getTravelTime() -> int
        getLength() -> float
        getSupplyMax() -> int
        getSupplyConsumption() -> int
        getNoncombattantCount() -> int
        applyCasualties() -> None
        
    """
    def __init__(self, name:str, formations:list, commander:Commander, supply:int, position:Position, morale:int=7, noncombattantPercent:int=25):
        self.name = str(name)
        self.commander = commander
        self.formations = list(formations)
        self.supply=int(supply)
        self.position=position
        self.morale=int(morale)
        self.noncombattantPercent = int(noncombattantPercent)
        
    def getForces(self) -> dict:
        """Return dictionary counting each type of troop within army"""
        forces = Counter()
        for formation in self.formations:
            forces[formation.getDescription()] += formation.warriorCount
            forces["wagons"] += formation.wagonCount
        return dict(forces)
    
    def getStrength(self, setting:str="FIELD") -> int:
        """Calculate effective strength of this army in a given setting"""
        assert setting in ["FIELD", "SEIGEATTACK", "SIEGEDEFEND"], "'setting' must be one of FIELD, SIEGEATTACK, or SIEGEDEFEND, got '{}'".format(setting)
        strength_total = 0
        for formation in self.formations:
            strength_total += formation.getStrength(setting=setting)
        return strength_total
    
    def getTravelTime(self, edge) -> int:
        """Returns the travel time for the slowest formation in the army along this edge"""
        hours = 0
        for formation in self.formations:
            formation_hours = formation.getTravelTime(edge)
            if formation_hours > hours:
                hours = formation_hours 
        return hours
    
    def getLength(self) -> float:
        """Calculate length in leagues of the army on the march"""
        length_warriors = 0
        for formation in self.formations:
            length_warriors += formation.getLength()
        length_noncombattants = (self.getNoncombattantCount()/5000)/3
        army_length = length_warriors + length_noncombattants
        return army_length
    
    def getSupplyMax(self) -> int:
        """Calculate maximum quantity of supply the army can carry"""
        capacity_warriors = 0
        for formation in self.formations:
            capacity_warriors += formation.getSupplyMax()
        capacity_noncombattants = self.getNoncombattantCount() * 15
        return capacity_warriors + capacity_noncombattants
        
    def getSupplyConsumption(self, period="DAY") -> int:
        assert period in ["DAY", "WEEK"], "'period' must be one of DAY or WEEK, got '{}'".format(period)
        
    def getNoncombattantCount(self) -> int:
        """Calculate current number of noncombattants attached to the army"""
        count_warriors = 0
        for formation in self.formations:
            count_warriors += formation.warriorCount
        count_noncombattants = int(count_warriors * (self.noncombattantPercent/100))
        return count_noncombattants
    
    def applyCasualties(self, count:int=None, percent:int=None) -> None:
        raise NotImplementedError("cubrum.army.Army.applyCasualties not implemented")