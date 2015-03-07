import unittest

import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0, corpustools_path)
from corpustools.corpus.tests.lexicon_test import create_unspecified_test_corpus

from corpustools.neighdens.neighborhood_density import neighborhood_density, neighborhood_density_graph

class NeighDenTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_basic_corpus(self):
        calls = [({'corpus': self.corpus,
                        'query':self.corpus.find('mata'),
                        'max_distance':1},1.0),
                ({'corpus': self.corpus,
                        'query':self.corpus.find('nata'),
                        'max_distance':2},3.0)]

        for c,v in calls:
            result = neighborhood_density(**c)
            msgcall = 'Call: {}\nExpected: {}\nActually got:{}'.format(c,v,result)
            self.assertTrue(abs(result[0]-v) < 0.0001,msg=msgcall)

    def test_basic_corpus_graph(self):
        calls = [({'corpus': self.corpus,
                        'query':self.corpus.find('mata'),
                        'max_distance':1},1.0),
                ({'corpus': self.corpus,
                        'query':self.corpus.find('nata'),
                        'max_distance':2},3.0)]

        for c,v in calls:
            result = neighborhood_density_graph(**c)
            msgcall = 'Call: {}\nExpected: {}\nActually got:{}'.format(c,v,result)
            self.assertTrue(abs(result[0]-v) < 0.0001,msg=msgcall)


if __name__ == '__main__':
    unittest.main()
