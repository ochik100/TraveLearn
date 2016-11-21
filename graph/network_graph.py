import random
from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from networkx import Graph

from community_detection import CommunityDetector
from format_data import (clean_data, connect_to_database,
                         convert_collection_to_df)


class NetworkXGraph(object):

    def __init__(self, df):
        self.df = df
        self.topics = None
        self.edges = None
        self.graph = None
        self.cd = None

    def run(self):
        '''
        Creates a graph!
        '''
        self.topics = self.get_topics()
        self.edges = self.create_edges_dataframe()
        self.graph = self.create_graph_from_edges()

    def get_topics(self):
        """
        Retrieve all topic id's and respective topics

        INPUT:
            df (DataFrame): cleaned dataframe
        OUTPUT:
            df (DataFrame)
        """
        return self.df[['topic_id', 'topic']].drop_duplicates().set_index('topic_id')

    def create_edges_dataframe(self):
        '''
        Create an edges dataframe from the cleaned data

        OUTPUT:
            edges (dataframe): dataframe with topic ids and combinations of user ids for each topic
        '''
        edges = self.df.groupby('topic_id').user_id.apply(
            lambda user_id: self.helper_get_edges_combination(user_id.values))
        print "Created edge list from dataframe"
        return edges

    def helper_get_edges(self, user_id):
        ids = np.unique(user_id)
        l = len(ids[1:])
        return zip(np.repeat(ids[0], l), ids[1:])

    def helper_get_edges_combination(self, user_id):
        '''
        Helper function to create a list of all the user interactions present in one topic

        OUTPUT:
            A list of tuples
        '''
        ids = np.unique(user_id)
        return [x for x in combinations(ids, 2)]

    def create_graph_from_edges(self):
        '''
        Create a NetworkX graph from an edges dataframe, where nodes are user ids, edges are formed if two users have interacted on a forum, and edges have the topic id of the forum interacted on

        OUTPUT:
            G (NetworkX Graph)
        '''
        G = Graph()
        for topic_id, user_ids in self.edges.iteritems():
            G.add_edges_from(user_ids, topic_id=topic_id)
        if G:
            print "Created graph from edges"
        return G

    def create_randomly_sampled_subgraph_of_graph(self):
        '''
        Randomly sample 1/10 of the nodes from the original graph using the reservoir sampling algorithm

        OUTPUT:
            subgraph_nodes (list): a list of the randomly sampled nodes
        '''
        num_nodes = self.graph.number_of_nodes() * (1. / 10)
        subgraph_nodes = []
        for i, node in enumerate(self.graph.nodes_iter()):
            if i <= num_nodes:
                subgraph_nodes.append(node)
            else:
                replace = random.randint(0, i - 1)
                if replace < num_nodes:
                    subgraph_nodes[replace] = node
        return subgraph_nodes


if __name__ == '__main__':
    DATABASE_NAME = 'tripadvisor'
    COLLECTION_NAME = 'arkansas'
    db = connect_to_database(DATABASE_NAME)
    df = convert_collection_to_df(db, COLLECTION_NAME)
    df = clean_data(df)
    nxg = NetworkXGraph(df)
    nxg.run()
    cd = CommunityDetector(nxg.graph, nxg.topics)
    cd.run()
