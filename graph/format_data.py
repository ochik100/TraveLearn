import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import LabelEncoder


def connect_to_database(database_name):
    client = MongoClient()
    db = client[database_name]
    return db


def convert_collection_to_df(db, collection_name):
    input_data = db[collection_name]
    df = pd.DataFrame(list(input_data.find()))
    return df


def clean_data(df):
    df.drop('_id', axis=1, inplace=True)
    df.drop_duplicates(['state', 'topic', 'user', 'text'])
    df.topic = df.topic.apply(lambda top: top.replace(" (Closed topic)", ""))
    le = LabelEncoder()
    df['user_id'] = le.fit_transform(df.user)
    df['topic_id'] = le.fit_transform(df.topic)
    return df


def get_users(df):
    return df[['user_id', 'user']].drop_duplicates()


def get_topics(df):
    return df[['topic_id', 'topic']].drop_duplicates()


def format_edges(clean):
    df = pd.DataFrame(clean.groupby(['user_id', 'topic_id']).count())['text'].reset_index()
    df.rename(columns={'text': 'count'}, inplace=True)  # use for weighted edges
    t1 = df[['user_id', 'topic_id']]
    t2 = df[['user_id', 'topic_id']]
    merged = pd.merge(t1, t2, how='inner', on='topic_id')
    merged = merged[merged.user_id_x != merged.user_id_y]
    for_csv = merged.drop('topic_id', axis=1)
    for_csv.rename(columns={'user_id_x': 'source', 'user_id_y': 'target'}, inplace=True)
    for_csv.to_csv('users_as_edges.tsv', sep='\t', index=False, encoding='utf-8')


def combining_dataframes(df1, df2):
    new_df = pd.concat([df1, df2])
    return new_df
