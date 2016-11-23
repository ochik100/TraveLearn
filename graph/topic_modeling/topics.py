import numpy as np
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


class TopicModeling(object):

    def __init__(self, topics):
        self.topics = topics

    def vectorize_topics_in_a_community(self):
        vectorizer = CountVectorizer(stop_words='english', max_features=500, ngram_range=(1, 2))
        topic_term_mat = vectorizer.fit_transform(self.topics)
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
