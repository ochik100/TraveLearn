import itertools
from collections import Counter
from multiprocessing import Pool

import community
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


class CommunityDetector(object):

    def __init__(self, G):
        self.G = G
        self.LG = None
        self.communities = None

    def get_largest_connected_component_of_graph(self):
        '''
        Get the largest connected component of a graph (essentially, remove all components not connected to the largest connected component of a graph)

        OUTPUT:
            LG (graph): graph of largest connected component
        '''
        self.LG = list(nx.connected_component_subgraphs(self.G))[0]
        return self.LG

    def find_communities_with_louvain_modularity(self):
        """
        Find communities within a graph, and plot the graph with the communities shown in different colors

        OUTPUT:
            parts (dict): a dictionary where each key is a node in the graph and its value is its associated community (a number from 0 to the number of communities found within the graph)
        """
        spring_pos = nx.spring_layout(self.LG)
        self.communities = community.best_partition(self.LG)
        values = [self.communities.get(node) for node in self.LG.nodes()]
        plt.axis("off")
        nx.draw_networkx(self.LG, pos=spring_pos, cmap=plt.get_cmap("jet"),
                         node_color=values, node_size=20, with_labels=False)
        plt.show()
        return self.communities

    def find_distribution_of_communities(self):
        Counter(self.communities.values())
