import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime, sys
import pandas as pd

from .gameclock import GameClock
from .messagehandler import MessageHandler
from .map import Map
from .army import Army
from .exceptions import NoSuchPlayerError

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

    def __repr__(self):
        repr_string = "<GameState: "
        repr_string+=str(self.clock)
        repr_string+=">"
        return repr_string

    def addPlayer(self, playerName:str) -> int:
        """Takes a player name and returns a new player ID
        
        Also adds the new player to the correspondents
            dataframe, clock, and playerToArmy dictionary 
            attributes
        """
        new_id = self.addCorrespondent(correspondentName=playerName, validRecipient=True)
        self.clock.addPlayer(new_id)
        self.playerToArmy[new_id] = None
        return new_id
    
    def getPlayers(self) -> list:
        """Returns list of valid player ID integers"""
        return list(self.playerToArmy.keys())
    
    def getPlayerName(self, playerID:int) -> str:
        """Returns string name associated with player ID"""
        try:
            matching_correspondents = self.correspondents.loc[self.correspondents['ID']==playerID, "name"]
            assert len(matching_correspondents)>0, "player with ID={} not found".format(playerID)
            assert len(matching_correspondents)==1, "multiple records returned for ID={}".format(playerID)
            return str(matching_correspondents.iloc[0])
        except AssertionError as e:
            raise NoSuchPlayerError(e)

    def addArmy(self, newArmy:Army, playerID:int=None) -> int:
        """Adds an Army object to the armies attribute

        ***

        Parameters:
            newArmy: Army object to be appended to list 
            playerID: Optional. If provided, sets newArmy.commander.id and 
                pairs this army with playerID in the playerToArmy attribute.
                If not set, playerID is instead drawn from newArmy.commander.id
        
        Returns:
            new_army_index: positional index of newly-added Army within
                armies attribute
        """
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
        """Adds a new item to correspondents dataframe

        ***
        
        Parameters:
            correspondentName: string name to associate with correspondent
            validRecipient: whether this correspondent should be presented as 
                able to recieve letters. Default True 
            
        Returns:
            correspondent_id: integer ID of newly added correspondent
        """
        new_id = len(self.correspondents)
        new_correspondent = {
            "ID":int(new_id),
            "name":str(correspondentName),
            "validRecipient":bool(validRecipient)
        }
        self.correspondents.loc[new_id] = new_correspondent
        return new_id
    
    def getRecipients(self) -> pd.DataFrame:
        """Return list of correspondents for which validRecipient is True
        """
        return self.correspondents.loc[self.correspondents["validRecipient"]==True]
    
    def getMessages(self, playerID:int) -> pd.DataFrame:
        """Return subset of messages addressed to player that have been recieved at current time
        
        ***
        Parameters:
            playerID: ID integer of player whose messages should be retrieved
        """
        try:
            assert playerID in self.getPlayers(), "player with ID={} not found".format(playerID)
        except AssertionError as e:
            raise NoSuchPlayerError(e)
        messages_addressed = self.messages.akashicRecords.loc[self.messages.akashicRecords['recipientID']==playerID]
        messages_recieved = messages_addressed.loc[messages_addressed['receiptDate'] != None]
        messages_recieved = messages_recieved.loc[messages_addressed['receiptDate'] <= self.clock.getPlayerTime(playerID)]
        return messages_recieved
    
    def getOptions(self, playerID:int) -> list:
        if not playerID in self.getPlayers():
            raise NoSuchPlayerError("player with ID={} not found".format(playerID))
        pass
    
    def applyAction(self, action):
        return action.apply(self)