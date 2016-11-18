from collections import Counter

import community
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def load_data(filename):
    df = pd.read_json(filename)
    return df


def create_edges_file(df, filename):
    ndf = df.groupby(['topic', 'user']).date_time.count().reset_index()
    ndf.drop('date_time', axis=1, inplace=True)
    ndf.columns = ['source', 'target']
    ndf.to_csv(filename, sep='\t', header=True, encoding='utf-8', index=False)
    return None


def create_graph_from_edges_file(filename):
    TG = nx.read_edgelist(filename, delimiter='\t')
    return TG


def create_graph_from_adjaceny_list_file(filename):
    AG = nx.read_adjlist(filename)
    return AG


def get_largest_connected_component_of_graph(G):
    return list(nx.connected_component_subgraphs(AG))[0]


def find_communities(G):
    spring_pos = nx.spring_layout(G)
    parts = community.best_partition(G)
    values = [parts.get(node) for node in G.nodes()]
    plt.axis("off")
    nx.draw_networkx(G, pos=spring_pos, cmap=plt.get_cmap("jet"),
                     node_color=values, node_size=20, with_labels=False)
    # plt.show()
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
