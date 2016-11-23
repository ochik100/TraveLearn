import networkx as nx

from community_detection import CommunityDetector
from format_data import (clean_data, combining_dataframes, connect_to_database,
                         convert_collection_to_df)
from network_graph import NetworkXGraph
from topic_modeling.topics import TopicModeling


def runner(DATABASE_NAME, COLLECTION_NAME):
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
    cd.run()
    # nx.write_gexf(cd.LG, 'nevada.gexf')

    print "-" * 20
    print "Text from Users"
    tm = TopicModeling(cd.community_text_user)
    for c in tm.topics:
        print "-" * 20
        print "Community", c
        tm.run(tm.topics[c])
        # topic_term_mat, feature_words = tm.vectorize_topics_in_a_community(tm.topics[c])
        # nmf, W, H = tm.nmf_topic_modeling(topic_term_mat)
        # tm.describe_nmf_results(feature_words, W, H)

if __name__ == '__main__':
    DATABASE_NAME = 'tripadvisor'
    COLLECTION_NAME = 'arkansas'
    runner(DATABASE_NAME, COLLECTION_NAME)
