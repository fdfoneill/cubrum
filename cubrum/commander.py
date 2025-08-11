import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from .warrior import Warrior

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
    def __init__(self, name:str, age:int, title:str, culture=None, commanderTraits:list=None):
        super().__init__(name, age, culture)
        self.title=title
        self.commanderTraits = (commanderTraits or [])

    def __repr__(self):
        return "{} {}".format(self.title, self.name)