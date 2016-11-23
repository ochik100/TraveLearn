from collections import Counter, defaultdict
from itertools import islice
from multiprocessing import Pool

import community
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


class CommunityDetector(object):

    def __init__(self, G, topics, text):
        # self.G = G
        self.topics = topics
        self.text = text
        self.LG = self.get_largest_connected_component_of_graph(G)
        self.communities = None
        self.comm_dict = defaultdict(list)
        self.community_subgraphs = []
        self.community_topics = {}
        self.community_text = {}

    def run(self):
        '''
        Find the communities!
        '''
        self.communities = self.find_communities_with_louvain_modularity(self.LG)
        self.get_nodes_per_community()
        self.create_subgraphs_and_topics_per_community()

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

    def plot_communities(self):
        spring_pos = nx.spring_layout(self.LG)
        values = [self.communities.get(node) for node in self.LG.nodes()]
        plt.axis("off")
        nx.draw_networkx(self.LG, pos=spring_pos, cmap=plt.get_cmap("jet"),
                         node_color=values, node_size=20, with_labels=False)
        plt.show()

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

    def create_subgraphs_and_topics_per_community(self):
        '''
        Creates subgraphs of each community and finds all topics present in each community
        '''
        print "Creating subgraphs and finding topics for each community..."
        for c in self.comm_dict:
            comm_subgraph = self.LG.subgraph(self.comm_dict[c])
            self.community_subgraphs.append(comm_subgraph)

            topic_ids = np.unique(nx.get_edge_attributes(comm_subgraph, 'topic_id').values())

            self.community_topics[c] = self.get_topics_from_topic_ids(topic_ids)
            self.community_text[c] = self.get_text_from_topic_ids(topic_ids)

    def get_topics_from_topic_ids(self, topic_ids):
        '''
        From the specified community, find the topics found within that community

        INTPUT:
            topic_ids (array): array of topic ids
        OUTPUT:
            topics found in the community
        '''
        # topic_ids = np.unique(nx.get_edge_attributes(subgraph, 'topic_id').values())
        return self.topics.loc[topic_ids].values.flatten()

    def get_text_from_topic_ids(self, topic_ids):
        return self.text.loc[topic_ids].values.flatten()

    def girvan_newman_step(self, LG):
        '''
        Run one step of the Girvan-Newman community detection algorithm.
        Afterwards, the graph will have one more connected component
        '''
        init_ncomp = nx.number_connected_components(LG)
        ncomp = init_ncomp
        while ncomp == init_ncomp:
            bw = Counter(nx.edge_betweenness_centrality(LG))
            a, b = bw.most_common(1)[0][0]
            LG.remove_edge(a, b)
            ncomp = nx.number_connected_components(LG)

    def find_communities_with_girvan_newman(self, n):
        '''
        Run the Girvan-Newman algorithm for n steps, and return the resulting
        communities

        INPUT:
            n (int): numer of iterations to run the algorithm
        OUTPUT:
            list of communities
        '''
        G1 = self.LG.copy()
        for i in xrange(n):
            self.girvan_newman_step(G1)
        return list(nx.connected_components(G1))

    def remove_node_with_highest_eigenvector_centrality(self):
        num_iterations = int(self.LG.number_of_nodes() * 0.10)
        for i in xrange(num_iterations):
            node = Counter(nx.eigenvector_centrality(self.LG)).most_common(1)[0][0]
            self.LG.remove_node(node)

    def find_n_ego_networks_of_nodes_with_highest_centralities(self, n):
        ego_nodes = Counter(nx.eigenvector_centrality(self.LG)).most_common(n)
        ego_graphs = []
        for node, ec in ego_nodes:
            ego = nx.ego_graph(self.LG, node, undirected=True)
            edges = nx.get_edge_attributes(ego, 'topic_id').values()
            topics = self.get_topics_from_topic_ids(edges)
            ego_graphs.append((ego, topics))
        return ego_graphs
        # return sorted(ego_graphs, key=nx.average_clustering, reverse=True)
