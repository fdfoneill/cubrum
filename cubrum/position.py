import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from .decisionpoint import DecisionPoint, CrossroadsReached, StrongholdReached
from .exceptions import InvalidActionError, InvalidPositionError
from .map import Map


class Position:
    """The location of an Army on a Map, including marching direction

    ***
    Attributes:
        mapLocation:[str, tuple]
        orientation:str
    """
    def __init__(self, mapLocation:str|tuple, map:Map, orientation:str=None, distanceToDestination:float=None):
        self.mapLocation = mapLocation
        self.map = map
        self.orientation=orientation
        self.distanceToDestination = distanceToDestination
        if self.getPositionType()=="edge":
            assert self.orientation is not None, "When mapLocation is an edge, orientation must be provided"
            assert self.distanceToDestination is not None, "When mapLocation is an edge, distanceToDestination must be provided"
        else:
            if distanceToDestination:
                log.warning("position '{}' is not an edge, ignoring passed value for edgeProgressPercent".format(mapLocation))
            self.distanceToDestination = None
        
    def validate(self):
        try:
            if self.getPositionType()=="edge":
                assert len(self.mapLocation)==2, "expected 2-tuple for edge, got '{}'".format(self.mapLocation)
                assert self.orientation is not None, "When mapLocation is an edge, orientation must be set"
                assert self.distanceToDestination is not None, "When mapLocation is an edge, distanceToDestination must be set"
                try:
                    self.map.edges[self.mapLocation]
                except KeyError:
                    raise AssertionError("edge '{}' not found in map".format(self.mapLocation))
                assert self.distanceToDestination <= self.map.edges[self.mapLocation]['distance'], "distanceToDestination must be less than total distance {} leagues of edge '{}', got {}".format(self.map.edges[self.mapLocation]['distance'], self.mapLocation, self.distanceToDestination)
                assert self.orientation in self.mapLocation, "node '{}' is not an endpoint of edge '{}'".format(self.orientation, self.mapLocation)
            else:
                assert self.mapLocation in self.map.nodes, "node '{}' not found in map".format(self.mapLocation)
                if self.orientation is not None:
                    assert self.orientation in self.map.neighbors(self.mapLocation), "orientation '{}' is not a neighbor of mapLocation '{}'".format(self.orientation, self.mapLocation)
                assert self.distanceToDestination is None, "when mapLocation is a node, distanceToDestination must be None, got '{}'".format(self.distanceToDestination)
        except AssertionError as e:
            raise InvalidPositionError(e)
        
    def getPositionType(self):
        if type(self.mapLocation)==tuple:
            return "edge"
        else:
            return "node"
        
    def getDescription(self):
        if self.getPositionType()=="edge":
            return self.map.edges[self.mapLocation]
        else:
            return self.map.nodes[self.mapLocation]

    def setOrientation(self, orientation:str):
        self.validate()
        try:
            if self.getPositionType()=="edge":
                assert orientation in self.mapLocation, "node '{}' is not an endpoint of edge '{}'".format(orientation, self.mapLocation)
            else:
                assert orientation in self.map.neighbors(self.mapLocation), "orientation '{}' is not a neighbor of mapLocation '{}'".format(orientation, self.mapLocation)
        except AssertionError as e:
            raise InvalidActionError(e)
        self.orientation = orientation

    def move(self, distance:float, toward:str=None) -> DecisionPoint:
        """Update position based on travel distance

        ***

        Parameters:
            distance: distance to travel, measured in leagues
        
        Returns:
            
        """
        self.validate()
        if self.getPositionType()=="edge":
            # edge behavior
            if (toward is not None) and (toward != self.orientation):
                try:
                    assert toward in self.mapLocation, "'{}' is not part of edge '{}'".format(toward, self.mapLocation)
                    self.orientation = toward 
                    self.distanceToDestination = (self.map.edges[self.mapLocation]['distance'] - self.distanceToDestination)
                except AssertionError as e:
                    raise InvalidActionError(e)
            if self.distanceToDestination <= 0:
                self.mapLocation=self.orientation 
                self.orientation = None
                self.distanceToDestination = None
                return None
            if distance >= self.distanceToDestination:
                self.distanceToDestination = 0
                reached_destination = self.map.nodes[self.orientation]
                if reached_destination.get("strongholdType"):
                    return StrongholdReached(strongholdName=reached_destination['name'], **reached_destination)
                else:
                    return CrossroadsReached(crossroads_name = reached_destination['name'], **reached_destination)
            self.distanceToDestination -= distance
        else:
            # node behavior
            if (toward is not None) and (toward != self.orientation):
                try:
                    assert toward in self.map.neighbors(self.mapLocation), "'{}' is not a neighbor of '{}'".format(toward, self.mapLocation)
                    self.orientation = toward 
                except AssertionError as e:
                    raise InvalidActionError(e) 
            if self.orientation is None:
                raise InvalidActionError("updating position from a node but orientation is not set")
            self.mapLocation = (self.mapLocation, self.orientation)
            self.distanceToDestination = self.map.edges[self.mapLocation]['distance']
            self.move(distance)
        return None