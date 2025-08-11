import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

class Warrior:
    """A single human being; a fighter
    
    ***
    
    Attributes:
        name:str
        age:int
        culture:cubrum.culture.Culture
        
    Methods:
        
    """
    def __init__(self, name:str, age:int, culture=None):
        self.name = name
        self.age = int(age)
        self.culture = culture