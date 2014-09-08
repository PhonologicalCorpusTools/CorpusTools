import unittest

import os
try:
    from corpustools.corpus.io import (download_binary, save_binary, load_binary,
                                    load_corpus_csv,load_corpus_text,
                                    export_corpus_csv, export_feature_matrix_csv,
                                    load_feature_matrix_csv,DelimiterError)
except ImportError:
    import sys

    test_dir = os.path.dirname(os.path.abspath(__file__))
    corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(corpustools_path)
    from corpustools.corpus.io import (download_binary, save_binary, load_binary,
                                    load_corpus_csv,load_corpus_text,
                                    export_corpus_csv, export_feature_matrix_csv,
                                    load_feature_matrix_csv,DelimiterError)

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix)
from corpustools.corpus.tests.classes import create_unspecified_test_corpus

TEST_DIR = r'C:\Users\michael\Dropbox\Measuring_Phonological_Relations\Computational\CorpusTools_test_files\Corpus_loading'

class RuntimeTest(unittest.TestCase):
    def setUp(self):
        self.example_path = os.path.join(TEST_DIR,'example.txt')
        self.hayes_path = os.path.join(TEST_DIR,'hayes.txt')
        self.spe_path = os.path.join(TEST_DIR,'spe.txt')

    def test_corpus_csv(self):
        self.assertRaises(DelimiterError,load_corpus_csv,'example',self.example_path,delimiter='\t')
        self.assertRaises(DelimiterError,load_corpus_csv,'example',self.example_path,delimiter=',',trans_delimiter='/')
        #c = load_corpus_csv('example',self.example_path,delimiter=',')

        c,errors = load_corpus_csv('example',self.example_path,delimiter=',')

        example_c = create_unspecified_test_corpus()

        self.assertIsInstance(c,Corpus)


if __name__ == '__main__':
    unittest.main()
