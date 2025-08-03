#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 14:33:15 2025

@author: DanO
"""

import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

class Node:
    """Node on the map graph
    
    ***
    
    Attributes:
        name
    
    Methods:
        getNeighbors() -> tuple
        getPathTo() -> list
    """
    pass