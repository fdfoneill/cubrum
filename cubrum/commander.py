import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import numpy as np

from .warrior import Warrior
from .culture import Culture
from .dice import rollD6, rollD20

COMMANDER_TRAITS = [
    "Beloved",
    "Brutal",
    "Commando",
    "Crusader",
    "Defensive Engineer",
    "Duelist",
    "Guardian",
    "Honorable",
    "Ironsides",
    "Logistician",
    "Outrider",
    "Poet",
    "Raider",
    "Ranger",
    "Scholar",
    "Siege Engineer",
    "Spartan",
    "Stubborn",
    "Vanquisher",
    "Veteran"
]


class Commander(Warrior):
    """A leader of armies
    
    ***
    
    Attributes:
        name:str
        age:int
        title:str
        culture:cubrum.culture.Culture
        commanderTraits:list
        
    Methods:
        
    """
    def __init__(self, name:str, age:int, title:str, pedigree:str=None, culture:Culture=None, commanderTraits:list=None):
        super().__init__(name, age, culture)
        self.title=title
        self.pedigree=pedigree
        self.commanderTraits = (commanderTraits or [])
        for trait in self.commanderTraits:
            assert trait in COMMANDER_TRAITS, "invalid commander trait '{}'".format(trait)

    def __repr__(self):
        repr_string = "{} {}".format(self.title, self.name)
        if self.pedigree:
            repr_string += " {}".format(self.pedigree)
        return repr_string
    
    def getRelationship(self, isFemale:bool=False, maxIndex:int=None) -> tuple:
        """Returns tuple of relationship string and age integer

        ***
        
        Parameters:
            isFemale: whether to choose female relationship terms (e.g 
                'niece' instead of 'nephew'). Default False
            maxIndex: upper bound on random table
        """
        relationship_results = [
            ("Child", 14+rollD6(3, sum=True)),
            ("Sibling", 20+rollD20(2, sum=True)),
            ("Parent", 30+rollD20(3, sum=True)),
            ("Niece" if isFemale else "Nephew", 16+rollD20(1, sum=True)),
            ("Aunt" if isFemale else "Uncle", 30+rollD20(3, sum=True)),
            ("Cousin", 20+rollD20(2, sum=True)),
            None,
            None,
            ("Spouse", 20+rollD20(2, sum=True)),
            ("Friend", 20+rollD20(2, sum=True)),
            ("Rival", 20+rollD20(2, sum=True)),
            ("Student", 16+rollD20(1, sum=True)),
            ("Teacher", 30+rollD20(3, sum=True)),
            ("Confessor", 20+rollD20(3, sum=True)),
            ("Advisor", 20+rollD20(3, sum=True)),
            ("Bodyguard", 20+rollD20(1, sum=True)),
            ("Quartermaster", 20+rollD20(2, sum=True)),
            ("Creditor", 20+rollD20(2, sum=True)),
            ("Favorite", 16+rollD20(2, sum=True)),
            ("Ally", 14+rollD20(3, sum=True))
        ]
        if maxIndex is None:
            maxIndex = len(relationship_results)
        max_index = min(maxIndex, len(relationship_results))
        index_choice = np.random.choice([i for i in range(max_index)])
        # log.debug(index_choice)
        if index_choice==6:
            return tuple([t[0]+t[1] for t in zip(("Step-", 0), self.getRelationship(isFemale=isFemale, maxIndex=5))])
        elif index_choice==7:
            return tuple([t[1]+t[0] for t in zip(("-in-Law", 0), self.getRelationship(isFemale=isFemale, maxIndex=5))])
        else:
            return relationship_results[index_choice]