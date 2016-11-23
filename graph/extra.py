import pandas as pd


'''
Functions that are helpful, but probably won't be used
'''


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
