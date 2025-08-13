import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime

from .decisionpoint import DecisionPoint, DayBreaks, NightFalls

SUNRISE = 5
SUNSET = 21

class GameClock:
    """Track in-game passage of time and turn order
    
    ***
    
    Attributes:
        masterTime:datetime.datetime 
        playerTimes:dict
        
    Methods:
        updateMasterTime()
        getActivePlayer() -> int
        incrementPlayerTime() -> None
    """
    def __init__(self, startTime:datetime.datetime, players:list):
        self.masterTime = startTime 
        self.playerTimes = {p:startTime for p in players}

    def __repr__(self):
        return self.masterTime.strftime("%Y-%m-%d:%H00")

    def addPlayer(self, playerID:int):
        """Add a new player to time tracking"""
        assert playerID not in self.playerTimes.keys(),"player '{}' already exists".format(playerID)
        self.playerTimes[playerID] = self.masterTime
        
    def updateMasterTime(self):
        """Set master time to latest of all player times"""
        latest_time = self.masterTime
        for p in self.playerTimes.keys():
            player_time = self.playerTimes[p]
            if latest_time < player_time:
                latest_time = player_time
        self.masterTime=latest_time
        
    def getActivePlayer(self) -> int:
        """Return player with earliest time"""
        active_player = None
        earliest_time = None
        for p in self.playerTimes.keys():
            player_time = self.playerTimes[p]
            if (earliest_time is None) or (earliest_time > player_time):
                earliest_time = player_time
                active_player=p
        return active_player
    
    def getPlayerTime(self, playerID:int) -> datetime.datetime:
        if playerID==0:
            return self.masterTime
        assert playerID in self.playerTimes.keys(), "player id '{}' not found in GameClock".format(playerID)
        return self.playerTimes[playerID]
    
    def incrementPlayerTime(self, playerID:int, hours:int) -> DecisionPoint:
        """Add hours to a player's current time
        
        ***
        
        Parameters:
            playerID: integer ID of player
            hours: how many hours to increment player's clock
            
        Returns:
            if crossing dawn, DayBreaks. if crossing dusk, NightFalls. else None
        """
        assert playerID in self.playerTimes.keys(), "player '{}' not being tracked".format(playerID)
        time_delta = datetime.timedelta(hours=hours)
        self.playerTimes[playerID] = self.playerTimes[playerID] + time_delta
        if (int(self.playerTimes[playerID].strftime("%H")) >= SUNRISE) and (int((self.playerTimes[playerID]-time_delta).strftime("%H")) < SUNRISE):
            return DayBreaks()
        if (int(self.playerTimes[playerID].strftime("%H")) >= SUNSET) and (int((self.playerTimes[playerID]-time_delta).strftime("%H")) < SUNSET):
            return NightFalls()
        self.updateMasterTime()
        