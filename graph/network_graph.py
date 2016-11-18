from collections import Counter

import community
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


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


def get_largest_connected_component_of_graph(G):
    '''
    Get the largest connected component of a graph (essentially, remove all components not connected to the largest connected component of a graph)

    INPUT:
        G (graph): graph of entire network
    OUTPUT:
        LG (graph): graph of largest connected component
    '''
    return list(nx.connected_component_subgraphs(AG))[0]


def find_communities(G):
    """
    Find communities within a graph, and plot the graph with the communities shown in different colors

    INPUT:
        G (graph)
    OUTPUT:
        parts (dict): a dictionary where each key is a node in the graph and its value is its associated community (a number from 0 to the number of communities found within the graph)
    """
    spring_pos = nx.spring_layout(G)
    parts = community.best_partition(G)
    values = [parts.get(node) for node in G.nodes()]
    plt.axis("off")
    nx.draw_networkx(G, pos=spring_pos, cmap=plt.get_cmap("jet"),
                     node_color=values, node_size=20, with_labels=False)
    plt.show()
    return parts


def find_distribution_of_communities(parts):
    Counter(parts.values())

if __name__ == '__main__':
    df = load_data('data/cali.json')
    # small_df = df.iloc[:10000]
    small_df = df.iloc[:100]
    create_edges_file(df, 'data/rly_small_cali_edges.tsv')
    # SG = create_graph_from_edges_file('data/small_edges.tsv')
    # nx.draw(SG)
    # plt.savefig("small_graph.pdf")

    # user labelencoder
