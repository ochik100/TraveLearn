from collections import Counter, defaultdict
from itertools import islice
from multiprocessing import Pool

import community
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


class CommunityDetector(object):

    def __init__(self, G):
        # self.G = G
        self.LG = self.get_largest_connected_component_of_graph(G)
        self.communities = None
        self.comm_dict = defaultdict(list)
        self.community_subgraphs = []

    def run(self):
        '''
        Find the communities!
        '''
        self.communities = self.find_communities_with_louvain_modularity(self.LG)
        self.get_nodes_per_community()
        self.create_subgraphs_per_community()

    def get_largest_connected_component_of_graph(self, graph):
        '''
        Get the largest connected component of a graph (essentially, remove all components not connected to the largest connected component of a graph)

        OUTPUT:
            LG (graph): graph of largest connected component
        '''
        return list(islice(nx.connected_component_subgraphs(graph), 1))[0]
        # return list(nx.connected_component_subgraphs(graph))[0]

    def find_communities_with_louvain_modularity(self, graph):
        """
        Find communities within a graph, and plot the graph with the communities shown in different colors

        OUTPUT:
            parts (dict): a dictionary where each key is a node in the graph and its value is its associated community (a number from 0 to the number of communities found within the graph)
        """
        print "Finding communities..."
        return community.best_partition(self.LG)
        # spring_pos = nx.spring_layout(LG)
        # self.communities = community.best_partition(LG)
        # values = [self.communities.get(node) for node in LG.nodes()]
        # plt.axis("off")
        # nx.draw_networkx(LG, pos=spring_pos, cmap=plt.get_cmap("jet"),
        #                  node_color = values, node_size = 20, with_labels = False)
        # plt.show()
        # return self.communities

    def find_distribution_of_communities(self):
        '''
        Find the number of nodes per community

        OUTPUT:
            dict
        '''
        return Counter(self.communities.values())

    def get_nodes_per_community(self):
        '''
        Creates a dictionary where keys are communities and values are a list of nodes in each community

        '''
        print "Finding nodes per community..."
        for node, comm in self.communities.iteritems():
            self.comm_dict[comm].append(node)
        # return self.comm_dict

    def create_subgraphs_per_community(self):
        '''
        Creates subgraphs of each community
        '''
        print "Creating subgraphs for each community..."
        for c in self.comm_dict:
            self.community_subgraphs.append(self.LG.subgraph(self.comm_dict[c]))

    def get_topics_from_subgraph(self, subgraph, topics):
        '''
        From the specified community, find the topics found within that community

        INTPUT:
            subgraph (NetworkX graph): community subraph
            topics (dataframe): dataframe with topic ids and their corresponding topic
        OUTPUT:
            topics found in the community
        '''
        topic_ids = np.unique(nx.get_edge_attributes(subgraph, 'topic_id').values())
        return topics.loc[topic_ids]
