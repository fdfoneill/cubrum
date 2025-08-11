import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime
import numpy as np

class Weather:
    """Represents the weather of an area
    
    ***
    Attributes:
        season:str
        currentWeather:str 
        weatherTypes:list
    Methods:
        dateToSeason() -> str
        getPotentialWeather() -> list
        changeCurrentWeather() -> None
        getBattleModifier() -> int
        getMovementModifier() -> int
    """
    def __init__(self, startingSeason:str="spring", startingWeather:str="fair"):
        self.season = startingSeason
        self.weatherTypes={
            'fair':{'seasons':['spring','summer','autumn','winter'], 'weight':2},
            'rain':{'battleModifier':-1, 'movementModifier':90, 'seasons':['spring','summer','autumn','winter']},
            'overcast':{'seasons':['spring','autumn','winter']},
            'snow':{'battleModifier':-1, 'movementModifier':75, 'seasons':['winter']},
            'storm':{'battleModifier':-1, 'movementModifier':75, 'seasons':['spring','summer','autumn'], 'weight':0.5},
            'blizzard':{'battleModifier':-1, 'movementModifier':10, 'seasons':['winter'], 'weight':0.5},
            'windy':{'seasons':['spring','autumn','winter']},
            'hot':{'seasons':['summer']},
            'cold':{'seasons':['spring','autumn','winter']}
        }
        assert startingWeather in [w for w in self.weatherTypes.keys()]
        self.currentWeather = startingWeather

    def dateToSeason(self, date:datetime.datetime) -> str:
        month = int(date.strftime("%m"))
        if month > 3:
            return "winter"
        elif month > 6:
            return "spring"
        elif month > 9:
            return "summer"
        elif month > 12:
            return "autumn"
        
    def getPotentialWeather(self, season:str=None) -> list:
        season = season or self.season
        return [w for w in self.weatherTypes.keys() if season in self.weatherTypes[w]['seasons']]
    
    def changeCurrentWeather(self) -> str:
        potential_weather = self.getPotentialWeather(self.season)
        weights = np.array([self.weatherTypes[pw].get('weight', 1) for pw in potential_weather])
        weights_normalized = weights/weights.sum()
        new_weather = np.random.choice(potential_weather, p=weights_normalized)
        self.currentWeather = str(new_weather)
        return self.currentWeather
    
    def getBattleModifier(self) -> int:
        return self.weatherTypes[self.currentWeather].get("battleModifier", 0)
    
    def getMovementModifer(self) -> int:
        return self.weatherTypes[self.currentWeather].get("movementModifier", 100)