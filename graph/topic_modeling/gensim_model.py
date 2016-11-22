import string

from gensim import corpora
from gensim.models.ldamodel import LdaModel
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


class GensimLDA(object):

    def __init__(self):
        self.stop = set(stopwords.words('english'))
        self.exclude = set(string.punctuation)
        self.lemma = WordNetLemmatizer()

    def clean(self, doc):
        stop_free = " ".join([i for i in doc.lower().split() if i not in self.stop])
        punc_free = ''.join(ch for ch in stop_free if ch not in self.exclude)
        normalized = " ".join(self.lemma.lemmatize(word) for word in punc_free.split())
        return normalized

    def clean_docs_in_community(self, topics):
        topics_clean = [self.clean(doc).split() for doc in topics]
        dictionary = corpora.Dictionary(topics_clean)
        topic_term_matrix = [dictionary.doc2bow(doc) for doc in topics_clean]
        return topics_clean, dictionary, topic_term_matrix

    def run_lda(self, topic_term_matrix, dictionary):
        lda = LdaModel(topic_term_matrix, num_topics=5, id2word=dictionary, passes=50)
        print lda.print_topics(num_topics=5, num_words=5)
