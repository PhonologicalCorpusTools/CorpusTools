import unittest

import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
print(corpustools_path)
sys.path.insert(0, corpustools_path)
from corpustools.corpus.tests.lexicon_test import create_specified_test_corpus

from corpustools.kl.kl import KullbackLeibler as KL


class KLTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_specified_test_corpus()

    def test_identical(self):
        #Test 1, things that are identical
        distance, seg1_entropy, seg2_entropy, ur, sr = KL(self.corpus, 's', 's')
        self.assertEqual(distance, 0.0)
        self.assertEqual(seg1_entropy, seg2_entropy)

    def test_allophones(self):
        #Test 2, things are supposed to be allophones
        distance, seg1_entropy, seg2_entropy, ur, sr = KL(self.corpus, 's', 'ʃ')
        self.assertAlmostEqual(distance, 0.15113518339295337)
        self.assertAlmostEqual(seg1_entropy, 0.035000140096702444)
        self.assertAlmostEqual(seg2_entropy, 0.06074393445793598)

    def test_pseudo_allophones(self):
        #Test 3, things that are allophones by coincidence
        distance, seg1_entropy, seg2_entropy, ur, sr = KL(self.corpus, 's', 'a')
        self.assertAlmostEqual(distance, 0.23231302100802534)
        self.assertAlmostEqual(seg1_entropy,0.03500014009670246)
        self.assertAlmostEqual(seg2_entropy, 0.07314589775440267)
        #self.assertEqual(ur,sr)#both should be None, to be fixed with features

    def test_default(self):
        #Test 4, things that have no assumed relationship
        distance, seg1_entropy, seg2_entropy, ur, sr = KL(self.corpus, 's', 'm')
        self.assertAlmostEqual(distance, 0.14186314747884132)
        self.assertAlmostEqual(seg1_entropy, 0.035000140096702444)
        self.assertAlmostEqual(seg2_entropy, 0.06074393445793598)

    def test_error(self):
        #Test 5, things not in the corpus
        self.assertRaises(ValueError,KL,self.corpus, 's', '!')


if __name__ == '__main__':
    unittest.main()

