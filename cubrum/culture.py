import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import numpy as np

# Allakian, Delisgrene, Bostite, Boonan, Bemm, Islish


class Culture:
    """For generating names and titles
    
    ***
    
    Attributes:
        cultureName:str
        titlesMiltary:list
        titlesNobility:list
        titlesReligious:list
        
    Methods:
        generateName() -> str
        generateTitle() -> str
        getTitleRank() -> int
    """
    def __init__(self, cultureName:str, titlesMiltary:list=None, titlesNobility:list=None, titlesReligious:list=None):
        self.cultureName=cultureName
        self.titlesMiltary = titlesMiltary or []
        self.titlesNobility = titlesNobility or []
        self.titlesReligious = titlesReligious or []
        
    def generateSyllable(self):
        raise NotImplementedError()
        
    def generateName(self):
        raise NotImplementedError()
        
    def generateTitle(self, sphere:str, rank_minimum:int=None, rank_maximum:int=None) -> str:
            if sphere=="military":
                titles=[t for t in self.titlesMiltary]
            elif sphere=="nobility":
                titles=[t for t in self.titlesNobility]
            elif sphere=="religious":
                titles=[t for t in self.titlesReligious]
            else:
                raise ValueError("sphere must be one of [military, nobility, religious], got '{}'".format(sphere))
            choices= []
            for i in range(len(titles)):
                rank_i = i+1
                title_i = titles[i]
                if (rank_i <= rank_minimum) and (rank_i <= rank_maximum) and (title_i is not None):
                    choices.append(title_i) 
            return np.random.choice(choices)
        
    def getTitleRank(self, title:str) -> int:
        for sphere_titles in [self.titlesMiltary, self.titlesNobility, self.titlesReligious]:
            for i in range(len(sphere_titles)):
                if sphere_titles[i] == title:
                    return i+1
            return -1
            