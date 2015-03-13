

from numpy import array
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,corpustools_path)
from corpustools.acousticsim.io import load_path_mapping

TEST_DIR = r'C:\Users\michael\Dropbox\Measuring_Phonological_Relations\Computational\CorpusTools_test_files\Acoustic_similarity'

class IOTest(unittest.TestCase):
    def setUp(self):
        self.valid_path = os.path.join(TEST_DIR,'mapping_test.txt')
        self.invalid_path = os.path.join(TEST_DIR,'invalid_mapping_test.txt')

    def test_valid(self):
        return
        mapping = load_path_mapping(self.valid_path)
        for line in mapping:
            self.assertEqual(len(line),2)

    def test_invalid(self):
        return
        self.assertRaises(OSError,load_path_mapping,self.invalid_path)

if __name__ == '__main__':
    unittest.main()
