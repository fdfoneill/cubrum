import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from .culture import Culture


class Warrior:
    """A single human being; a fighter
    
    ***
    
    Attributes:
        name:str
        age:int
        culture:cubrum.culture.Culture
        
    Methods:
        
    """
    def __init__(self, name:str, age:int, culture:Culture=None, id:int=None):
        self.name = name
        self.age = int(age)
        assert self.age>0, "age must be positive, got {}".format(self.age)
        self.culture = culture
        self.id = int(id) if id is not None else None