import numpy as np
from sklearn.decomposition import NMF
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer


class TopicModeling(object):

    def __init__(self, topics):
        self.topics = topics

    def vectorize_topics_in_a_community(self, topics):
        additional_stop_words = ['http', 'https', 'g29217', 'i268',
                                 'www', 'com', 'tripadvisor', 'showtopic']
        stop_words = text.ENGLISH_STOP_WORDS.union(additional_stop_words)
        vectorizer = CountVectorizer(stop_words=stop_words, max_features=300, ngram_range=(2, 2))
        topic_term_mat = vectorizer.fit_transform(topics)
        feature_words = vectorizer.get_feature_names()
        return topic_term_mat, feature_words

    def nmf_topic_modeling(self, topic_term_mat):
        if topic_term_mat.shape[0] < 5:
            nmf = NMF(n_components=topic_term_mat.shape[0])
        else:
            nmf = NMF(n_components=5)
        W = nmf.fit_transform(topic_term_mat)
        H = nmf.components_
        print("Reconstruction error: %f") % nmf.reconstruction_err_
        return nmf, W, H

    def describe_nmf_results(self, feature_words, W, H, n_top_words=15):
        for topic_num, topic in enumerate(H):
            print "Topic %d:" % topic_num
            print ", ".join([feature_words[i] for i in topic.argsort()[::-1][:15]])
