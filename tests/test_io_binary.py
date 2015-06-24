import pytest
import os

from corpustools.corpus.io.binary import download_binary, save_binary, load_binary

def test_save(export_test_dir, unspecified_test_corpus):
    save_path = os.path.join(export_test_dir, 'testsave.corpus')
    save_binary(unspecified_test_corpus,save_path)

    c = load_binary(save_path)

    assert(unspecified_test_corpus == c)


#class BinaryCorpusLoadTest(unittest.TestCase):
    #def setUp(self):
        #self.example_path = os.path.join(TEST_DIR,'example.corpus')

    #def test_load(self):
        #return
        #if not os.path.exists(TEST_DIR):
            #return
        #c = load_binary(self.example_path)

        #example_c = create_unspecified_test_corpus()

        #self.assertEqual(c,example_c)

#class BinaryFeatureMatrixSaveTest(unittest.TestCase):
    #def setUp(self):
        #self.basic_path = os.path.join(TEST_DIR,'test_feature_matrix.txt')
        #self.basic_save_path = os.path.join(TEST_DIR,'basic.feature')
        #self.missing_segment_path = os.path.join(TEST_DIR,'test_feature_matrix_missing_segment.txt')
        #self.missing_save_path = os.path.join(TEST_DIR,'missing_segments.feature')

    #def test_save(self):
        #if not os.path.exists(TEST_DIR):
            #return
        #fm = load_feature_matrix_csv('test',self.basic_path,',')
        #save_binary(fm,self.basic_save_path)
        #saved_fm = load_binary(self.basic_save_path)
        #self.assertEqual(fm,saved_fm)

        #fm = load_feature_matrix_csv('test',self.missing_segment_path,',')
        #save_binary(fm,self.missing_save_path)
        #saved_fm = load_binary(self.missing_save_path)
        #self.assertEqual(fm,saved_fm)
