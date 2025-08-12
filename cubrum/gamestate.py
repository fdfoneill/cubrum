import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime, sys
import pandas as pd

from .gameclock import GameClock
from .messagehandler import MessageHandler
from .map import Map
from .army import Army

COPPERCOAST_NODES_PATH = os.path.join(os.path.dirname(__file__), "mapdata", "coppercoast_strongholds.json")
COPPERCOAST_ROADS_PATH = os.path.join(os.path.dirname(__file__), "mapdata", "coppercoast_roads.json")
COPPERCOAST_MAP = Map()
COPPERCOAST_MAP.addNodesFromFile(COPPERCOAST_NODES_PATH)
COPPERCOAST_MAP.addEdgesFromFile(COPPERCOAST_ROADS_PATH)


class GameState:
    """Master class for running a game in cubrum

    ***

    Attributes:
        map[Map]: road network in game area
        clock[GameClock]: clock tracking game time and players
        correspondents[pandas.DataFrame]: DataFrame pairing senders and recipients 
            of letterswith their unique IDs 
        armies[list]: all Army objects currently active in-game
        playerToArmy[dict]: map of player ID to index in armies attribute

    Methods:
        addPlayer() -> int
        getPlayers() -> list
        addArmy() -> int
        addCorrespondent() -> int
        getRecipients() -> pandas.DataFrame
        getOptions() -> list
        applyAction() -> 
    """
    def __init__(self, map:Map=COPPERCOAST_MAP, startDate:str="1410-05-20"):
        self.clock = GameClock(datetime.datetime.strptime(startDate+":7", "%Y-%m-%d:%H"),players=[])
        self.messages = MessageHandler()
        self.correspondents = pd.DataFrame(
            {
                "ID":[0],
                "name":["system"],
                "validRecipient":[False]
            }
        )
        self.map=map
        for node in self.map.nodes:
            if self.map.nodes[node].get("strongholdType"):
                correspondent_name = "{} garrison".format(node)
                node_id = self.addCorrespondent(correspondentName=correspondent_name, validRecipient=False)
                self.map.nodes[node]['id'] = node_id
        self.armies = []
        self.playerToArmy = {}

    def addPlayer(self, playerName:str) -> int:
        """Pass a player name, get a new player ID"""
        new_id = self.addCorrespondent(correspondentName=playerName, validRecipient=True)
        self.clock.addPlayer(new_id)
        self.playerToArmy[new_id] = None
        return new_id
    
    def getPlayers(self) -> list:
        return list(self.playerToArmy.keys())

    def addArmy(self, newArmy:Army, playerID:int=None) -> int:
        if playerID:
            newArmy.commander.id = playerID
        else:
            playerID = newArmy.commander.id 
        if playerID is None:
            raise ValueError("Army has no current player and playerID not set")
        if self.playerToArmy.get(playerID) is not None:
            raise ValueError("Player with id '{}' already assigned army '{}'".format(playerID, self.armies(self.playerToArmy[playerID])))
        new_army_index = len(self.armies)
        self.armies.append(newArmy)
        self.playerToArmy[playerID] = new_army_index

    def addCorrespondent(self, correspondentName:str, validRecipient:bool=True) -> int:
        new_id = len(self.correspondents)
        new_correspondent = {
            "ID":int(new_id),
            "name":str(correspondentName),
            "validRecipient":bool(validRecipient)
        }
        self.correspondents.loc[new_id] = new_correspondent
        return new_id
    
    def getRecipients(self) -> pd.DataFrame:
        return self.correspondents.loc[self.correspondents["validRecipient"]==True]
    
    def getMessages(self, playerID:int) -> pd.DataFrame:
        """Return subset of messages addressed to player that have been recieved at current time"""
        messages_addressed = self.messages.akashicRecords.loc[self.messages.akashicRecords['recipientID']==playerID]
        messages_recieved = messages_addressed.loc[messages_addressed['receiptDate'] != None]
        messages_recieved = messages_recieved.loc[messages_addressed['receiptDate'] <= self.clock.getPlayerTime(playerID)]
        return messages_recieved
    
    def getOptions(self, playerID:int) -> list:
        pass
    
    def applyAction(self, action):
        return action.apply(self)