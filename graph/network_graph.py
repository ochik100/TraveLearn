import random
from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from networkx import Graph

from community_detection import CommunityDetector
from format_data import (clean_data, combining_dataframes, connect_to_database,
                         convert_collection_to_df)
from topic_modeling.topics import TopicModeling


class NetworkXGraph(object):

    def __init__(self, df, topics):
        self.df = df
        self.topics = topics
        self.edges = None
        self.graph = None
        self.cd = None

    def run(self):
        '''
        Creates a graph!
        '''
        # self.topics = self.get_topics()
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
            G.add_edges_from(user_ids, topic_id=topic_id.item())
        if G:
            print "Created graph from edges"
        return G

    def create_randomly_sampled_subgraph_of_graph(self):
        '''
        Randomly sample 1/5 of the nodes from the original graph using the reservoir sampling algorithm

        OUTPUT:
            subgraph_nodes (list): a list of the randomly sampled nodes
        '''
        # TODO: this produces a subgraph with a lot of nodes with no edges,
        # possibly better to do a random sample of edges?

        num_nodes = self.graph.number_of_nodes() * (1. / 5)
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
    DATABASE_NAME = 'tripadvisor_nevada'
    COLLECTION_NAME = 'nevada'
    db = connect_to_database(DATABASE_NAME)
    df = convert_collection_to_df(db, COLLECTION_NAME)
    # df2 = convert_collection_to_df(db, 'hawaii')
    # df3 = convert_collection_to_df(db, 'colorado')
    # df = combining_dataframes(df1, df2)
    # df = combining_dataframes(df_, df3)
    df, topics, text, text_user = clean_data(df)
    nxg = NetworkXGraph(df, topics)
    nxg.run()
    cd = CommunityDetector(nxg.graph, topics, text, text_user)
    # egos = cd.find_n_ego_networks_of_nodes_with_highest_centralities(5)
    # for ego, topics in egos:
    #     print '-' * 20
    #     tm = TopicModeling(topics)
    #     topic_term_mat, feature_words = tm.vectorize_topics_in_a_community()
    #     nmf, W, H = tm.nmf_topic_modeling(topic_term_mat)
    #     tm.describe_nmf_results(feature_words, W, H)
    cd.run()
    nx.set_node_attributes(cd.LG, 'color', cd.communities)
    nx.write_gexf(cd.LG, 'nevada.gexf')
    # print "-" * 20
    # print "Topic"
    # tm = TopicModeling(cd.community_topics)
    # for c in tm.topics:
    #     print "-" * 20
    #     print "Community", c
    #     topic_term_mat, feature_words = tm.vectorize_topics_in_a_community(tm.topics[c])
    #     nmf, W, H = tm.nmf_topic_modeling(topic_term_mat)
    #     tm.describe_nmf_results(feature_words, W, H)
    #
    # print "-" * 20
    # print "Text"
    # tm = TopicModeling(cd.community_text)
    # for c in tm.topics:
    #     print "-" * 20
    #     print "Community", c
    #     topic_term_mat, feature_words = tm.vectorize_topics_in_a_community(tm.topics[c])
    #     nmf, W, H = tm.nmf_topic_modeling(topic_term_mat)
    #     tm.describe_nmf_results(feature_words, W, H)

    print "-" * 20
    print "Text from Users"
    tm = TopicModeling(cd.community_text_user)
    for c in tm.topics:
        print "-" * 20
        print "Community", c
        topic_term_mat, feature_words = tm.vectorize_topics_in_a_community(tm.topics[c])
        nmf, W, H = tm.nmf_topic_modeling(topic_term_mat)
        tm.describe_nmf_results(feature_words, W, H)
