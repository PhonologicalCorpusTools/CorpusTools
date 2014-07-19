import unittest

try:
    from corpustools.corpus.tests.classes import create_unspecified_test_corpus
except ImportError:
    import sys
    import os
    test_dir = os.path.dirname(os.path.abspath(__file__))
    corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(corpustools_path)
    from corpustools.corpus.tests.classes import create_unspecified_test_corpus
from corpustools.funcload.functional_load import minpair_fl, deltah_fl
from corpustools.corpus.classes import Segment


class NeutralizeTest(unittest.TestCase):
    pass

class MinPairsTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_non_minimal_pair_corpus(self):
        calls = [({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ')],
                        'frequency_cutoff':0,
                        'relative_count':True},0.125),
                ({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ')],
                        'frequency_cutoff':0,
                        'relative_count':False},1),
                ({'corpus': self.corpus,
                        'segment_pairs':[('m','n')],
                        'frequency_cutoff':0,
                        'relative_count':True},0.11111),
                ({'corpus': self.corpus,
                        'segment_pairs':[('m','n')],
                        'frequency_cutoff':0,
                        'relative_count':False},1),
                ({'corpus': self.corpus,
                        'segment_pairs':[('e','o')],
                        'frequency_cutoff':0,
                        'relative_count':True},0),
                ({'corpus': self.corpus,
                        'segment_pairs':[('e','o')],
                        'frequency_cutoff':0,
                        'relative_count':False},0),

                ({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ')],
                        'frequency_cutoff':3,
                        'relative_count':True},0.14286),
                ({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ')],
                        'frequency_cutoff':3,
                        'relative_count':False},1),
                ({'corpus': self.corpus,
                        'segment_pairs':[('m','n')],
                        'frequency_cutoff':3,
                        'relative_count':True},0),
                ({'corpus': self.corpus,
                        'segment_pairs':[('m','n')],
                        'frequency_cutoff':3,
                        'relative_count':False},0),
                ({'corpus': self.corpus,
                        'segment_pairs':[('e','o')],
                        'frequency_cutoff':3,
                        'relative_count':True},0),
                ({'corpus': self.corpus,
                        'segment_pairs':[('e','o')],
                        'frequency_cutoff':3,
                        'relative_count':False},0),

                ({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ'),
                                        ('m','n'),
                                        ('e','o')],
                        'frequency_cutoff':0,
                        'relative_count':True},0.14286),
                ({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ'),
                                        ('m','n'),
                                        ('e','o')],
                        'frequency_cutoff':0,
                        'relative_count':False},2),
                ({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ'),
                                        ('m','n'),
                                        ('e','o')],
                        'frequency_cutoff':3,
                        'relative_count':True},0.09091),
                ({'corpus': self.corpus,
                        'segment_pairs':[('s','ʃ'),
                                        ('m','n'),
                                        ('e','o')],
                        'frequency_cutoff':3,
                        'relative_count':False},1)]

        for c,v in calls:
            msgcall = 'Call: {}\nExpected: {}\nActually got:{}'.format(c,v,minpair_fl(**c))
            self.assertTrue(abs(minpair_fl(**c)-v) < 0.0001,msg=msgcall)

class DeltaHTest(unittest.TestCase):
    def setUp(self):
        self.corpus = create_unspecified_test_corpus()

    def test_non_minimal_pair_corpus(self):
        calls = [({'corpus': self.corpus,
                    'segment_pairs':[('s','ʃ')],
                    'frequency_cutoff':0,
                    'type_or_token':'type'},0.13333),
                ({'corpus': self.corpus,
                    'segment_pairs':[('s','ʃ')],
                    'frequency_cutoff':0,
                    'type_or_token':'token'},0.24794),
                ({'corpus': self.corpus,
                    'segment_pairs':[('m','n')],
                    'frequency_cutoff':0,
                    'type_or_token':'type'},0.13333),
                ({'corpus': self.corpus,
                    'segment_pairs':[('m','n')],
                    'frequency_cutoff':0,
                    'type_or_token':'token'},0.00691),
                ({'corpus': self.corpus,
                    'segment_pairs':[('e','o')],
                    'frequency_cutoff':0,
                    'type_or_token':'type'},0),
                ({'corpus': self.corpus,
                    'segment_pairs':[('e','o')],
                    'frequency_cutoff':0,
                    'type_or_token':'token'},0),

                ({'corpus': self.corpus,
                    'segment_pairs':[('s','ʃ')],
                    'frequency_cutoff':3,
                    'type_or_token':'type'},0.16667),
                ({'corpus': self.corpus,
                    'segment_pairs':[('s','ʃ')],
                    'frequency_cutoff':3,
                    'type_or_token':'token'},0.25053),
                ({'corpus': self.corpus,
                    'segment_pairs':[('m','n')],
                    'frequency_cutoff':3,
                    'type_or_token':'type'},0),
                ({'corpus': self.corpus,
                    'segment_pairs':[('m','n')],
                    'frequency_cutoff':3,
                    'type_or_token':'token'},0),
                ({'corpus': self.corpus,
                    'segment_pairs':[('e','o')],
                    'frequency_cutoff':3,
                    'type_or_token':'type'},0),
                ({'corpus': self.corpus,
                    'segment_pairs':[('e','o')],
                    'frequency_cutoff':3,
                    'type_or_token':'token'},0),

                ({'corpus': self.corpus,
                    'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'frequency_cutoff':0,
                    'type_or_token':'type'},0.26667),
                ({'corpus': self.corpus,
                    'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'frequency_cutoff':0,
                    'type_or_token':'token'},0.25485),

                ({'corpus': self.corpus,
                    'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'frequency_cutoff':3,
                    'type_or_token':'type'},0.16667),
                ({'corpus': self.corpus,
                    'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'frequency_cutoff':3,
                    'type_or_token':'token'},0.25053),]


        for c,v in calls:
            msgcall = 'Call: {}\nExpected: {}\nActually got:{}'.format(c,v,deltah_fl(**c))
            self.assertTrue(abs(deltah_fl(**c)-v) < 0.0001,msg=msgcall)



if __name__ == '__main__':
    unittest.main()
