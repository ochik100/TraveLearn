from itertools import chain

import igraph
import numpy as np
import pandas as pd
from igraph import Graph


def create_graph_from_dataframe(df):
    edges = df.groupby('topic_id').user_id.apply(
        lambda user_id: helper_get_edges(user_id.values)).values
    edges = list(chain.from_iterable(edges))
    graph = Graph(edges)
    return graph


def helper_get_edges(user_ids):
    l = len(user_ids[1:])
    return zip(np.repeat(user_ids[0], l), user_ids[1:])
