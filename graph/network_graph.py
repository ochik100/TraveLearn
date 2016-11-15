import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def load_data(filename):
    # with open(filename, 'a') as f:
    #     f.write(']')
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

if __name__ == '__main__':
    df = load_data('data/cali.json')
    small_df = df.iloc[:10000]
    create_edges_file(small_df, 'data/small_edges.tsv')
    # SG = create_graph_from_edges_file('data/small_edges.tsv')
    # nx.draw(SG)
    # plt.savefig("small_graph.pdf")
