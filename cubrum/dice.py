import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import numpy as np
from typing import Union

def rollD6(n:int=1, sum:bool=True) -> Union[int, tuple]:
    rolls = []
    for i in range(n):
        rolls.append(np.random.randint(1, 7))
    if sum:
        return int(np.array(rolls).sum())
    else:
        return tuple([int(r) for r in rolls])
    
def rollD20(n:int=1, sum:bool=True) -> Union[int, tuple]:
    rolls = []
    for i in range(n):
        rolls.append(np.random.randint(1, 21))
    if sum:
        return int(np.array(rolls).sum())
    else:
        return tuple([int(r) for r in rolls])