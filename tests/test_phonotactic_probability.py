import unittest

import sys
import os

from corpustools.phonoprob.phonotactic_probability import phonotactic_probability_vitevitch
from corpustools.contextmanagers import CanonicalVariantContext, MostFrequentVariantContext, WeightedVariantContext

def test_basic_corpus_probs(unspecified_test_corpus):
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        prob_dict = c.get_phone_probs(1, log_count = False, probability=False)

    expected = {(('i',), 1):3, (('s',), 2):3, (('ʃ',), 6):1, (('t',), 3):1,
                (('m',), 3):1, (('s',), 0):1, (('o',), 1):1, (('u',), 1):2,
                (('u',), 2):1, (('n',), 4):1, (('o',), 3):3, (('ʃ',), 2):4,
                (('m',), 4):3, (('n',), 0):1, (('t',), 0):5, (('ʃ',), 0):4,
                (('e',), 3):1, (('ɑ',), 5):2, (('m',), 0):2, (('t',), 1):1,
                (('u',), 7):1, (('t',), 4):1, (('ɑ',), 1):7, (('i',), 7):1,
                (('t',), 2):3, (('s',), 6):1, (('ɑ',), 3):4, (('i',), 5):3,
                (('e',), 0):1, (('i',), 3):3, (('n',), 1):1, (('n',), 2):1,
                (('ɑ',), 0):1, (('ɑ',), 4):2, (('e',), 2):1,
                'total':{0: 15, 1: 15, 2: 13, 3: 13, 4: 7, 5: 5, 6: 2, 7: 2}}
    for k,v in expected.items():
        if k == 'total':
            for k2, v2 in v.items():
                assert(prob_dict[k][k2] == v2)
            continue
        assert(prob_dict[k] == v)

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        prob_dict = c.get_phone_probs(1, log_count = False, probability=True)
    for k,v in expected.items():
        if k == 'total':
            continue
        assert(prob_dict[k] == v / expected['total'][k[1]])

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        prob_dict = c.get_phone_probs(1, log_count = True, probability=True)
    expected = {(('ɑ',), 0):0.0587828456,(('t',), 1):0.0587828456, #atema
                (('e',), 2):0.0668038019,(('m',), 3):0.0668038019,
                (('ɑ',), 4):0.2544134544,
                (('e',), 0):0.0587828456,(('n',), 1):0.0587828456, #enuta
                (('u',), 2):0.0668038019,(('t',), 3):0.0668038019,
                (('t',), 0):0.4333449434, (('ɑ',), 1):0.4373852679,#ta
                (('m',), 0):0.0564463785,(('t',), 2):0.0928330493,  #mata
                (('ɑ',), 3):0.1657810293,
                (('n',), 0):0.0169920531 #nata
                }
    for k,v in expected.items():
        assert(abs(prob_dict[k] - v) < 0.0001)

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        prob_dict = c.get_phone_probs(2, log_count = True, probability=True)
    expected = {(('ɑ','t'), 0):0.0587828456,(('t','e'), 1):0.0668038019, #atema
                (('e','m'), 2):0.0668038019,(('m','ɑ'), 3):0.1272067272,
                (('e','n'), 0):0.0587828456,(('n','u'), 1):0.0668038019, #enuta
                (('u','t'), 2):0.0668038019,(('t','ɑ'), 3):0.1272067272,
                (('t','ɑ'), 0):0.1507780332,#ta
                (('m','ɑ'), 0):0.0564463785,(('ɑ','t'), 1):0.0928330493,  #mata
                (('t','ɑ'), 2):0.0386212588,
                (('n','ɑ'), 0):0.0169920531 #nata
                }
    #print(list(prob_dict.keys()))
    for k,v in expected.items():
        assert(abs(prob_dict[k] - v) < 0.0001)

#Not passing around a word object!

def test_basic_phonoprob(unspecified_test_corpus):
    expected = {'atema':0.1011173499,
                'enuta':0.1011173499,
                'ta':0.4353651056,
                'mata':0.1881114313,
                'nata':0.1782478499}
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        for k,v in expected.items():
            res = phonotactic_probability_vitevitch(c, unspecified_test_corpus.find(k), 'unigram')
        assert(abs(v - res) < 0.0001)

    expected = {'atema':0.0798992942,
                'enuta':0.0798992942,
                'ta':0.1507780332,
                'mata':0.0626335622,
                'nata':0.0494821204}
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        for k,v in expected.items():
            res = phonotactic_probability_vitevitch(c, unspecified_test_corpus.find(k), 'bigram')
        assert(abs(v - res) < 0.0001)

#def test_iphod(self):
    #return
    #if not os.path.exists(TEST_DIR):
        #return
    #from corpustools.corpus.io import load_corpus_csv
    #corpus = load_corpus_csv('iphod', os.path.join(TEST_DIR,'IPhOD2.txt'),'\t')
    #print(list(map(str,corpus.attributes)))
    #for word in corpus:
        ##unigram = phonotactic_probability_vitevitch(corpus,word,'transcription','type','unigram')
        ##self.assertAlmostEqual(getattr(word,'unspospav'),unigram)
        ##biphone = phonotactic_probability_vitevitch(corpus,word,'transcription','type','bigram')
        ##self.assertAlmostEqual(getattr(word,'unsbpav'),biphone)
        #unigram = phonotactic_probability_vitevitch(corpus,word,'transcription','token','unigram')
        #self.assertAlmostEqual(getattr(word,'unslpospav'),unigram,places=4)
        #biphone = phonotactic_probability_vitevitch(corpus,word,'transcription','token','bigram')
        #self.assertAlmostEqual(getattr(word,'unslbpav'),biphone,places=4)

if __name__ == '__main__':
    unittest.main()
