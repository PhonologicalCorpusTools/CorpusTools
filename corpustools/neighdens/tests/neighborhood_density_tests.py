import unittest

import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
print(corpustools_path)
sys.path.insert(0, corpustools_path)
from corpustools.corpus.tests.lexicon_test import create_unspecified_test_corpus

from corpustools.neighdens.neighborhood_density import neighborhood_density
from corpustools.corpus.classes import Segment



class MinPairsTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_non_minimal_pair_corpus(self):
        calls = [({'corpus': self.corpus,
                        'query':'mata',
                        'max_distance':1},1.0),
                ({'corpus': self.corpus,
                        'query':'nata',
                        'max_distance':2},3.0)]

        for c,v in calls:
            result = neighborhood_density(**c)
            msgcall = 'Call: {}\nExpected: {}\nActually got:{}'.format(c,v,result)
            self.assertTrue(abs(result[0]-v) < 0.0001,msg=msgcall)


if __name__ == '__main__':
    unittest.main()
