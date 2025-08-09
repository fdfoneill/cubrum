import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from . import map, army, formation, commander

COPPERCOAST_NODES_PATH = os.path.join(os.path.dirname(__file__), "mapdata", "coppercoast_strongholds.json")
COPPERCOAST_ROADS_PATH = os.path.join(os.path.dirname(__file__), "mapdata", "coppercoast_roads.json")

def initializeArmy(starting_stronghold:str=None, formations:list=None) -> army.Army:
    assert os.path.exists(COPPERCOAST_NODES_PATH)
    assert os.path.exists(COPPERCOAST_ROADS_PATH)
    coppercoast = map.Map()
    coppercoast.addNodesFromFile(COPPERCOAST_NODES_PATH)
    coppercoast.addEdgesFromFile(COPPERCOAST_ROADS_PATH)
    starting_stronghold=starting_stronghold or "Yinnagul"
    assert starting_stronghold in coppercoast.nodes
    cavalry = formation.Formation(name="1st Yinnagul Light Cavalry", warriorCount=200, wagonCount=0, cavalry=True)
    recon_force = army.Army(name="Yinnagul Reconnaisance Force", formations=(formations or [cavalry]), commander=commander.Commander(), supply=cavalry.getSupplyCapacity(), startingStronghold=starting_stronghold,map=coppercoast)
    return recon_force
    
    


