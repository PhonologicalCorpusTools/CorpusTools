import unittest

try:
    from corpustools.corpus.tests.classes_test import create_specified_test_corpus
except ImportError:
    import sys
    import os
    test_dir = os.path.dirname(os.path.abspath(__file__))
    corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(corpustools_path)
    from corpustools.corpus.tests.classes_test import create_specified_test_corpus
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
        env_matches, missing_words, overlapping_words = check_envs(self.corpus,
                                                                    seg1,seg2,
                                                                    type_or_token,
                                                                    env_list,
                                                                    tier)
        results = calc_prod(self.corpus.name, tier, seg1, seg2, env_matches, type_or_token)
        #hack
        for line in results:
            key = line[4].replace("'",'').replace(' ',"")
            h = float(line[8])
            self.assertAlmostEqual(expected[key],h)

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
        env_matches, missing_words, overlapping_words = check_envs(self.corpus,
                                                                    seg1,seg2,
                                                                    type_or_token,
                                                                    env_list,
                                                                    tier)
        results = calc_prod(self.corpus.name, tier, seg1, seg2, env_matches, type_or_token)
        #hack
        for line in results:
            key = line[4].replace("'",'').replace(' ',"")
            h = float(line[8])
            self.assertAlmostEqual(expected[key],h)


if __name__ == '__main__':
    unittest.main()

