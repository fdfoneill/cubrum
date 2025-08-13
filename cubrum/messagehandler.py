import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime
import numpy as np
import pandas as pd
from typing import Union

from .map import Map
from .position import PointPosition, ColumnPosition


class MessageHandler:
    """Records actions, rumors, and letters

    ***

    Attributes:
        akashicRecords:pandas.DataFrame

    Methods:
        addEvent() -> None
        addLetter() -> None
        getMessages() -> pandas.DataFrame
    """
    def __init__(self):
        self.akashicRecords = pd.DataFrame(
            {
                "messageType":[],
                "creationDate":[],
                "creationLocation":[],
                "receiptDate":[],
                "text":[],
                "senderID":[],
                "recipientID":[],
                "link":[]
            }
        )
        self.messageTypes = [
            "EVENT",
            "RUMOR",
            "LETTER"
        ]

    def __repr__(self):
        return self.akashicRecords.__repr__()
    
    @property
    def loc(self):
        return self.akashicRecords.loc 
    
    @property
    def iloc(self):
        return self.akashicRecords.iloc

    def addLetter(self, text:str, senderID:str, recipientID:str, creationDate:datetime.datetime, creationPosition:Union[PointPosition, ColumnPosition], recipientPosition:Union[PointPosition, ColumnPosition], messengerSpeed:float=1, safeDeliveryPercent:int=80) -> int:
        """Adds a LETTER record to the messageHandler, and an EVENT record if the letter will be lost along the way
        """
        # extract vanPositions 
        if type(creationPosition)==ColumnPosition:
            creationPosition = creationPosition.vanPosition
        if type(recipientPosition)==ColumnPosition:
            recipientPosition=recipientPosition.vanPosition
        # calculate travel time
        travel_distance = creationPosition.getDistance(recipientPosition)
        travel_time = messengerSpeed * travel_distance
        remaining_time = travel_time
        receiptDate = creationDate
        while remaining_time > 0:
            receiptDate += datetime.timedelta(hours=1)
            remaining_time -= 1
            while (int(receiptDate.strftime("%H")) >= 21) or (int(receiptDate.strftime("%H")) <= 5): # messengers don't travel at night
                receiptDate += datetime.timedelta(hours=1)
        # convert creationLocation to pretty string 
        creation_location_string = str(creationPosition)
        # add letter message 
        letter_id = len(self.akashicRecords)
        new_message = {
            "messageType":"LETTER",
            "creationDate":creationDate,
            "creationLocation":creation_location_string,
            "receiptDate":receiptDate,
            "text":text,
            "senderID":senderID,
            "recipientID":recipientID,
            "link":None
            }
        self.akashicRecords.loc[letter_id] = new_message
        return_value = letter_id
        # check for intercepted messenger
        if np.random.randint(1, 101) > safeDeliveryPercent: # message lost
            # lost_date = creationDate + ((receiptDate-creationDate)/2)
            lost_date = receiptDate
            event_text = "letter lost along the way"
            event_id = self.addEvent(event_text, lost_date, recipientPosition, link=letter_id)
            self.akashicRecords.loc[letter_id, "receiptDate"] = None
            self.akashicRecords.loc[letter_id, "link"] = event_id 
            return_value = event_id
        return return_value

    def addEvent(self, text:str, creationDate:datetime.datetime, creationPosition:PointPosition, link:int=None) -> int:
        # convert creationLocation to pretty string 
        creation_location_string = str(creationPosition)
        event_id = len(self.akashicRecords)
        new_message = {
            "messageType":"EVENT",
            "creationDate":creationDate,
            "creationLocation":creation_location_string,
            "recieptDate":None,
            "text":text,
            "senderID":0,
            "recipientID":None,
            "link":link
        }
        self.akashicRecords.loc[event_id] = new_message
        return event_id