import numpy as np
from sklearn.decomposition import NMF
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer


class TopicModeling(object):

    def __init__(self, community_topics):
        '''
        Initialize TopicModeling object
        '''
        self.community_topics = community_topics
        self.topic_term_mat = None
        self.feature_words = None
        self.nmf = None
        self.W = None
        self.H = None

    def run(self, topics):
        '''
        Run NMF model on communities
        '''
        self.vectorize_topics_in_a_community(topics)
        self.nmf_topic_modeling()
        # self.describe_nmf_results()

    def vectorize_topics_in_a_community(self, topics):
        '''
        Vectorize the text specified using a count vectorizer

        INPUT:
            topics (list): list of text
        OUTPUT:
            topic_term_mat (matrix): vectorized text matrix
            feature_words (list): list of the feature words that were vectorized
        '''
        additional_stop_words = ['http', 'https', 'g29217', 'i268',
                                 'www', 'com', 'tripadvisor', 'showtopic']
        stop_words = text.ENGLISH_STOP_WORDS.union(additional_stop_words)
        vectorizer = CountVectorizer(stop_words=stop_words, max_features=300, ngram_range=(2, 2))
        self.topic_term_mat = vectorizer.fit_transform(topics)
        self.feature_words = vectorizer.get_feature_names()
        # return self.topic_term_mat, self.feature_words

    def nmf_topic_modeling(self):
        '''
        Use non-negative matrix factorization to extract topics from the text
        '''
        if self.topic_term_mat.shape[0] < 5:
            self.nmf = NMF(n_components=self.topic_term_mat.shape[0])
        else:
            self.nmf = NMF(n_components=10)
        self.W = self.nmf.fit_transform(self.topic_term_mat)
        self.H = self.nmf.components_
        print("Reconstruction error: %f") % self.nmf.reconstruction_err_
        # return nmf, W, H

    def describe_nmf_results(self, n_top_words=10):
        '''
        Prints the n top words contributing to each topic

        INPUT:
            n_top_words (int): number of words to display
        '''
        for topic_num, topic in enumerate(self.H):
            print "Topic %d:" % topic_num
            print ", ".join([self.feature_words[i] for i in topic.argsort()[::-1][:n_top_words]])

    def write_nmf_results_to_file(self, f, n_top_words=15):
        '''
        Write n top words per topic for each of the communities to a file

        INPUT:
            f (filestream)
            n_top_words (int): number of words to display
        '''
        for topic_num, topic in enumerate(self.H):
            f.write("Topic %d:\n" % topic_num)
            words = [self.feature_words[i]
                     for i in topic.argsort()[::-1][:n_top_words]]
            string = ", ".join(words) + "\n"
            f.write(string.encode('utf-8'))
