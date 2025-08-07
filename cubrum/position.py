import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from typing import Union

from .decisionpoint import DecisionPoint, CrossroadsReached, StrongholdReached
from .exceptions import InvalidActionError, InvalidPositionError
from .map import Map


class PointPosition:
    """The location of a single point on a Map, including movement direction

    ***
    Attributes:
        mapLocation:[str, tuple]
        orientation:str
        map:cubrum.map.Map

    Methods:
        validate() -> None
        getPositionType() -> str
        getDescription() -> dict
        setOrientation() -> None
        move() -> DecisionPoint
        getDistance() -> float
    """
    def __init__(self, mapLocation:Union[str, tuple], map:Map, orientation:str=None, distanceToDestination:float=None):
        self.mapLocation = mapLocation
        self.map = map
        self.orientation=orientation
        self.distanceToDestination = distanceToDestination
        if self.getPositionType()=="edge":
            assert self.orientation is not None, "When mapLocation is an edge, orientation must be provided"
            assert self.distanceToDestination is not None, "When mapLocation is an edge, distanceToDestination must be provided"
        else:
            if distanceToDestination:
                log.warning("position '{}' is not an edge, ignoring passed value for distanceToDestination".format(mapLocation))
            self.distanceToDestination = None
        
    def validate(self) -> None:
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
        
    def copy(self) -> "PointPosition":
        return PointPosition(mapLocation=self.mapLocation, map=self.map, orientation=self.orientation, distanceToDestination=self.distanceToDestination)
    
    def getPositionType(self) -> str:
        if type(self.mapLocation)==tuple:
            return "edge"
        elif type(self.mapLocation)==str:
            return "node"
        else:
            raise InvalidPositionError("type of mapLocation must be tuple or str, got {}".format(type(self.mapLocation)))
        
    def getDescription(self) -> dict:
        if self.getPositionType()=="edge":
            return self.map.edges[self.mapLocation]
        else:
            return self.map.nodes[self.mapLocation]

    def setOrientation(self, orientation:str) -> None:
        self.validate()
        try:
            if self.getPositionType()=="edge":
                assert orientation in self.mapLocation, "node '{}' is not an endpoint of edge '{}'".format(orientation, self.mapLocation)
                if orientation != self.orientation:
                    new_distance_to_destination = self.getDescription()['distance'] - self.distanceToDestination
                else:
                    new_distance_to_destination = self.distanceToDestination
            else:
                assert (orientation is None) or (orientation in self.map.neighbors(self.mapLocation)), "orientation '{}' is not a neighbor of mapLocation '{}'".format(orientation, self.mapLocation)
                new_distance_to_destination = self.distanceToDestination
        except AssertionError as e:
            raise InvalidActionError(e)
        self.orientation = orientation
        self.distanceToDestination = new_distance_to_destination

    def reverseCourse(self) -> None:
        self.validate()
        if self.getPositionType()=="node":
            raise InvalidActionError("Cannot reverse course while on a node")
        if not self.orientation:
            raise InvalidActionError("Cannot reverse course when orientation is not set")
        new_orientation = self.mapLocation[0] if self.mapLocation[0]!=self.orientation else self.mapLocation[1]
        new_distance_to_destination = self.getDescription()['distance'] - self.distanceToDestination
        self.setOrientation(new_orientation)
        self.distanceToDestination = new_distance_to_destination

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
    
    def getDistance(self, other:"PointPosition") -> float:
        """Return distance in leagues along shortest route between positions"""
        self.validate()
        other.validate()
        if (self.getPositionType() == "node") and (other.getPositionType() =="node"): # easy two-node case
            if self.mapLocation==other.mapLocation:
                return 0
            shortest_path = self.map.getShortestPath(self.mapLocation, other.mapLocation)
            path_length = self.map.getPathLength(shortest_path)
            return path_length
        elif (self.getPositionType()=="edge") and (other.getPositionType()=="node"): # self edge, other node
            distance_choices = []
            for node_name in self.mapLocation: # iterate over edges
                node_position = PointPosition(node_name, map=self.map)
                node_position.validate()
                distance_to_adjacent_node =  node_position.getDistance(other)
                if node_name==self.orientation:
                    distance_choices.append(distance_to_adjacent_node+self.distanceToDestination)
                else:
                    distance_choices.append(distance_to_adjacent_node+(self.getDescription()['distance'] - self.distanceToDestination))
            return distance_choices[0] if (distance_choices[0] < distance_choices[1]) else distance_choices[1]
        elif (self.getPositionType()=="node") and (other.getPositionType()=="edge"): # self node, other edge
            # reverse case already handled, so just switch self and other
            return other.getDistance(self)
        else: # both edges
            if set(self.mapLocation)==set(other.mapLocation): # same-edge case
                if self.orientation==other.orientation: # same edge, pointed the same way
                    return abs(other.distanceToDestination-self.distanceToDestination) 
                else: # same edge, pointed opposite ways
                    others_distance_to_self_destination = (other.getDescription()["distance"]-other.distanceToDestination)
                    return abs(others_distance_to_self_destination-self.distanceToDestination)
            distance_choices = []
            for node_name in self.mapLocation: # iterate over edges
                node_position = PointPosition(node_name, map=self.map)
                node_position.validate()
                distance_to_adjacent_node =  other.getDistance(node_position)
                if node_name==self.orientation:
                    distance_choices.append(distance_to_adjacent_node+self.distanceToDestination)
                else:
                    distance_choices.append(distance_to_adjacent_node+(self.getDescription()['distance'] - self.distanceToDestination))
            return distance_choices[0] if (distance_choices[0] < distance_choices[1]) else distance_choices[1]


class ColumnPosition:
    """Position of an Army column on a map, spread out or concentrated
    
    ***
    
    Attributes:
        vanPosition: PointPosition of vanguard
        rearPosition: PointPosition of rearguard
        columnLength: full extent of column on the march

    Methods:
        validate() -> None 
        reverseCourse() -> None
        getCurrentLength() -> float
        setDestination() -> None

    """
    def __init__(self, vanPosition:PointPosition, rearPosition:PointPosition=None, columnLength:float=None, waypoints:list=None):
        self.vanPosition = vanPosition
        self.rearPosition = (rearPosition or vanPosition.copy())
        self.columnLength = (columnLength or self.GetCurrentLength())
        self.waypoints = (waypoints or [])
        self.waypoints = list(self.waypoints)

    def validate(self):
        self.vanPosition.validate()
        self.rearPosition.validate()
        try:
            assert self.getCurrentLength() <= self.columnLength, "column length {} greater than maximum length {}".format(self.getCurrentLength(), self.columnLength)
            if len(self.waypoints) > 0:
                # if there are waypoints 
                # validate waypoint adjacency
                if len(self.waypoints) > 1:
                    for i in range(1, len(self.waypoints)):
                        test_edge = (self.waypoints[i-1], self.waypoints[i])
                        try:
                            self.vanPosition.map.edges[test_edge]
                        except:
                            raise InvalidPositionError("waypoints '{}' and '{}' are not adjacent".format(self.waypoints[i-1], self.waypoints[i]))
                # check rearPosition
                if self.rearPosition.getPositionType()=="node":
                    assert self.rearPosition.mapLocation!=self.waypoints[-1], "last waypoint '{}' is the same as rearPosition '{}'".format(self.waypoints[-1], self.rearPosition.mapLocation)
                    assert self.rearPosition.mapLocation in self.rearPosition.map.neighbors(self.waypoints[-1]), "rearPosition '{}' not adjacent to last waypoint '{}'".format(self.rearPosition.mapLocation, self.waypoints[-1])
                else:
                    assert self.waypoints[-1] in self.rearPosition.mapLocation, "last waypoint '{}' not an endpoint of rearPosition '{}'".format(self.waypoints[-1], self.rearPosition.mapLocation)
                    if self.rearPosition.orientation:
                        assert self.rearPosition.orientation==self.waypoints[-1], "rearPosition is oriented away from last waypoint '{}'".format(self.waypoints[-1])
                # check vanPosition
                if self.vanPosition.getPositionType()=="node":
                    assert self.waypoints[0]!=self.vanPosition.mapLocation, "first waypoint '{}' is the same as vanPosition '{}'".format(self.waypoints[0], self.vanPosition.mapLocation)
                    assert self.vanPosition.mapLocation in self.vanPosition.map.neighbors(self.waypoints[0]), "vanPosition '{}' not adjacent to first waypoint '{}'".format(self.vanPosition.mapLocation, self.waypoints[0])
                else:
                    assert self.waypoints[0] in self.vanPosition.mapLocation, "first waypoint '{}' not an endpoint of vanPosition '{}'".format(self.waypoints[0], self.vanPosition.mapLocation)
                    if self.vanPosition.orientation:
                        pass
            else:
                # if van and rear are on the same edge or node
                if self.vanPosition.getPositionType()==self.rearPosition.getPositionType():
                    assert (self.vanPosition.mapLocation==self.rearPosition.mapLocation) or (set(self.vanPosition.mapLocation)==set(self.rearPosition.mapLocation)), "no waypoints, but vanPosition '{}' and rearPosition '{}' are not the same".format(self.vanPosition.mapLocation, self.rearPosition.mapLocation)
                    if self.vanPosition.getPositionType()=="edge": # both edges
                        if self.vanPosition.orientation==self.rearPosition.orientation: # oriented the same way
                            assert self.vanPosition.distanceToDestination<=self.rearPosition.distanceToDestination, "rearPosition ahead of vanPosition"
                        else: # oriented opposite ways, only valid if "shrinking"
                            assert self.vanPosition.distanceToDestination>(self.rearPosition.getDescription()['distance']-self.rearPosition.distanceToDestination), "rearPosition oriented away from vanPosition"
                elif self.vanPosition.getPositionType()=="node": # van node, rear edge
                    assert self.vanPosition.mapLocation in self.rearPosition.mapLocation, "no waypoints, but vanPosition node '{}' is not part of rearPosition edge '{}'".format(self.vanPosition.mapLocation, self.rearPosition.mapLocation)
                    assert self.rearPosition.orientation==self.vanPosition.mapLocation, "rearPosition not oriented toward vanPosition"
                elif self.rearPosition.getPositionType()=="node": # van edge, rear node
                    assert self.rearPosition.mapLocation in self.vanPosition.mapLocation, "no waypoints, but rearPosition node '{}' is not part of vanPosition edge '{}'".format(self.rearPosition.mapLocation, self.vanPosition.mapLocation)
                    assert self.rearPosition.orientation==(self.vanPosition.mapLocation[0] if self.vanPosition.mapLocation[1]==self.rearPosition.mapLocation else self.vanPosition.mapLocation[1]), "rearPosition not oriented toward vanPosition"
                    assert self.vanPosition.orientation!=self.rearPosition.mapLocation, "vanPosition cannot shrink towards static rearPosition"
        except AssertionError as e:
            raise InvalidPositionError(e)

    def getCurrentLength(self) -> float:
        """Return current extent of column"""
        return self.vanPosition.getDistance(self.rearPosition)
    
    def reverseCourse(self) -> None:
        """Swap van and rear"""
        self.waypoints = [self.waypoints[i] for i in range(len(self.waypoints)-1,-1,-1)] # reverse list
        tempVan = self.rearPosition.copy()
        if tempVan.getPositionType()=="edge":
            try:
                tempVan.reverseCourse()
            except InvalidActionError:
                pass
        else:
            tempVan.setOrientation(None)
        tempRear = self.vanPosition.copy()
        if tempRear.getPositionType()=="edge":
            try:
                tempRear.reverseCourse()
            except InvalidActionError:
                pass
        else:
            if len(self.waypoints)>0:
                tempRear.setOrientation(self.waypoints[-1])
            else:
                tempRear.setOrientation(tempVan.orientation)
        self.vanPosition = tempVan
        self.rearPosition = tempRear

    def setOrientation(self, new_orientation) -> None:
        if new_orientation==self.vanPosition.orientation:
            # new orientation is current orientation
            pass 
        elif new_orientation==self.vanPosition.mapLocation:
            # new orientation is current vanPosition location
            pass
        elif new_orientation==self.rearPosition.mapLocation:
            # new orientation is current rearPosition location
            self.reverseCourse()
        elif new_orientation in self.waypoints:
            # new orientation is an existing waypoint
            self.vanPosition.setOrientation(self.waypoints[0])
            self.rearPosition.setOrientation(self.waypoints[-1])
        elif (self.vanPosition.getPositionType()=="node") and (new_orientation in self.vanPosition.map.neighbors(self.vanPosition.mapLocation)):
            # new orientation is neighbor of vanPosition node
            if (self.rearPosition.getPositionType()=="edge") and (new_orientation in self.rearPosition.mapLocation):
                self.reverseCourse() 
            else:
                self.vanPosition.setOrientation(new_orientation)
        elif (self.rearPosition.getPositionType()=="node") and (new_orientation in self.vanPosition.map.neighbors(self.rearPosition.mapLocation)):
            # new orientation is neighbor of rearPosition node
            self.reverseCourse()
            self.vanPosition.setOrientation(new_orientation)
        elif (self.vanPosition.getPositionType()=="edge") and (new_orientation in self.vanPosition.mapLocation):
            # new orientation is reverse of current vanPosition orientation
            # we already know it's not the current orientation, so reverse course 
            if len(self.waypoints) > 0:
                # if there are waypoints, turn inward to shrink
                self.vanPosition.reverseCourse()
            else:
                # otherwise just reverse column
                self.reverseCourse()
        else:
            raise InvalidActionError("Cannot set orientation of column with vanPosition '{}', rearPosition '{}', and waypoints '{}' to '{}'".format(self.vanPosition.mapLocation, self.rearPosition.mapLocation, self.waypoints, new_orientation))
        self.validate()