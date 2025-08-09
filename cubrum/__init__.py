import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from . import position, map

COPPERCOAST_NODES_PATH = os.path.join(os.path.dirname(__file__), "mapdata", "coppercoast_strongholds.json")
COPPERCOAST_ROADS_PATH = os.path.join(os.path.dirname(__file__), "mapdata", "coppercoast_roads.json")

def initializeColumn(stronghold_name:str, column_length:float=0.3) -> position.ColumnPosition:
    assert os.path.exists(COPPERCOAST_NODES_PATH)
    assert os.path.exists(COPPERCOAST_ROADS_PATH)
    coppercoast = map.Map()
    coppercoast.addNodesFromFile(COPPERCOAST_NODES_PATH)
    coppercoast.addEdgesFromFile(COPPERCOAST_ROADS_PATH)
    assert stronghold_name in coppercoast.nodes
    van_position = position.PointPosition(stronghold_name, map=coppercoast)
    rear_position = position.PointPosition(stronghold_name, map=coppercoast)
    column_position = position.ColumnPosition(vanPosition=van_position, rearPosition=rear_position, columnLength=column_length)
    return column_position


