import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime
import pandas as pd


class MessageHandler:
    """Records actions, rumors, and letters

    ***

    Attributes:
        akashicRecords:pandas.DataFrame

    Methods:
        addAction() -> None
        addLetter() -> None
        getNews() -> pandas.DataFrame
    """
    def __init__(self):
        self.akashicRecords = pd.DataFrame(
            {
                "messageType":[],
                "creationDate":[],
                "creationLocation":[],
                "text":[],
                "sender":[],
                "recipient":[]
            }
        )