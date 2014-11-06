import unittest

import sys
import os
test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
print(corpustools_path)
sys.path.insert(0, corpustools_path)
from corpustools.corpus.tests.classes_test import create_unspecified_test_corpus

from corpustools.prod.pred_of_dist import check_envs, calc_prod, count_segs



class CountSegsTest(unittest.TestCase):
    pass

class CheckEnvsTest(unittest.TestCase):
    pass

class MatchEnvTest(unittest.TestCase):
    pass

class FormalizeEnvTest(unittest.TestCase):
    pass

class ProdAllEnvsTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_specified_test_corpus()



class ProdTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_specified_test_corpus()

    def test_prod_token(self):
        seg1 = 's'
        seg2 = 'ʃ'
        expected = {"_[-voc]":0.0,
                    "_[+voc,+high]":0.9321115676166747,
                    "_[+voc,-high]":0.9660096062568557,
                    "_#":0.0}
        env_list = list(expected.keys())
        expected["AVG"] = 0.9496532099899153
        type_or_token = 'token'
        tier = 'transcription'
        result = calc_prod(self.corpus,seg1,seg2,env_list,tier, type_or_token)
        for k,v in result.items():
            k = str(k).replace("'",'').replace(' ','')
            self.assertAlmostEqual(expected[k],v)

    def test_prod_type(self):
        seg1 = 's'
        seg2 = 'ʃ'
        expected = {"_[-voc]":0.0,
                    "_[+voc,+high]":0.863120568566631,
                    "_[+voc,-high]":0.9852281360342515,
                    "_#":0.0}
        env_list = list(expected.keys())
        expected["AVG"] = 0.9241743523004413
        type_or_token = 'type'
        tier = 'transcription'
        result = calc_prod(self.corpus,seg1,seg2,env_list,tier, type_or_token,all_info=False)
        for k,v in result.items():
            k = str(k).replace("'",'').replace(' ','')
            self.assertAlmostEqual(expected[k],v)


if __name__ == '__main__':
    unittest.main()

