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
        getActivePlayer() -> str
        incrementPlayerTime() -> None
    """
    def __init__(self, startTime:datetime.datetime, players:list):
        self.masterTime = startTime 
        self.playerTimes = {p:startTime for p in players}
        
    def updateMasterTime(self):
        """Set master time to latest of all player times"""
        latest_time = self.masterTime
        for p in self.playerTimes.keys():
            player_time = self.playerTimes[p]
            if latest_time < player_time:
                latest_time = player_time
        self.masterTime=latest_time
        
    def getActivePlayer(self) -> str:
        """Return player with earliest time"""
        active_player = None
        earliest_time = None
        for p in self.playerTimes.keys():
            player_time = self.playerTimes[p]
            if (earliest_time is None) or (earliest_time > player_time):
                earliest_time = player_time
                active_player=p
        return active_player
    
    def incrementPlayerTime(self, player:str, hours:int) -> DecisionPoint:
        """Add hours to a player's current time
        
        ***
        
        Parameters:
            player: string ID of player
            hours: how many hours to increment player's clock
            
        Returns:
            if crossing dawn, DayBreaks. if crossing dusk, NightFalls. else None
        """
        assert player in self.playerTimes.keys(), "player '{}' not being tracked".format(player)
        time_delta = datetime.timedelta(hours=hours)
        self.playerTimes[player] = self.playerTimes[player] + time_delta
        if (int(self.playerTimes[player].strftime("%H")) >= SUNRISE) and (int((self.playerTimes[player]-time_delta).strftime("%H")) < SUNRISE):
            return DayBreaks()
        if (int(self.playerTimes[player].strftime("%H")) >= SUNSET) and (int((self.playerTimes[player]-time_delta).strftime("%H")) < SUNSET):
            return NightFalls()
        