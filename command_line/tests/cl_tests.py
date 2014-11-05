import unittest

import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))
CorpusTools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
print(CorpusTools_path)
sys.path.insert(0, CorpusTools_path)
from CorpusTools.corpustools.corpus.tests.classes_test import create_unspecified_test_corpus



class MinPairsTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_non_minimal_pair_corpus(self):
        calls = [({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ')],
                        'frequency_cutoff':0,
                        'relative_count':True},0.125)]

        for c,v in calls:
            msgcall = 'Call: {}\nExpected: {}\nActually got:{}'.format(c,v,minpair_fl(**c))
            self.assertTrue(abs(minpair_fl(**c)-v) < 0.0001,msg=msgcall)



if __name__ == '__main__':
    unittest.main()
