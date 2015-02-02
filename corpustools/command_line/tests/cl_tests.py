import unittest

import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))
CorpusTools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
print(CorpusTools_path)
sys.path.insert(0, CorpusTools_path)
from CorpusTools.corpustools.corpus.tests.lexicon_test import create_unspecified_test_corpus



class MinPairsTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_non_minimal_pair_corpus(self):
        pass



if __name__ == '__main__':
    unittest.main()
