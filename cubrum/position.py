import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from typing import Union

from .decisionpoint import DecisionPoint, ArmyGathered, CrossroadsReached, NodeOccupied, StrongholdReached
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
        
    def __repr__(self):
        if self.getPositionType()=="node":
            self_description = "in {}".format(self.mapLocation) 
        else:
            destination = self.orientation 
            origin = self.mapLocation[0] if self.mapLocation[1]==self.orientation else self.mapLocation[1]
            self_description = "{} leagues outside {} on the road from {}".format(self.distanceToDestination, destination, origin)
        return self_description

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
    
    def isSameLocation(self, other:"PointPosition") -> bool:
        """Returns whether two PointPositions are in the same location, regardless of orientation"""
        if self.getPositionType()=="node" and other.getPositionType()=="node":
            if self.mapLocation==other.mapLocation:
                return True 
        if self.getPositionType()=="edge" and other.getPositionType()=="edge":
            if set(self.mapLocation)==set(other.mapLocation):
                if (self.orientation==other.orientation) and (self.distanceToDestination==other.distanceToDestination):
                    return True
                if (self.orientation!=other.orientation) and (round(self.getDescription()['distance']-self.distanceToDestination, 2)==other.distanceToDestination):
                    return True
        return False

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

    def getValidOrientations(self) -> list:
        if self.getPositionType()=="edge":
            return list(self.mapLocation)
        elif self.getPositionType()=="node":
            return list(self.map.neighbors(self.mapLocation))+[self.mapLocation]
        else:
            raise InvalidPositionError("positionType is neither node nor edge")

    def getOrigin(self) -> str:
        if self.getPositionType()=="node":
            return self.mapLocation
        else:
            return self.mapLocation[0] if self.mapLocation[1]==self.orientation else self.mapLocation[1]

    def setOrientation(self, orientation:str) -> None:
        self.validate()
        # assert orientation in self.getValidOrientations(), "valid orientations are {}, got '{}'".format(self.getValidOrientations(), orientation)
        try:
            if self.getPositionType()=="edge":
                assert orientation in self.mapLocation, "node '{}' is not an endpoint of edge '{}'".format(orientation, self.mapLocation)
                if orientation != self.orientation:
                    new_orientation = orientation
                    new_distance_to_destination = round(self.getDescription()['distance'] - self.distanceToDestination, 2)
                else:
                    new_orientation = orientation
                    new_distance_to_destination = self.distanceToDestination
            else:
                if orientation==self.mapLocation:
                    new_orientation = None 
                else:
                    assert (orientation is None) or (orientation in self.map.neighbors(self.mapLocation)), "orientation '{}' is not a neighbor of mapLocation '{}'".format(orientation, self.mapLocation)
                    new_orientation = orientation
                new_distance_to_destination = self.distanceToDestination
        except AssertionError as e:
            raise InvalidActionError(e)
        self.orientation = new_orientation
        if new_distance_to_destination is not None:
            new_distance_to_destination = round(new_distance_to_destination, 2)
        self.distanceToDestination = new_distance_to_destination

    def reverseCourse(self) -> None:
        self.validate()
        if self.getPositionType()=="node":
            raise InvalidActionError("Cannot reverse course while on a node")
        if not self.orientation:
            raise InvalidActionError("Cannot reverse course when orientation is not set")
        new_orientation = self.getOrigin()
        new_distance_to_destination = round(self.getDescription()['distance'] - self.distanceToDestination, 2)
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
                    self.distanceToDestination = round(self.map.edges[self.mapLocation]['distance'] - self.distanceToDestination, 2)
                except AssertionError as e:
                    raise InvalidActionError(e)
            if self.distanceToDestination <= 0:
                self.mapLocation=self.orientation 
                self.orientation = None
                self.distanceToDestination = None
                return None
            if distance >= self.distanceToDestination:
                remaining_movement = round(distance - self.distanceToDestination, 2)
                self.distanceToDestination = 0
                reached_destination = self.map.nodes[self.orientation]
                if reached_destination.get("strongholdType"):
                    return StrongholdReached(strongholdName=reached_destination['name'], remaining_movement=remaining_movement, **reached_destination)
                else:
                    return CrossroadsReached(crossroadsName = reached_destination['name'], remaining_movement=remaining_movement, **reached_destination)
            self.distanceToDestination = round(self.distanceToDestination - distance, 2)
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
            return self.move(distance)
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
            return round(path_length, 2)
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
            return round(distance_choices[0] if (distance_choices[0] < distance_choices[1]) else distance_choices[1], 2)
        elif (self.getPositionType()=="node") and (other.getPositionType()=="edge"): # self node, other edge
            # reverse case already handled, so just switch self and other
            return other.getDistance(self)
        else: # both edges
            if set(self.mapLocation)==set(other.mapLocation): # same-edge case
                if self.orientation==other.orientation: # same edge, pointed the same way
                    return round(abs(other.distanceToDestination-self.distanceToDestination), 2)
                else: # same edge, pointed opposite ways
                    others_distance_to_self_destination = (other.getDescription()["distance"]-other.distanceToDestination)
                    return round(abs(others_distance_to_self_destination-self.distanceToDestination), 2)
            distance_choices = []
            for node_name in self.mapLocation: # iterate over edges
                node_position = PointPosition(node_name, map=self.map)
                node_position.validate()
                distance_to_adjacent_node =  other.getDistance(node_position)
                if node_name==self.orientation:
                    distance_choices.append(distance_to_adjacent_node+self.distanceToDestination)
                else:
                    distance_choices.append(distance_to_adjacent_node+(self.getDescription()['distance'] - self.distanceToDestination))
            return round(distance_choices[0] if (distance_choices[0] < distance_choices[1]) else distance_choices[1], 2)


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
        self.columnLength = (columnLength or self.getCurrentLength())
        self.waypoints = (waypoints or [])
        self.waypoints = list(self.waypoints)

    def __repr__(self):
        van_description = str(self.vanPosition)
        rear_description = str(self.rearPosition)
        if self.getCurrentLength()==0:
            self_description= "column arrayed {}".format(van_description)
        else:
            self_description = "column {} leagues long; van is {}; rear is {})".format(self.getCurrentLength(), van_description, rear_description)
        return self_description

    def validate(self):
        self.vanPosition.validate()
        self.rearPosition.validate()
        try:
            assert self.getCurrentLength() <= self.columnLength, "column length {} greater than maximum length {}".format(self.getCurrentLength(), self.columnLength)
            if len(self.waypoints) > 0: # waypoints
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
            else: # no waypoints
                if self.vanPosition.getPositionType()==self.rearPosition.getPositionType(): # van and rear are on the same edge or node
                    assert (self.vanPosition.mapLocation==self.rearPosition.mapLocation) or (set(self.vanPosition.mapLocation)==set(self.rearPosition.mapLocation)), "no waypoints, but vanPosition '{}' and rearPosition '{}' are not the same".format(self.vanPosition.mapLocation, self.rearPosition.mapLocation)
                    if self.vanPosition.getPositionType()=="edge": # both edges
                        if self.vanPosition.orientation==self.rearPosition.orientation: # oriented the same way
                            assert self.vanPosition.distanceToDestination<=self.rearPosition.distanceToDestination, "rearPosition ahead of vanPosition"
                        else: # oriented opposite ways, only valid if "shrinking"
                            assert self.vanPosition.distanceToDestination>round(self.rearPosition.getDescription()['distance']-self.rearPosition.distanceToDestination, 2), "rearPosition oriented away from vanPosition"
                elif self.vanPosition.getPositionType()=="node": # van node, rear edge
                    assert self.vanPosition.mapLocation in self.rearPosition.mapLocation, "no waypoints, but vanPosition node '{}' is not part of rearPosition edge '{}'".format(self.vanPosition.mapLocation, self.rearPosition.mapLocation)
                    assert self.rearPosition.orientation==self.vanPosition.mapLocation, "rearPosition not oriented toward vanPosition"
                elif self.rearPosition.getPositionType()=="node": # van edge, rear node
                    assert self.rearPosition.mapLocation in self.vanPosition.mapLocation, "no waypoints, but rearPosition node '{}' is not part of vanPosition edge '{}'".format(self.rearPosition.mapLocation, self.vanPosition.mapLocation)
                    assert self.rearPosition.orientation==(self.vanPosition.mapLocation[0] if self.vanPosition.mapLocation[1]==self.rearPosition.mapLocation else self.vanPosition.mapLocation[1]), "rearPosition not oriented toward vanPosition"
                    assert self.vanPosition.orientation!=self.rearPosition.mapLocation, "vanPosition cannot shrink towards static rearPosition"
        except AssertionError as e:
            raise InvalidPositionError(e)

    def isSameLocation(self, other:"ColumnPosition") -> bool:
        """Returns whether two ColumnPositions are in exactly the same location, regardless of disposition"""
        if (self.vanPosition.isSameLocation(other.vanPosition)) and (self.rearPosition.isSameLocation(other.rearPosition)):
            return True 
        if (self.vanPosition.isSameLocation(other.rearPosition)) and (self.rearPosition.isSameLocation(other.vanPosition)):
            return True 
        return False

    def getCurrentLength(self) -> float:
        """Return current extent of column"""
        return round(self.vanPosition.getDistance(self.rearPosition), 2)

    def getValidOrientations(self) -> list:
        valid_orientations = [waypoint for waypoint in self.waypoints]
        valid_orientations += self.vanPosition.getValidOrientations()
        valid_orientations += self.rearPosition.getValidOrientations()
        return list(set(valid_orientations))

    def getMotion(self, gather_at_gates:bool=False) -> str:
        """Returns one of [holding, gathering, regrouping, entering, marching]"""
        self.validate()
        if (self.getCurrentLength()==0) and (self.vanPosition.orientation is None):
            return "holding"
        if len(self.waypoints) > 0:
            if self.vanPosition.orientation==self.waypoints[0]:
                return "regrouping"
        if self.vanPosition.orientation is None:
            return "entering"
        if (self.vanPosition.distanceToDestination==0) and gather_at_gates:
            return "gathering"
        else:
            return "marching"

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
            tempVan.setOrientation(tempVan.mapLocation)
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
        
    def getOrientation(self, gather_at_gates:bool=False) -> str:
        self.validate()
        if self.getMotion(gather_at_gates) in ["marching", "gathering"]:
            return self.vanPosition.orientation
        elif self.getMotion(gather_at_gates) in ["holding", "entering"]:
            return self.vanPosition.mapLocation
        elif self.getMotion(gather_at_gates)=="regrouping":
            if len(self.waypoints)<1:
                raise InvalidPositionError("regrouping without waypoints")
            return self.waypoints[0]
        else:
            raise InvalidPositionError("invalid value '{}' returned from getMotion()".format(self.getMotion()))

    def setOrientation(self, new_orientation) -> None:
        assert new_orientation in self.getValidOrientations(), "valid orientations are {}, got '{}'".format(self.getValidOrientations(), new_orientation)
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

    def reform(self, maxLength:float=None) -> None:
        if maxLength is None:
            maxLength = self.columnLength
        if self.vanPosition.getPositionType()=="node" and self.rearPosition.getPositionType()=="node":
            if self.vanPosition.mapLocation!= self.rearPosition.mapLocation:
                self.rearPosition.move(0.015) # move out about 100 yards so we don't have van and rear in different nodes
        overstretch = round(self.getCurrentLength() - maxLength, 2)
        if overstretch <=0:
            return
        iteration = 0
        while overstretch > 0:
            iteration += 1
            log.debug("iteration {} of reforming, overstretch={}".format(iteration, overstretch))
            arrived_somewhere = self.rearPosition.move(overstretch)
            new_overstretch = round(self.getCurrentLength() - maxLength, 2)
            if new_overstretch >= overstretch:
                return InvalidPositionError("attempting to reform is making overstretch worse")
            overstretch = new_overstretch
            if arrived_somewhere:
                if arrived_somewhere.name==self.vanPosition.mapLocation:
                    log.debug("rearPosition has arrived at vanPosition")
                    self.rearPosition.move(1) # enter the stronghold
                    return
                elif arrived_somewhere.name in self.waypoints:
                    assert arrived_somewhere.name == self.waypoints[-1], "rearPosition has bypassed last waypoint somehow, waypoints={} but arrived at {}".format(self.waypoints, arrived_somewhere.name)
                    if arrived_somewhere.name==self.vanPosition.orientation:
                        log.debug("rearPosition has arrived at node to which column is shrinking, entering and reversing course")
                        self.waypoints = []
                        self.rearPosition.move(1)
                        self.reverseCourse()
                        continue
                    elif len(self.waypoints)>1:
                        self.rearPosition.move(1) # enter waypoint
                        self.waypoints = self.waypoints[:-1] # remove waypoint
                        self.rearPosition.setOrientation(self.waypoints[-1])
                        self.rearPosition.move(0.015) # move out about 100 yards so we don't have van and rear in different nodes
                        continue
                    else:
                        # vanPosition is at most one edge away
                        self.waypoints = []
                        if self.vanPosition.getPositionType()=="node":
                            self.rearPosition.move(1) # enter node
                            self.rearPosition.setOrientation(self.vanPosition.mapLocation)
                            self.rearPosition.move(0.015) # move out about 100 yards so we don't have van and rear in different nodes
                        else:
                            self.rearPosition.move(1) # enter node
                            for potential_orientation in self.rearPosition.getValidOrientations():
                                if potential_orientation in self.vanPosition.mapLocation:
                                    self.rearPosition.setOrientation(potential_orientation)
                                    self.rearPosition.move(0.015) # move out about 100 yards so we don't have van and rear in different nodes
                                    break
                            else:
                                raise InvalidPositionError("no waypoints, and valid orientations for rearPosition are {}, none of which matches vanPosition {}".format(self.rearPosition.getValidOrientations(), self.vanPosition.mapLocation))
                else:
                    raise InvalidPositionError("rearPosition has arrived at {} which is not in waypoints {}".format(arrived_somewhere.name, self.waypoints))
            else:
                pass

    def move(self, distance:float, gather_at_gates:bool=False) -> DecisionPoint:
        if self.getMotion(gather_at_gates)=="marching": # marching forward normally
            if self.vanPosition.getPositionType()=="node":
                if self.rearPosition.mapLocation==self.vanPosition.mapLocation:
                    self.rearPosition.setOrientation(self.vanPosition.orientation)
                else:
                    self.waypoints = [self.vanPosition.mapLocation] + self.waypoints
                response = self.vanPosition.move(distance)
                self.reform()
                return response
            else:
                response = self.vanPosition.move(distance)
                self.reform()
                return response
        elif self.getMotion(gather_at_gates)=="gathering": # accumulating on doorstep of node 
            if distance >= self.getCurrentLength():
                self.rearPosition.mapLocation=self.vanPosition.mapLocation
                self.rearPosition.orientation=self.vanPosition.orientation
                self.rearPosition.distanceToDestination=self.vanPosition.distanceToDestination=0
                return ArmyGathered(self.vanPosition.orientation, self.vanPosition.getOrigin(), **PointPosition(self.vanPosition.orientation, map=self.vanPosition.map).getDescription())
            else:
                while distance > 0:
                    response = self.rearPosition.move(distance)
                    if response:
                        if response.trigger in ["StrongholdReached", "CrossroadsReached"]:
                            if response.name==self.vanPosition.orientation:
                                return ArmyGathered(self.vanPosition.orientation, self.vanPosition.getOrigin(), **PointPosition(self.vanPosition.orientation, map=self.vanPosition.map).getDescription())
                            elif response.name==self.waypoints[-1]:
                                self.waypoints = self.waypoints[:-1]
                                if len(self.waypoints)>1:
                                    rear_new_destination = self.waypoints[-1]
                                else:
                                    rear_new_destination = self.vanPosition.mapLocation
                                self.rearPosition.mapLocation=(rear_new_destination, response.name)
                                self.rearPosition.setOrientation(rear_new_destination)
                                self.rearPosition.distanceToDestination = self.rearPosition.getDescription()['distance']
                                distance = response.remaining_movement
                            else:
                                raise InvalidPositionError("rearPosition reached node '{}', which is not vanPosition orientation '{}' or in waypoints {}".format(response.name, self.vanPosition.orientation, self.waypoints))
                        else:
                            return response 
                    else:
                        return
        elif self.getMotion(gather_at_gates)=="entering": # van already in node, remainder joining them
            if distance >= self.getCurrentLength():
                self.rearPosition.mapLocation=self.vanPosition.mapLocation
                self.rearPosition.orientation=None 
                self.rearPosition.distanceToDestination = None 
                return NodeOccupied(nodeName=self.vanPosition.getDescription()['name'], **self.vanPosition.getDescription()) 
            else:
                while distance > 0:
                    response = self.rearPosition.move(distance)
                    if response:
                        if response.trigger in ["StrongholdReached", "CrossroadsReached"]:
                            if response.name==self.vanPosition.mapLocation:
                                self.rearPosition.move(1) # enter 
                                return NodeOccupied(nodeName=self.vanPosition.getDescription()['name'], **self.vanPosition.getDescription()) 
                            elif response.name==self.waypoints[-1]:
                                self.waypoints = self.waypoints[:-1]
                                if len(self.waypoints)>1:
                                    rear_new_destination = self.waypoints[-1]
                                else:
                                    rear_new_destination = self.vanPosition.mapLocation
                                self.rearPosition.mapLocation=(rear_new_destination, response.name)
                                self.rearPosition.setOrientation(rear_new_destination)
                                self.rearPosition.distanceToDestination = self.rearPosition.getDescription()['distance']
                                distance = response.remaining_movement
                            else:
                                raise InvalidPositionError("rearPosition reached node '{}', which is not vanPosition '{}' or in waypoints {}".format(response.name, self.vanPosition.mapLocation, self.waypoints))
                        else:
                            return response 
                    else:
                        return
        elif self.getMotion(gather_at_gates)=="regrouping": # both van and rear pulling in to waypoint
            if distance >= self.getCurrentLength():
                self.vanPosition.mapLocation=self.waypoints[0]
                self.vanPosition.orientation=None
                self.vanPosition.distanceToDestination=None
                self.rearPosition.mapLocation=self.waypoints[0]
                self.rearPosition.orientation=None
                self.rearPosition.distanceToDestination=None
                self.waypoints=[]
                return NodeOccupied(nodeName=self.vanPosition.getDescription()['name'], **self.vanPosition.getDescription()) 
            else: # vanPosition oriented toward first waypoint
                response = self.vanPosition.move(distance)
                if response:
                    assert response.name==self.waypoints[0], "vanPosition regrouping to first waypoint but arrived at '{}' when waypoints are {}".format(response.name, self.waypoints)
                    self.vanPosition.move(1) # enter waypoint
                    self.waypoints= self.waypoints[1:]
                    remaining_movement = response.remaining_movement
                    if remaining_movement:
                        self.move(remaining_movement, gather_at_gates)
                    else:
                        return
                else:
                    return
        else:
            # raise InvalidActionError("cannot move while holding position, define an orientation")
            return NodeOccupied(nodeName=self.vanPosition.mapLocation, **self.vanPosition.getDescription())
   
    def getValidBypasses(self) -> list:
        if (self.vanPosition.distanceToDestination is None) or (self.vanPosition.distanceToDestination>0):
            return []
        else:
            return [n for n in self.vanPosition.map.neighbors(self.vanPosition.orientation) if n!= self.vanPosition.getOrigin()]

    def bypassTo(self, bypass_name) -> None:
        assert bypass_name in self.getValidBypasses(), "valid bypasses are {}, got '{}'".format(self.getValidBypasses(), bypass_name)
        self.waypoints = [self.vanPosition.orientation] + self.waypoints
        self.vanPosition.mapLocation=(bypass_name, self.vanPosition.orientation)
        self.vanPosition.setOrientation(bypass_name)
        self.vanPosition.distanceToDestination=self.vanPosition.getDescription()['distance']
        self.reform()
        
    def containsPoint(self, other:PointPosition) -> bool:
        """Whether the column contains a given PointPosition"""
        if other.getPositionType()=="node":
            if other.mapLocation in [self.vanPosition.mapLocation, self.rearPosition.mapLocation] + self.waypoints:
                return True 
        else:
            # if self.vanPosition.getDistance(other) < self.vanPosition.getDistance(self.rearPosition):
            #     if self.rearPosition.getDistance(other) < self.rearPosition.getDistance(self.vanPosition):
            #         return True
            if (self.vanPosition.getPositionType()=="edge") and (set(other.mapLocation)==set(self.vanPosition.mapLocation))and (set(other.mapLocation)==set(self.rearPosition.mapLocation)):
                if other.orientation==self.vanPosition.orientation:
                    if (other.distanceToDestination >= self.vanPosition.distanceToDestination) and (other.distanceToDestination <= self.rearPosition.distanceToDestination):
                        return True
                else:
                    if (round(other.getDescription()['distance']-other.distanceToDestination, 2) >= self.vanPosition.distanceToDestination) and (round(other.getDescription()['distance']-other.distanceToDestination, 2) <= self.rearPosition.distanceToDestination):
                        return True
            elif (self.vanPosition.getPositionType()=="edge") and (set(other.mapLocation)==set(self.vanPosition.mapLocation)): # on vanPosition's edge
                if (len(self.waypoints)==0 or (self.vanPosition.orientation!=self.waypoints[0])): # not shrinking
                    # check if it falls in the same part of the edge
                    if other.orientation==self.vanPosition.orientation:
                        if other.distanceToDestination >= self.vanPosition.distanceToDestination:
                            return True
                    else: # facing opposite directons
                        if round(other.getDescription()['distance']-other.distanceToDestination, 2) >= self.vanPosition.distanceToDestination:
                            return True
                else: # shrinking
                    # check if it falls in the same part of the edge
                    if other.orientation==self.vanPosition.orientation:
                        if other.distanceToDestination <= self.vanPosition.distanceToDestination:
                            return True
                    else: # facing opposite directons
                        if round(other.getDescription()['distance']-other.distanceToDestination, 2) <= self.vanPosition.distanceToDestination:
                            return True
            elif (self.rearPosition.getPositionType()=="edge") and (set(other.mapLocation)==set(self.rearPosition.mapLocation)): # on rearPosition's edge
                # check if it falls in the same part of the edge
                if other.orientation==self.rearPosition.orientation:
                    if other.distanceToDestination <= self.rearPosition.distanceToDestination:
                        return True
                else: # facing opposite directions
                    if round(other.getDescription()['distance']-other.distanceToDestination, 2) <= self.rearPosition.distanceToDestination:
                        return True
            if len(self.waypoints)>1:
                for i in range(1, len(self.waypoints)):
                    if set(other.mapLocation)==set((self.waypoints[i-1], self.waypoints[i])):
                        return True
        return False
        
    def intersectsColumn(self, other:"ColumnPosition") -> bool:
        """Whether the column overlaps at all with another column"""
        if (self.containsPoint(other.vanPosition)) or (self.containsPoint(other.rearPosition)):
            return True
        for waypoint in self.waypoints:
            if (waypoint in other.waypoints) or (waypoint==other.vanPosition.mapLocation) or (waypoint==other.rearPosition.mapLocation):
                return True
        for waypoint in other.waypoints:
            if (waypoint in self.waypoints) or (waypoint==self.vanPosition.mapLocation) or (waypoint==self.rearPosition.mapLocation):
                return True
        return False
    
    def touchingColumn(self, other:"ColumnPosition") -> bool:
        """Returns whether columns touching endpoints but not overlapping"""
        if self.isSameLocation(other):
            if self.vanPosition.isSameLocation(self.rearPosition):
                return True
            else: # self and other overlapping 
                return False
        elif self.vanPosition.isSameLocation(other.vanPosition):
            if (self.containsPoint(other.rearPosition)) and (not other.rearPosition.isSameLocation(other.vanPosition)):
                return False 
            if (other.containsPoint(self.rearPosition)) and (not self.rearPosition.isSameLocation(self.vanPosition)):
                return False 
            return True
        elif self.vanPosition.isSameLocation(other.rearPosition):
            if (self.containsPoint(other.vanPosition)) and (not other.rearPosition.isSameLocation(other.vanPosition)):
                return False 
            if (other.containsPoint(self.rearPosition)) and (not self.rearPosition.isSameLocation(self.vanPosition)):
                return False 
            return True
        elif self.rearPosition.isSameLocation(other.vanPosition):
            if (self.containsPoint(other.rearPosition)) and (not other.rearPosition.isSameLocation(other.vanPosition)):
                return False 
            if (other.containsPoint(self.vanPosition)) and (not self.rearPosition.isSameLocation(self.vanPosition)):
                return False 
            return True
        elif self.rearPosition.isSameLocation(other.rearPosition):
            if (self.containsPoint(other.vanPosition)) and (not other.rearPosition.isSameLocation(other.vanPosition)):
                return False 
            if (other.containsPoint(self.vanPosition)) and (not self.rearPosition.isSameLocation(self.vanPosition)):
                return False 
            return True
        elif self.vanPosition.orientation in [other.vanPosition.mapLocation, other.rearPosition.mapLocation]+other.waypoints:
            if self.vanPosition.distanceToDestination==0:
                return True 
        elif other.vanPosition.orientation in [self.vanPosition.mapLocation, self.rearPosition.mapLocation]+self.waypoints:
            if other.vanPosition.distanceToDestination==0:
                return True 
        return False

    def getDistance(self, other:"ColumnPosition") -> float:
        if self.touchingColumn(other):
            return 0
        if self.intersectsColumn(other):
            return -1
        min_distance = None
        for self_position in [self.vanPosition, self.rearPosition] + [PointPosition(wp, map=self.map) for wp in self.waypoints]:
            for other_position in [other.vanPosition, other.rearPosition] + [PointPosition(wp, map=other.map) for wp in other.waypoints]:
                pair_distance = self_position.getDistance(other_position)    
                if (min_distance is None) or (pair_distance < min_distance):
                    min_distance = pair_distance
        return round(min_distance, 2)
    
    def deconflictFrom(self, other:"ColumnPosition") -> None:
        if not self.intersectsColumn(other):
            raise InvalidActionError("cannot deconflict non-intersecting ColumnPositions")
        elif self.isSameLocation(other): # perfect overlap 
            if self.getMotion()!="holding": # self has an orientation
                if self.vanPosition.getPositionType()=="node":
                    self.move(distance=0.01)
                    self.reform(maxLength=0)
                    self.reverseCourse()
                    self.move(self.vanPosition.distanceToDestination)
                else:
                    self.vanPosition=other.vanPosition.copy()
                    self.rearPosition=other.rearPosition.copy()
                    self.reform(maxLength=0)
                    self.reverseCourse()
            else: # shared node, no orientation
                if other.getMotion()!="holding": # try to grab orientation from other
                    return other.deconflictFrom(self)
                else: # admit defeat
                    raise InvalidPositionError("failed to deconflict, ColumnPositions share a node but no orientation set")
        elif self.containsPoint(other.vanPosition) and self.containsPoint(other.rearPosition): # self fully contains other
            self.reform(maxLength=0)
            self.reverseCourse()
            self.move(distance=self.getDistance(other))
        elif other.containsPoint(self.vanPosition) and (other.containsPoint(self.rearPosition)): # other fully contains self
            other.deconflictFrom(self) 
        elif other.containsPoint(self.vanPosition): # only van is within other 
            self.reverseCourse()
            self.reform(maxLength=0)
            self.reverseCourse()
            self.move(distance=self.getDistance(other)) 
        elif other.containsPoint(self.rearPosition): # only rear is within other 
            self.reform(maxLength=0)
            self.reverseCourse()
            self.move(distance=self.getDistance(other))