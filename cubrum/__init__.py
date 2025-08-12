import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from . import gamestate, map, army, formation, commander, culture

COPPERCOAST_NODES_PATH = os.path.join(os.path.dirname(__file__), "mapdata", "coppercoast_strongholds.json")
COPPERCOAST_ROADS_PATH = os.path.join(os.path.dirname(__file__), "mapdata", "coppercoast_roads.json")

def getStartingState() -> gamestate.GameState:
    assert os.path.exists(COPPERCOAST_NODES_PATH)
    assert os.path.exists(COPPERCOAST_ROADS_PATH)
    coppercoast = map.Map()
    coppercoast.addNodesFromFile(COPPERCOAST_NODES_PATH)
    coppercoast.addEdgesFromFile(COPPERCOAST_ROADS_PATH)

    state = gamestate.GameState(coppercoast, "1410-05-20")

    # Allakia
    cmdr_giubrin = commander.Commander(name="Giubrin",age=31,title="Prince", culture=culture.ALLAKIAN, commanderTraits=["Beloved","Crusader","Spartan"])
    cmdr_giubrin.id = state.addPlayer(str(cmdr_giubrin))
    army_allakian_expeditionary = army.Army(
        name="Allakian Expeditionary Force", 
        allegience="Allakia", 
        formations=[
            formation.Formation(name="The Laugher's Privateers", warriorCount=400, wagonCount=0, special="Corsairs"),
            formation.Formation(name="Captain Golin's Freebooters", warriorCount=400, wagonCount=0, special="Corsairs"),
            formation.Formation("1st Port Yarbalk Infantry", warriorCount=600, wagonCount=40),
            formation.Formation("2nd Port Yarbalk Infantry", warriorCount=500, wagonCount=20),
            formation.Formation("1st Traffra Heavy Infantry", warriorCount=500, wagonCount=40, heavy=True),
            formation.Formation("2nd Traffra Heavy Infantry", warriorCount=400, wagonCount=35, heavy=True),
            formation.Formation("3rd Traffra Infantry", warriorCount=400, wagonCount=20),

            formation.Formation("1st Highhold Caprites", warriorCount=200, wagonCount=0, cavalry=True, special="Goat-riders"),
            formation.Formation("1st Traffra Heavy Cavalry", warriorCount=225, wagonCount=0, cavalry=True, heavy=True),
            formation.Formation("2nd Traffra Cavalry", warriorCount=200, wagonCount=0, cavalry=True),
            formation.Formation("1st Port Yarbalk Heavy Cavalry", warriorCount=150, wagonCount=0, cavalry=True, heavy=True)
        ], 
        commander=cmdr_giubrin, 
        supply=0, 
        startingStronghold="Traffra",
        map=coppercoast
    )
    army_allakian_expeditionary.supply = army_allakian_expeditionary.getSupplyCapacity()
    state.addArmy(army_allakian_expeditionary)

    # Boonan
    cmdr_soolabab = commander.Commander(name="Soolabab", age=48, title="High Marshall", culture=culture.BOONAN, commanderTraits=["Defensive Engineer", "Poet", "Stubborn", "Veteran"])
    cmdr_soolabab.id = state.addPlayer(str(cmdr_soolabab))
    army_boonan_levy = army.Army(
        name="Boonan General Levy",
        allegience="Boonan",
        formations=[
            formation.Formation("1st Jerboon Men-at-Arms", warriorCount=800, wagonCount=70, heavy=True),
            formation.Formation("2nd Jerboon Volunteers", warriorCount=700, wagonCount=40),
            formation.Formation("3rd Jerboon Half-Trolls", warriorCount=600, wagonCount=40, heavy=True, special="Half-trolls"),
            formation.Formation("4th Jerboon Volunteers", warriorCount=800, wagonCount=10),
            formation.Formation("5th Jerboon Volunteers", warriorCount=600, wagonCount=15),
            formation.Formation("1st Bemm Men-at-Arms", warriorCount=700, wagonCount=60, heavy=True),
            formation.Formation("2nd Bemm Half-Trolls", warriorCount=500, wagonCount=40, heavy=True, special="Half-trolls"),
            formation.Formation("3rd Bemm Volunteers", warriorCount=600, wagonCount=30),
            formation.Formation("1st Cua Rangers", warriorCount=400, wagonCount=0, special="Mountain men"),
            formation.Formation("1st Sandpass Rangers", warriorCount=400, wagonCount=0, special="Mountain men"),
            formation.Formation("1st Merewey Volunteers", warriorCount=600, wagonCount=10),
            formation.Formation("1st Lebooni Volunteers", warriorCount=500, wagonCount=20),

            formation.Formation("1st Jerboon Heavy Cavalry", warriorCount=300, wagonCount=0, cavalry=True, heavy=True),
            formation.Formation("2nd Jerboon Cavalry", warriorCount=400, wagonCount=0, cavalry=True),
            formation.Formation("1st Bemm Cavalry", warriorCount=275, wagonCount=0, cavalry=True),
            formation.Formation("2nd Bemm Heavy Cavalry", warriorCount=200, wagonCount=0, cavalry=True, heavy=True),
            formation.Formation("1st Lugana Cavalry", warriorCount=300, wagonCount=0, cavalry=True),
            formation.Formation("1st Taree Cavalry", warriorCount=200, wagonCount=0, cavalry=True)
        ],
        commander=cmdr_soolabab,
        supply=0,
        startingStronghold="Jerboon",
        map=coppercoast
    )
    army_boonan_levy.supply = army_boonan_levy.getSupplyCapacity()
    state.addArmy(army_boonan_levy)

    return state


