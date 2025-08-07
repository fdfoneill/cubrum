import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from .warrior import Warrior

class Commander(Warrior):
    pass