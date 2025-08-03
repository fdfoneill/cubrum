#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 14:33:20 2025

@author: DanO
"""

import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from .node import Node 

class Stronghold(Node):
    """City, town, or fortress
    
    ***
    
    Attributes:
        name:str
        strongholdType:str
        thresholdMax:int
        thresholdCurrent:int
        supplyCount:int
        lootCount:int
        morale:int
        
    Methods:
        getGarrisonCount() -> int
    """
    pass