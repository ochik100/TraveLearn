import random
from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from networkx import Graph

from format_data import (clean_data, connect_to_database,
                         convert_collection_to_df, get_topics)


def load_data(filename):
    """
    Load data into a pandas dataframe from a JSON file

    INPUT:
        filename (str)
    OUTPUT:
        df (DataFrame)
    """
    df = pd.read_json(filename)
    return df


def create_edges_file(df, filename):
    """
    Create an edge list TSV file from dataframe (this format is used for Gephi)

    INPUT:
        df (DataFrame)
        filename (str)
    """
    ndf = df.groupby(['topic', 'user']).date_time.count().reset_index()
    ndf.drop('date_time', axis=1, inplace=True)
    ndf.columns = ['source', 'target']
    ndf.to_csv(filename, sep='\t', header=True, encoding='utf-8', index=False)


def create_graph_from_edges_file(filename):
    """
    Create a graph from an edge list given the TSV filename

    INPUT:
        filename (str)
    OUTPUT:
        G (graph)
    """
    G = nx.read_edgelist(filename, delimiter='\t')
    return G


def create_graph_from_adjaceny_list_file(filename):
    """
    Create a graph from an adjacency list given the filename

    INPUT:
        filename (str)
    OUTPUT:
        AG (graph)
    """
    AG = nx.read_adjlist(filename)
    return AG


def create_edge_list_from_dataframe(df):
    edges = df.groupby('topic_id').user_id.apply(
        lambda user_id: helper_get_edges_combination(user_id.values))
    # edges = list(chain.from_iterable(edges))
    return edges


def helper_get_edges(user_id):
    ids = np.unique(user_id)
    l = len(ids[1:])
    return zip(np.repeat(ids[0], l), ids[1:])


def helper_get_edges_combination(user_id):
    ids = np.unique(user_id)
    return [x for x in combinations(ids, 2)]


def create_graph_from_edges(edges):
    G = Graph()
    for topic_id, user_ids in edges.iteritems():
        G.add_edges_from(user_ids, topic_id=topic_id)
    return G


def create_subgraph_of_graph(graph):
    num_nodes = graph.number_of_nodes() * (1. / 10)
    subgraph_nodes = []
    for i, node in enumerate(graph.nodes_iter()):
        if i <= num_nodes:
            subgraph_nodes.append(node)
        else:
            replace = random.randint(0, i - 1)
            if replace < num_nodes:
                subgraph_nodes[replace] = node
    return subgraph_nodes


if __name__ == '__main__':
    DATABASE_NAME = 'tripadvisor'
    COLLECTION_NAME = 'hawaii'
    db = connect_to_database(DATABASE_NAME)
    df = convert_collection_to_df(db, COLLECTION_NAME)
    df = clean_data(df)
    edges = create_edge_list_from_dataframe(df)
    print "Created edge list from dataframe"
    G = create_graph_from_edges(edges)
    print "Created graph from edges"
    # df = load_data('data/cali.json')
    # small_df = df.iloc[:10000]
    # small_df = df.iloc[:100]
    # create_edges_file(df, 'data/rly_small_cali_edges.tsv')
    # SG = create_graph_from_edges_file('data/small_edges.tsv')
    # nx.draw(SG)
    # plt.savefig("small_graph.pdf")

    # user labelencoder
