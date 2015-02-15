import unittest

import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,corpustools_path)
from corpustools.corpus.io import (download_binary, save_binary, load_binary,
                                load_corpus_csv,load_spelling_corpus, load_transcription_corpus,
                                export_corpus_csv, export_feature_matrix_csv,
                                load_feature_matrix_csv,DelimiterError,
                                load_corpus_ilg)

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix)
from corpustools.corpus.tests.lexicon_test import create_unspecified_test_corpus

TEST_DIR = r'C:\Users\michael\Dropbox\Measuring_Phonological_Relations\Computational\CorpusTools_test_files\Corpus_loading'

class ILGTest(unittest.TestCase):
    def setUp(self):
        self.basic_path = os.path.join(TEST_DIR,'ilg','test_basic.txt')

    def test_ilg_basic(self):
        corpus = load_corpus_ilg('test', self.basic_path,delimiter=None,ignore_list=[], trans_delimiter = '.')
        print(corpus.words)
        self.assertEqual(corpus.lexicon.find('a').frequency,2)


class CustomCorpusTest(unittest.TestCase):
    def setUp(self):
        self.example_path = os.path.join(TEST_DIR,'example.txt')
        self.hayes_path = os.path.join(TEST_DIR,'hayes.txt')
        self.spe_path = os.path.join(TEST_DIR,'spe.txt')

    def test_corpus_csv(self):
        if not os.path.exists(TEST_DIR):
            return
        self.assertRaises(DelimiterError,load_corpus_csv,'example',self.example_path,delimiter='\t')
        self.assertRaises(DelimiterError,load_corpus_csv,'example',self.example_path,delimiter=',',trans_delimiter='/')
        #c = load_corpus_csv('example',self.example_path,delimiter=',')

        c = load_corpus_csv('example',self.example_path,delimiter=',')

        example_c = create_unspecified_test_corpus()

        self.assertIsInstance(c,Corpus)
        self.assertEqual(c,example_c)

class CustomCorpusTextTest(unittest.TestCase):
    def setUp(self):
        self.spelling_path = os.path.join(TEST_DIR,'test_text_spelling.txt')
        self.transcription_path = os.path.join(TEST_DIR,'test_text_transcription.txt')
        self.transcription_morphemes_path = os.path.join(TEST_DIR,'test_text_transcription_morpheme_boundaries.txt')

        self.full_feature_matrix_path = os.path.join(TEST_DIR,'basic.feature')
        self.missing_feature_matrix_path = os.path.join(TEST_DIR, 'missing_segments.feature')

    def test_load_spelling_no_ignore(self):
        if not os.path.exists(TEST_DIR):
            return
        self.assertRaises(DelimiterError, load_spelling_corpus, 'test', self.spelling_path,"?",[])

        c = load_spelling_corpus('test',self.spelling_path,' ',[])

        self.assertEqual(c.lexicon['ab'].frequency, 2)


    def test_load_spelling_ignore(self):
        if not os.path.exists(TEST_DIR):
            return
        c = load_spelling_corpus('test',self.spelling_path,' ',["'",'.'])

        self.assertEqual(c.lexicon['ab'].frequency, 3)
        self.assertEqual(c.lexicon['cabd'].frequency, 1)

    def test_load_transcription(self):
        if not os.path.exists(TEST_DIR):
            return
        self.assertRaises(DelimiterError,load_transcription_corpus,'test',
                                self.transcription_path," ",[],
                                trans_delimiter = ',')

        c = load_transcription_corpus('test',self.transcription_path,' ',[],trans_delimiter='.')

        self.assertEqual(sorted(c.lexicon.inventory), sorted(['#','a','b','c','d']))

    def test_load_transcription_morpheme(self):
        if not os.path.exists(TEST_DIR):
            return
        c = load_transcription_corpus('test',self.transcription_morphemes_path,' ',['-','=','.'],trans_delimiter='.')

        self.assertEqual(c.lexicon['cab'].frequency, 2)

    def test_load_with_fm(self):
        if not os.path.exists(TEST_DIR):
            return
        c = load_transcription_corpus('test',self.transcription_path,' ',
                    ['-','=','.'],trans_delimiter='.',
                    feature_system_path = self.full_feature_matrix_path)

        self.assertEqual(c.lexicon.specifier,load_binary(self.full_feature_matrix_path))

        self.assertEqual(c.lexicon['cab'].frequency, 1)

        self.assertEqual(c.lexicon.check_coverage(),[])

        c = load_transcription_corpus('test',self.transcription_path,' ',
                    ['-','=','.'],trans_delimiter='.',
                    feature_system_path = self.missing_feature_matrix_path)

        self.assertEqual(c.lexicon.specifier,load_binary(self.missing_feature_matrix_path))

        self.assertEqual(sorted(c.lexicon.check_coverage()),sorted(['b','c','d']))


class BinaryCorpusLoadTest(unittest.TestCase):
    def setUp(self):
        self.example_path = os.path.join(TEST_DIR,'example.corpus')

    def test_load(self):
        if not os.path.exists(TEST_DIR):
            return
        c = load_binary(self.example_path)

        example_c = create_unspecified_test_corpus()

        self.assertEqual(c,example_c)


class BinaryCorpusSaveTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(TEST_DIR):
            return
        self.corpus = create_unspecified_test_corpus()
        self.path = os.path.join(TEST_DIR,'testsave.corpus')

    def test_save(self):
        if not os.path.exists(TEST_DIR):
            return
        save_binary(self.corpus,self.path)

        c = load_binary(self.path)

        self.assertEqual(self.corpus,c)

class BinaryCorpusDownloadTest(unittest.TestCase):
    def setUp(self):
        self.name = 'example'
        self.path = os.path.join(TEST_DIR,'testdownload.corpus')
        self.example_path = os.path.join(TEST_DIR,'example.corpus')

    def test_download(self):
        if not os.path.exists(TEST_DIR):
            return
        download_binary(self.name,self.path)

        c = load_binary(self.path)

        example_c = load_binary(self.example_path)
        self.assertEqual(c,example_c)

class FeatureMatrixCsvTest(unittest.TestCase):
    def setUp(self):
        self.basic_path = os.path.join(TEST_DIR,'test_feature_matrix.txt')
        self.missing_value_path = os.path.join(TEST_DIR,'test_feature_matrix_missing_value.txt')
        self.extra_feature_path = os.path.join(TEST_DIR,'test_feature_matrix_extra_feature.txt')

    def test_basic(self):
        if not os.path.exists(TEST_DIR):
            return
        self.assertRaises(DelimiterError,load_feature_matrix_csv,'test',self.basic_path,' ')
        fm = load_feature_matrix_csv('test',self.basic_path,',')

        self.assertEqual(fm.name,'test')
        self.assertEqual(fm['a','feature1'], '+')

    def test_missing_value(self):
        if not os.path.exists(TEST_DIR):
            return
        fm = load_feature_matrix_csv('test',self.missing_value_path,',')

        self.assertEqual(fm['d','feature2'],'n')

    def test_extra_feature(self):
        if not os.path.exists(TEST_DIR):
            return
        fm = load_feature_matrix_csv('test',self.extra_feature_path,',')

        self.assertRaises(KeyError,fm.__getitem__,('a','feature3'))

class BinaryFeatureMatrixSaveTest(unittest.TestCase):
    def setUp(self):
        self.basic_path = os.path.join(TEST_DIR,'test_feature_matrix.txt')
        self.basic_save_path = os.path.join(TEST_DIR,'basic.feature')
        self.missing_segment_path = os.path.join(TEST_DIR,'test_feature_matrix_missing_segment.txt')
        self.missing_save_path = os.path.join(TEST_DIR,'missing_segments.feature')

    def test_save(self):
        if not os.path.exists(TEST_DIR):
            return
        fm = load_feature_matrix_csv('test',self.basic_path,',')
        save_binary(fm,self.basic_save_path)
        saved_fm = load_binary(self.basic_save_path)
        self.assertEqual(fm,saved_fm)

        fm = load_feature_matrix_csv('test',self.missing_segment_path,',')
        save_binary(fm,self.missing_save_path)
        saved_fm = load_binary(self.missing_save_path)
        self.assertEqual(fm,saved_fm)



if __name__ == '__main__':
    if os.path.exists(TEST_DIR):
        unittest.main()
