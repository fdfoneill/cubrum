import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)


class InvalidActionError(Exception):
    pass

class InvalidPositionError(Exception):
    pass