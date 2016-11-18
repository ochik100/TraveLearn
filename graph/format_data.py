from itertools import combinations

import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import LabelEncoder


def connect_to_database(database_name):
    '''
    Connect to MongoDB (must have Mongo server running to connect)

    INPUT:
        database_name (st)
    OUTPUT:
        db (MongoDB)
    '''
    client = MongoClient()
    db = client[database_name]
    return db


def convert_collection_to_df(db, collection_name):
    '''
    Convert collection in MongoDB to pandas dataframe

    INPUT:
        db (MongoDB): mongo database instance
        collection_name (str)
    OUTPUT:
        df (DataFrame)
    '''
    input_data = db[collection_name]
    df = pd.DataFrame(list(input_data.find()))
    return df


def clean_data(df):
    '''
    Clean and reformat dataframe

    INPUT:
        df (DataFrame): unclean dataframe
    OUTPUT:
        df (DataFrame): clean dataframe
    '''
    df.drop('_id', axis=1, inplace=True)
    df.drop_duplicates(['state', 'topic', 'user', 'text'])
    df.topic = df.topic.apply(lambda top: top.replace(" (Closed topic)", ""))
    le = LabelEncoder()
    # TODO: should wait till all dataframes are combined to use LabelEncoder
    df['user_id'] = le.fit_transform(df.user)
    df['topic_id'] = le.fit_transform(df.topic)
    return df


def get_post_text(df):
    """
    Retrieve all the posts' text for respective topics

    INPUT:
        df (DataFrame): cleaned dataframe
    OUTPUT:
        df (DataFrame)
    """
    return df[['topic_id', 'text']].drop_duplicates()


def get_users(df):
    """
    Retrieve all user id's and respective usernames

    INPUT:
        df (DataFrame): cleaned dataframe
    OUTPUT:
        df (DataFrame)
    """
    return df[['user_id', 'user']].drop_duplicates()


def get_topics(df):
    """
    Retrieve all topic id's and respective topics

    INPUT:
        df (DataFrame): cleaned dataframe
    OUTPUT:
        df (DataFrame)
    """
    return df[['topic_id', 'topic']].drop_duplicates()


def format_adjacency_list(df):
    """
    Create an adjacency list from a dataframe and write to csv file

    INPUT:
        df (DataFrame): cleaned dataframe
    """
    df = df.groupby(['topic_id']).user_id.apply(lambda x: " ".join(str(x) for x in x.values))
    df.to_csv("adj_list.csv", index=False, header=False)


def format_edges_combinations(df):
    """
    Create edge list from dataframe using combinations and write to tsv file

    INPUT:
        df (DataFrame): cleaned dataframe
    """
    topic_user = df[['topic_id', 'user_id']]
    combos = topic_user.groupby('topic_id').user_id.apply(lambda x: list(combinations(x, 2)))
    edges = pd.DataFrame(reduce(lambda x, y: x + y, combos))
    edges.to_csv('users_as_edges_combo.tsv', sep='\t', header=False, index=False, encoding='utf-8')


def format_edges(clean):
    """
    Create edge list from dataframe and write to tsv file

    INPUT:
        df (DataFrame): cleaned dataframe
    """
    df = pd.DataFrame(clean.groupby(['topic_id', 'user_id']).count())['text'].reset_index()
    df.rename(columns={'text': 'count'}, inplace=True)  # use for weighted edges
    t1 = df[['user_id', 'topic_id']]
    t2 = df[['user_id', 'topic_id']]
    merged = pd.merge(t1, t2, how='inner', on='topic_id')
    merged = merged[merged.user_id_x != merged.user_id_y]
    # can i achieve something like this with combinations?
    for_csv = merged.drop('topic_id', axis=1)
    for_csv.rename(columns={'user_id_x': 'source', 'user_id_y': 'target'}, inplace=True)
    for_csv.to_csv('users_as_edges.tsv', sep='\t', index=False, encoding='utf-8')


def combining_dataframes(df1, df2):
    """
    Combine two dataframes

    INPUT:
        df1 (DataFrame)
        df2 (DataFrame)
    OUTPUT:
        new_df (DataFrame)
    """
    new_df = pd.concat([df1, df2])
    return new_df

if __name__ == '__main__':
    DATABASE_NAME = 'tripadvisor'
    COLLECTION_NAME = 'iowa'
    db = connect_to_database(DATABASE_NAME)
    print "Connected to", DATABASE_NAME
    df = convert_collection_to_df(db, COLLECTION_NAME)
    print "Converted", COLLECTION_NAME, "to dataframe"
    df = clean_data(df)
    print "Cleaned data"
    users = get_users(df)
    topics = get_topics(df)
    post_text = get_post_text(df)
    # print "Formatting edges..."
    # format_edges_combinations(df)
    # print "Created edges file complete."
