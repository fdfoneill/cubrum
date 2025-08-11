import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import datetime, json
import numpy as np
import networkx as nx
from networkx.classes.graph import Graph

from .formation import Formation


class Map(Graph):
    """A network of locations and paths between them

    ***

    Methods:
        addNodes(node_list)
        addEdges(edge_list)
        addNodesFromFile()
        addEdgesFromFile()
        getShortestPath(start, end) -> list
        getPathLength(path) -> int
    """
    def fillDefaults(self):
        for node in self.nodes:
            # set name
            self.nodes[node]['name']=node
            self.nodes[node]['taxed']=self.nodes[node].get("taxed", [])
            self.nodes[node]['levied']=self.nodes[node].get("levied", [])
            # default defenses
            if self.nodes[node].get("defenses") is None:
                if self.nodes[node].get('strongholdType')=="city":
                    self.nodes[node]['defenses'] = 4
                elif self.nodes[node].get('strongholdType')=="town":
                    self.nodes[node]['defenses'] = 3
                elif self.nodes[node].get('strongholdType')=="fortress":
                    self.nodes[node]['defenses'] = 5
            # gates closed by default
            if self.nodes[node].get("gatesOpen") is None:
                self.nodes[node]['gatesOpen'] = False
            # default supply
            if self.nodes[node].get("maxSupply") is None:
                if self.nodes[node].get('strongholdType')=="city":
                    self.nodes[node]['maxSupply'] = np.random.randint(1,7)*100000
                    self.nodes[node]['currentSupply'] = self.nodes[node]['maxSupply']
                elif self.nodes[node].get('strongholdType')=="town":
                    self.nodes[node]['maxSupply'] = np.random.randint(1,7)*10000
                    self.nodes[node]['currentSupply'] = self.nodes[node]['maxSupply']
                elif self.nodes[node].get('strongholdType')=="fortress":
                    self.nodes[node]['maxSupply'] = np.random.randint(1,7)*1000
                    self.nodes[node]['currentSupply'] = self.nodes[node]['maxSupply']
            # default loot
            if self.nodes[node].get("maxLoot") is None:
                if self.nodes[node].get('strongholdType')=="city":
                    self.nodes[node]['maxLoot'] = np.random.randint(1,7)*100000
                    self.nodes[node]['currentLoot'] = self.nodes[node]['maxLoot']
                elif self.nodes[node].get('strongholdType')=="town":
                    self.nodes[node]['maxLoot'] = np.random.randint(1,7)*100000
                    self.nodes[node]['currentLoot'] = self.nodes[node]['maxLoot']
                elif self.nodes[node].get('strongholdType')=="fortress":
                    self.nodes[node]['maxLoot'] = (np.random.randint(10,20)*1000) if (np.random.randint(1,11)>9) else 0
                    self.nodes[node]['currentLoot'] = self.nodes[node]['maxLoot']
            # default garrison, update to use Formation objects
            if self.nodes[node].get("garrison") is None:
                if self.nodes[node].get('strongholdType')=="city":
                    self.nodes[node]['garrison'] = {'name':'{} garrison'.format(node), 'infantryCount':500}
                elif self.nodes[node].get('strongholdType')=="town":
                    self.nodes[node]['garrison'] = {'name':'{} garrison'.format(node), 'infantryCount':250}
                elif self.nodes[node].get('strongholdType')=="fortress":
                    self.nodes[node]['garrison'] = {'name':'{} garrison'.format(node), 'infantryCount':250, 'cavalryCount':50}
        for edge in self.edges:
            self.edges[edge]['foraged'] = self.edges[edge].get("foraged", []) 

    def addNodes(self, node_list) -> None:
        """Add nodes to underlying graph object

        ***

        Parameters:
            node_list: list of lists. Each item is a 2-tuple, with the first
                item as the node name, and the second a dictionary of 
                node attributes.
        """
        node_json = node_list.copy()
        self.add_nodes_from(node_json)
        self.fillDefaults()

    def addEdges(self, edge_list) -> None:
        """Add edges to underlying graph object

        ***
        Parameters:
            edge_list: list of lists. Each item is a 3-tuple, with the first
                two items as the endpoints and the third a dictionary
                of edge attributes. The attributes must include 'distance',
                measured in leagues.
        """
        edge_json = edge_list.copy()
        for e in edge_json:
            e[2]['start'] = e[0]
        self.add_edges_from(edge_json)
        self.fillDefaults()

    def addNodesFromFile(self, json_file_path) -> None:
        with open(json_file_path, 'r') as rf:
            self.addNodes(json.load(rf)) 

    def addEdgesFromFile(self, json_file_path) -> None:
        with open(json_file_path, 'r') as rf:
            self.addEdges(json.load(rf)) 

    def getShortestPath(self, start:str, end:str, exclusion_function=None) -> list:
        """Returns the shortest path between two nodes

        ***

        Parameters:
            start: string name of starting node
            end: string name of ending node
            exclusion_function: boolean function that takes exactly three parameters: the 
                attribute dictionary of the start node, the end node, and the edge between 
                them. If this function returns True, the edge is excluded from consideration.
                If None (default), all edges are considered.
        """
        if exclusion_function is None:
            exclusion_function = lambda u,v,d: False 
        def weight_function(u,v,d):
            if exclusion_function(self.nodes[u],self.nodes[v],d):
                return None
            return d['distance']
        shortest_path = nx.shortest_simple_paths(self, start, end, weight=weight_function).__next__()
        return shortest_path
    
    def getPathLength(self, path:list) -> int:
        """Returns the total number of leagues along a path

        ***

        Parameters:
            path: list of node names, each adjacent to the last
        """
        total_distance = 0
        for i in range(1, len(path)):
            edge = self.edges[(path[i-1], path[i])]
            total_distance += edge['distance']
        return total_distance