import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import sys, unittest
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np

import cubrum.position
import cubrum.map 
from cubrum.exceptions import InvalidPositionError

COPPERCOAST_NODES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cubrum", "mapdata", "coppercoast_strongholds.json")
COPPERCOAST_ROADS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cubrum", "mapdata", "coppercoast_roads.json")


class TestPointPosition(unittest.TestCase):
    def setUp(self):
        self.roads = cubrum.map.Map()
        self.roads.addNodesFromFile(COPPERCOAST_NODES_PATH)
        self.roads.addEdgesFromFile(COPPERCOAST_ROADS_PATH)

    def testGetDistanceTwoPoints(self):
        position_orbost = cubrum.position.PointPosition("Orbost", map=self.roads)
        position_ulgis = cubrum.position.PointPosition("Ulgis", map=self.roads)
        distance_expected = 4
        distance_ou = position_orbost.getDistance(position_ulgis)
        self.assertEqual(distance_expected, distance_ou)
        distance_uo = position_ulgis.getDistance(position_orbost)
        self.assertEqual(distance_expected, distance_uo)

    def testGetDistancePointEdge(self):
        position_point = cubrum.position.PointPosition("Bemm", map=self.roads)
        position_edge = cubrum.position.PointPosition(("The Sapphire Dome", "Lugana"), orientation="Lugana", distanceToDestination=2, map=self.roads)
        distance_expected = 10
        distance_pe = position_point.getDistance(position_edge)
        self.assertEqual(distance_expected, distance_pe)
        distance_ep = position_edge.getDistance(position_point)
        self.assertEqual(distance_expected, distance_ep)

    def testGetDistanceDifferentEdges(self):
        position_edge1 = cubrum.position.PointPosition(("Oughan Keep", "Joukra"), orientation="Oughan Keep", distanceToDestination=1, map=self.roads)
        position_edge2 = cubrum.position.PointPosition(("Oughan Keep", "Smara"), orientation="Oughan Keep", distanceToDestination=1, map=self.roads)
        distance_expected = 2
        distance_12 = position_edge1.getDistance(position_edge2)
        self.assertEqual(distance_expected, distance_12)
        distance_21 = position_edge2.getDistance(position_edge1)
        self.assertEqual(distance_expected, distance_21)

    def testGetDistanceSameEdge(self):
        position_edge1 = cubrum.position.PointPosition(("Oughan Keep", "Smara"), orientation="Oughan Keep", distanceToDestination=2, map=self.roads)
        position_edge2 = cubrum.position.PointPosition(("Oughan Keep", "Smara"), orientation="Oughan Keep", distanceToDestination=1, map=self.roads)
        distance_expected = 1
        distance_12 = position_edge1.getDistance(position_edge2)
        self.assertEqual(distance_expected, distance_12)
        distance_21 = position_edge2.getDistance(position_edge1)
        self.assertEqual(distance_expected, distance_21)


class TestColumnPosition(unittest.TestCase):
    def setUp(self):
        self.roads = cubrum.map.Map()
        self.roads.addNodesFromFile(COPPERCOAST_NODES_PATH)
        self.roads.addEdgesFromFile(COPPERCOAST_ROADS_PATH)

    def testStaticNode(self):
        van_position = cubrum.position.PointPosition("Orbost", map=self.roads)
        rear_position = cubrum.position.PointPosition("Orbost", map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e
        
    def testTravelingNode(self):
        van_position = cubrum.position.PointPosition("Orbost", orientation="Ulgis", map=self.roads)
        rear_position = cubrum.position.PointPosition("Orbost", orientation="Ulgis", map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e

    def testTravelingEdge(self):
        van_position = cubrum.position.PointPosition(("Orbost", "Ulgis"), orientation="Ulgis", distanceToDestination=0.5, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Ulgis", "Orbost"), orientation="Ulgis", distanceToDestination=0.6, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e
        
    def testShrinkingNoWaypoints(self):
        van_position = cubrum.position.PointPosition(("Lugana", "Kuragang"), orientation="Lugana", distanceToDestination=6, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Lugana", "Kuragang"), orientation="Kuragang", distanceToDestination=6.1, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e
        
    def testTravelingOneWayPoint(self):
        van_position = cubrum.position.PointPosition(("Brick Bridge", "Kuragang"), orientation="Brick Bridge", distanceToDestination=1.9, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Lugana", "Kuragang"), orientation="Kuragang", distanceToDestination=0.05, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, waypoints=["Kuragang"], columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e
        
    def testShrinkingOneWayPoint(self):
        van_position = cubrum.position.PointPosition(("Brick Bridge", "Kuragang"), orientation="Kuragang", distanceToDestination=0.1, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Lugana", "Kuragang"), orientation="Kuragang", distanceToDestination=0.05, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, waypoints=["Kuragang"], columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e
        
    def testTravelingTwoWayPoints(self):
        van_position = cubrum.position.PointPosition(("Neruga's Gate", "Nkaa"), orientation="Neruga's Gate", distanceToDestination=7, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Purann", "Sultan's Rock"), orientation="Sultan's Rock", distanceToDestination=1, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, waypoints=["Nkaa", "Sultan's Rock"], columnLength=5)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e

    def testReverseCourseNoWaypoints(self):
        van_position = cubrum.position.PointPosition(("Orbost", "Ulgis"), orientation="Ulgis", distanceToDestination=0.5, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Ulgis", "Orbost"), orientation="Ulgis", distanceToDestination=0.6, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise InvalidPositionError("Failed before course reversal: {}".format(e))
        column_position.reverseCourse()
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e
        
    def testReverseCourseTwoWaypoints(self):
        van_position = cubrum.position.PointPosition(("Neruga's Gate", "Nkaa"), orientation="Neruga's Gate", distanceToDestination=7, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Purann", "Sultan's Rock"), orientation="Sultan's Rock", distanceToDestination=1, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, waypoints=["Nkaa", "Sultan's Rock"], columnLength=5)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise InvalidPositionError("Failed before course reversal: {}".format(e))
        column_position.reverseCourse()
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise e
        
    def testSetOrientationOneEdge(self):
        van_position = cubrum.position.PointPosition(("Orbost", "Ulgis"), orientation="Ulgis", distanceToDestination=0.5, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Ulgis", "Orbost"), orientation="Ulgis", distanceToDestination=0.6, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise InvalidPositionError("Failed before course change: {}".format(e))
        column_length_before_course_change = column_position.getCurrentLength()
        column_position.setOrientation("Orbost")
        try:
            column_position.validate()
            self.assertEqual(column_position.vanPosition.orientation, "Orbost")
            np.testing.assert_allclose(column_length_before_course_change, column_position.getCurrentLength())
        except InvalidPositionError as e:
            raise e
        
    def testSetOrientationNodeEdge(self):
        van_position = cubrum.position.PointPosition("Ulgis", map=self.roads)
        rear_position = cubrum.position.PointPosition(("Ulgis", "Orbost"), orientation="Ulgis", distanceToDestination=0.1, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=0.2)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise InvalidPositionError("Failed before course change: {}".format(e))
        column_length_before_course_change = column_position.getCurrentLength()
        column_position.setOrientation("Orbost")
        try:
            column_position.validate()
            self.assertEqual(column_position.vanPosition.orientation, "Orbost")
            self.assertEqual(column_position.rearPosition.mapLocation, "Ulgis")
            np.testing.assert_allclose(column_length_before_course_change, column_position.getCurrentLength())
        except InvalidPositionError as e:
            raise e
        
    def testSetOrientationWayPoints(self):
        van_position = cubrum.position.PointPosition(("Ulgis", "Orbost"), orientation="Orbost", distanceToDestination=3, map=self.roads)
        rear_position = cubrum.position.PointPosition(("Ulgis", "Nabiac"), orientation="Ulgis", distanceToDestination=1, map=self.roads)
        column_position = cubrum.position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, waypoints=["Ulgis"], columnLength=4)
        try:
            column_position.validate()
            self.assertTrue(True)
        except InvalidPositionError as e:
            raise InvalidPositionError("Failed before course change: {}".format(e))
        column_length_before_course_change = column_position.getCurrentLength()
        column_position.setOrientation("Ulgis")
        try:
            column_position.validate()
            self.assertEqual(set(column_position.vanPosition.mapLocation), set(("Ulgis","Orbost")))
            self.assertEqual(set(column_position.rearPosition.mapLocation), set(("Ulgis","Nabiac")))
            self.assertEqual(column_position.vanPosition.orientation, "Ulgis")
            self.assertEqual(column_position.rearPosition.orientation, "Ulgis")
            np.testing.assert_allclose(column_length_before_course_change, column_position.getCurrentLength())
        except InvalidPositionError as e:
            raise e

def main():
    log.info("Creating map")
    roads = cubrum.map.Map()
    roads.addNodesFromFile(COPPERCOAST_NODES_PATH)
    roads.addEdgesFromFile(COPPERCOAST_ROADS_PATH)

    log.info("Creating position")
    p = cubrum.position.PointPosition("Orbost", map=roads)
    speed = 1/8

    # log.info("Day 1, 0900: starting in {}".format(p.mapLocation))
    last_destination = p.mapLocation
    day = 0
    while day < 14:
        day += 1
        hour = 6
        while hour < 20:
            hour += 1
            if p.getPositionType()=="node":
                if p.getDescription().get("strongholdType"):
                    if hour >=15:
                        log.info("Spending the rest of the day in {}".format(p.mapLocation))
                        day+=1
                        hour = 6
                        continue
                    # else:
                    #     log.info("Day {}, {}: setting out from {}".format(day, str(hour*100).zfill(4), p.mapLocation))
                elif hour >= 20:
                    log.info("Bedding down on the road")
                    continue
                neighbors = [n for n in roads.neighbors(p.mapLocation) if n != last_destination]
                if len(neighbors)<1:
                    log.info("Dead end, turning back to {}".format(last_destination))
                    p.orientation = last_destination
                else:
                    new_destination = neighbors[np.random.randint(0, len(neighbors))]
                    # log.info("New destination: {}".format(new_destination))
                    log.info("Day {}, {}: setting out from {} toward {}".format(day, str(hour*100).zfill(4), p.mapLocation, new_destination))
                    last_destination = p.orientation 
                    p.setOrientation(new_destination)
            res = p.move(speed)
            if res:
                if res.trigger == "CrossroadsReached":
                    event_description = "reached {}"
                elif res.trigger == "StrongholdReached":
                    event_description = "reached {} of {}, currently held by {}".format(res.strongholdType, res.strongholdName, res.heldBy)
                else:
                    event_description = str(res)
                log.info("Day {}, {}: {}".format(day, str(hour*100).zfill(4), event_description))
    log.info("Day {}, {}: journey ended".format(day, str(hour*100).zfill(4)))


if __name__ == "__main__":
    main()