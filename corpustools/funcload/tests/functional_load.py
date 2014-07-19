import unittest

try:
    from corpustools.corpus.classes import Corpus, Word
except ImportError:
    import sys
    import os
    test_dir = os.path.dirname(os.path.abspath(__file__))
    corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(corpustools_path)
    from corpustools.corpus.classes import Corpus, Word
from corpustools.funcload.functional_load import minpair_fl, deltah_fl


class NeutralizeTest(unittest.TestCase):
    pass

class MinPairsTest(unittest.TestCase):
    def setUp(self):
        pass


class DeltaHTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
