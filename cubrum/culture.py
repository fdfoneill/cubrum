import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import numpy as np

# Allakian, Delisgrene, Boonan, Dinn, Islish


class Culture:
    """For generating names and titles
    
    ***
    
    Attributes:
        cultureName:str
        names:list
        titles:list
        
    Methods:
        generateName() -> str
        generateTitle() -> str
        getTitleRank() -> int
    """
    def __init__(self, cultureName:str, names:list=None, titles:list=None):
        self.cultureName=cultureName
        self.names = names or []
        self.namesUsed = [False for name in self.names]
        self.titles = titles or []

    def generateName(self, unusedOnly:bool=True, updateUsed:bool=True) -> str:
        name_indices = []
        for i in range(len(self.names)):
            if (not self.namesUsed[i]) or (not unusedOnly):
                name_indices.append(i)
        if len(name_indices)<1:
            log.warning("all {} names used, reusing".format(self.cultureName))
            return self.generateName(unusedOnly=False)
        chosen_index = np.random.choice(name_indices) 
        chosen_name = self.names[chosen_index]
        if updateUsed:
            self.namesUsed[chosen_index] = True 
        return chosen_name

    def generateTitle(self, minRank:int=None, maxRank:int=None) -> str:
        assert len(self.titles) > 0, "no titles from which to generate"
        if minRank:
            assert minRank > 0, "rank must be greater than 0"
            assert minRank <= len(self.titles), "cannot get rank {} from title list with length {}".format(minRank, len(self.titles))
        else:
            minRank=0
        if maxRank:
            assert maxRank > 0, "rank must be greater than 0"
            assert maxRank <= len(self.titles), "cannot get rank {} from title list with length {}".format(maxRank, len(self.titles))
        else:
            maxRank=len(self.titles)
        assert minRank <= maxRank, "minRank cannot be greater than maxRank: {}>{}".format(minRank, maxRank)
        rank_choices = [r for r in range(minRank, maxRank+1)]
        chosen_rank = np.random.choice(rank_choices)
        return self.titles[chosen_rank]
       
    def getTitleRank(self, title:str) -> int:
        if title in self.titles:
            return self.titles.index(title) 
        else:
            return -1
            

ALLAKIAN = Culture(
    "Allakian", 
    names=[
        "Malden",
        "Strough",
        "Dudek",
        "Yoman",
        "Broughan",
        "Peyker",
        "Crannan",
        "Golin",
        "Jelalk",
        "Iviss",
        "Effeth",
        "Gostin",
        "Nalgin",
        "Volish"
    ],
    titles=[
        "Prince",
        "Baron",
        "Commodore",
        "Knight-Captain",
        "Captain",
        "Sir"
    ]
)

BOONAN = Culture(
    cultureName="Boonan",
    names=[
        "Foolan",
        "Hoanee",
        "Mendoo",
        "Mey",
        "Drola",
        "Sonab",
        "Honiriri",
        "Joonin",
        "Boaloo",
        "Meramab",
        "Kirunga",
        "Nkerey"
    ],
    titles=[
        "High Marshall",
        "Marshall",
        "Warden",
        "Captain",
        "Commander",
        "Chief"
    ]
)

DELISGRENE = Culture(
    cultureName="Delisgrene",
    names=[
        "Voltiziar",
        "Soman",
        "Bostion",
        "Lavran",
        "Agnos",
        "Gultiziar",
        "Triulgin",
        "Brosh",
        "Nalish",
        "Brygost",
        "Alwis",
        "Dargren"
    ],
    titles=[
        "Empress",
        "Duke",
        "Marquis",
        "Count",
        "Lord",
        "Sir"
    ]
)

DINN = Culture(
    cultureName="Dinn",
    names=[
        "Urungar",
        "Mennar",
        "Parum",
        "Nkuga",
        "Ongum",
        "Jonjey",
        "Onga",
        "Rekiku",
        "Kirraney",
        "Irawe",
        "Arai",
        "Burawar"
    ],
    titles=[
        "Sultan",
        "Councillor",
        "General",
        "Captain",
        "Honorable"
    ]
)

ISLISH = Culture(
    cultureName="Islish",
    names=[
        "Cratch",
        "Malkal",
        "Kalitz",
        "Rath",
        "Rabbachir",
        "Gurm",
        "Verk",
        "Petch",
        "Targitch",
        "Habbetch",
        "Gulkir",
        "Gemz"
    ],
    titles=[
        "Governor",
        "Headman",
        "Big Man",
        "Boss",
        "Gangboss",
        "Tough"
    ]
)
