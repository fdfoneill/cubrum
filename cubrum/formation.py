#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 14:32:42 2025

@author: DanO
"""

import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

class Formation:
    """An indivisible military unit
    
    ***
    
    Attributes:
        name:str
        warriorCount:int
        cavalry:bool
        heavy:bool
        
    Methods:
        getDescription() -> str
        getStrength() -> int
        getTravelTime() -> int
        getLength() -> float
        getSupplyCapacity() -> int
        getSupplyConsumption() -> int
        
    """
    def __init__(self, name:str, warriorCount:int, wagonCount:int, cavalry:bool=False, heavy:bool=False):
        self.name = name
        self.warriorCount = int(warriorCount)
        self.wagonCount = int(wagonCount)
        self.cavalry=bool(cavalry)
        self.heavy=bool(heavy)
        
    def getDescription(self) -> str:
        """Nicely format unit type (e.g. 'heavy infantry') as a string"""
        weight = "heavy" if self.heavy else "light"
        infantry_or_cavalry = "cavalry" if self.cavalry else "infantry"
        return "{} {}".format(weight, infantry_or_cavalry)
    
    def getStrength(self, setting:str) -> int:
        """Calculate the effective strength of this formation in a given setting"""
        assert setting in ["FIELD", "SEIGEATTACK", "SIEGEDEFEND"], "'setting' must be one of FIELD, SIEGEATTACK, or SIEGEDEFEND, got '{}'".format(setting)
        if setting=="FIELD":
            if self.cavalry and self.heavy:
                return 4 * self.warriorCount 
            elif self.cavalry or self.heavy:
                return 2 * self.warriorCount
            else:
                return self.warriorCount
        else:
            return self.warriorCount
    
    def getTravelTime(self, edge, forced:bool=False) -> int:
        """Returns the time in hours for this formation to travel a graph edge"""
        if (not edge.road) and (self.wagonCount > 0):
            return -1 # wagons cannot travel overland
        if forced:
            if self.cavalry:
                leagues_per_hour = 2
            else:
                leagues_per_hour = 1
        else:
            leagues_per_hour = 0.5
        distance = edge.distance
        hours = distance / leagues_per_hour
        return int(hours)
    
    def getLength(self) -> float:
        """Calculate length in leagues of the formation on the march"""
        if self.cavalry:
            warrior_length_miles = self.warriorCount / 2000
        else:
            warrior_length_miles = self.warriorCount / 5000
        wagon_length_miles = self.wagonCount / 50
        formation_length_miles = warrior_length_miles + wagon_length_miles
        return formation_length_miles / 3 # league conversion
    
    def getSupplyCapacity(self) -> int:
        """Calculate how much supply the formation can transport"""
        if self.cavalry:
            warrior_capacity self.warriorCount * 75
        else:
            warrior_capacity = self.warriorCount * 15
        wagon_capacity = self.wagonCount * 1000
        return warrior_capacity + wagon_capacity
    
    def getSupplyConsumption(self) -> int:
        """Calculate daily consumption of supply for the formation"""
        if self.cavalry:
            warrior_consumption self.warriorCount * 10
        else:
            warrior_consumption = self.warriorCount * 1
        wagon_consumption = self.wagonCount * 10
        return warrior_consumption + wagon_consumption