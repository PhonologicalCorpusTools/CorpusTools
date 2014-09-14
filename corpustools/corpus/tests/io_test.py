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
from corpustools.corpus.tests.classes_test import create_unspecified_test_corpus

TEST_DIR = r'C:\Users\michael\Dropbox\Measuring_Phonological_Relations\Computational\CorpusTools_test_files\Corpus_loading'

class CustomCorpusTest(unittest.TestCase):
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
        self.assertEqual(c,example_c)

class CustomCorpusTextTest(unittest.TestCase):
    def setUp(self):
        self.spelling_path = os.path.join(TEST_DIR,'test_text_spelling.txt')
        self.transcription_path = os.path.join(TEST_DIR,'test_text_transcription.txt')

    def test_load_spelling_no_ignore(self):
        self.assertRaises(DelimiterError, load_corpus_text, 'test', self.spelling_path,"?",[])

        c,errors = load_corpus_text('test',self.spelling_path,' ',[],string_type='spelling')

        self.assertEqual(c['ab'].frequency, 2)


    def test_load_spelling_ignore(self):
        c,errors = load_corpus_text('test',self.spelling_path,' ',["'",'.'],string_type='spelling')

        self.assertEqual(c['ab'].frequency, 3)
        self.assertEqual(c['cabd'].frequency, 1)

    def test_load_transcription(self):
        self.assertRaises(DelimiterError,load_corpus_text,'test',
                                self.transcription_path," ",[],
                                string_type='transcription',
                                trans_delimiter = ',')

        c,errors = load_corpus_text('test',self.transcription_path,' ',[],string_type='transcription',trans_delimiter='.')

        self.assertEqual(sorted(c.inventory.keys()), sorted(['#','a','b','c','d']))

class BinaryCorpusLoadTest(unittest.TestCase):
    def setUp(self):
        self.example_path = os.path.join(TEST_DIR,'example.corpus')

    def test_load(self):
        c = load_binary(self.example_path)

        example_c = create_unspecified_test_corpus()

        self.assertEqual(c,example_c)


class BinaryCorpusSaveTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()
        self.path = os.path.join(TEST_DIR,'testsave.corpus')

    def test_save(self):
        save_binary(self.corpus,self.path)

        c = load_binary(self.path)

        self.assertEqual(self.corpus,c)

class BinaryCorpusDownloadTest(unittest.TestCase):
    def setUp(self):
        self.name = 'example'
        self.path = os.path.join(TEST_DIR,'testdownload.corpus')
        self.example_path = os.path.join(TEST_DIR,'example.corpus')

    def test_download(self):
        download_binary(self.name,self.path)

        c = load_binary(self.path)

        example_c = load_binary(self.example_path)
        self.assertEqual(c,example_c)



if __name__ == '__main__':
    if os.path.exists(TEST_DIR):
        unittest.main()
