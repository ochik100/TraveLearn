import cPickle as pickle

import networkx as nx

from community_detection import CommunityDetector
from format_data import (clean_data, combining_dataframes, connect_to_database,
                         convert_collection_to_df)
from network_graph import NetworkXGraph
from topic_modeling.topics import TopicModeling


def runner(COLLECTION_NAME, df, topics, text, text_user):
    '''
    Create graph from dataframe, find communities within graph, write topics found per community to a file

    INPUT:
        COLLECTION_NAME (str): name of the collection for desired state
        df (dataframe): cleaned dataframe
        topics (dataframe): topic ids and respective topics
        text (dataframe): topic ids and all respective text in each topic
        text_user (dataframe): user ids, topic ids, and the respective text for each user
    '''
    nxg = NetworkXGraph(df, topics)
    nxg.run()
    cd = CommunityDetector(nxg.graph, topics, text, text_user)
    cd.run()

    print "Saving to gexf..."
    gexf_filename = "{}.gexf".format(COLLECTION_NAME)
    nx.write_gexf(cd.LG, gexf_filename)
    print "Saving to pickle..."
    pkl_filename = "{}_cd.pkl".format(COLLECTION_NAME)
    with open(pkl_filename, 'w') as f:
        pickle.dump(cd, f)

    print "-" * 20
    print "Text from Users"
    tm = TopicModeling(cd.community_text_user)
    topics_filename = "{}_topics.txt".format(COLLECTION_NAME)
    with open(topics_filename, 'w') as f:
        for c in tm.community_topics:
            f.write("-" * 20 + "\n")
            f.write("Community {}\n".format(c))
            tm.run(tm.community_topics[c])
            tm.write_nmf_results_to_file(f)
            # tm.describe_nmf_results()

if __name__ == '__main__':
    DATABASE_NAME = 'database_name'
    COLLECTION_NAME = 'collection_name'
    db = connect_to_database(DATABASE_NAME)
    df = convert_collection_to_df(db, COLLECTION_NAME)
    df, topics, text, text_user = clean_data(df)
    runner(COLLECTION_NAME, df, topics, text, text_user)
