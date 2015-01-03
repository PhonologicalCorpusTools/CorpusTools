import unittest

import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0, corpustools_path)
from corpustools.corpus.tests.lexicon_test import create_unspecified_test_corpus

from corpustools.phonoprob.phonotactic_probability import phonotactic_probability_vitevitch

TEST_DIR = r'C:\Users\michael\Documents\Data\Iphod'

class NeighDenTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_basic_corpus(self):
        prob_dict = self.corpus.get_phone_probs('transcription','type',1,log_count = False,probability=False)
        print(prob_dict)
        print(prob_dict['total'])
        #calls = [({'corpus': self.corpus,
                        #'query':'mata',
                        #'max_distance':1},1.0),
                #({'corpus': self.corpus,
                        #'query':'nata',
                        #'max_distance':2},3.0)]
        #for c,v in calls:
            #result = neighborhood_density(**c)
            #msgcall = 'Call: {}\nExpected: {}\nActually got:{}'.format(c,v,result)
            #self.assertTrue(abs(result[0]-v) < 0.0001,msg=msgcall)

    def test_iphod(self):
        if not os.path.exists(TEST_DIR):
            return
        from corpustools.corpus.io import load_corpus_csv
        corpus = load_corpus_csv('iphod', os.path.join(TEST_DIR,'IPhOD2.txt'),'\t')
        print(list(map(str,corpus.attributes)))
        for word in corpus:
            #unigram = phonotactic_probability_vitevitch(corpus,word,'transcription','type','unigram')
            #self.assertAlmostEqual(getattr(word,'unspospav'),unigram)
            #biphone = phonotactic_probability_vitevitch(corpus,word,'transcription','type','bigram')
            #self.assertAlmostEqual(getattr(word,'unsbpav'),biphone)
            unigram = phonotactic_probability_vitevitch(corpus,word,'transcription','token','unigram')
            self.assertAlmostEqual(getattr(word,'unslpospav'),unigram,places=4)
            biphone = phonotactic_probability_vitevitch(corpus,word,'transcription','token','bigram')
            self.assertAlmostEqual(getattr(word,'unslbpav'),biphone,places=4)

if __name__ == '__main__':
    unittest.main()
