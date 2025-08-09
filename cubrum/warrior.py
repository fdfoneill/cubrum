import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

class Warrior:
    """A single human being; a fighter
    
    ***
    
    Attributes:
        name:str
        age:int
        title:str
        rank:int
        culture:cubrum.culture.Culture
        
    Methods:
        
    """
    pass