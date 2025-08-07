import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np

import cubrum.position
import cubrum.map 

COPPERCOAST_NODES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cubrum", "mapdata", "coppercoast_strongholds.json")
COPPERCOAST_ROADS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cubrum", "mapdata", "coppercoast_roads.json")

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