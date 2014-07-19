

import unittest
import os
try:
    from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix)
except ImportError:
    import sys

    test_dir = os.path.dirname(os.path.abspath(__file__))
    corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(corpustools_path)
    from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix)

class WordTest(unittest.TestCase):
    def setUp(self):
        self.basic = {'spelling':'test',
                    'transcription':['T','EH','S','T'],
                    'frequency':'14.0'}

        self.tiered = {'spelling':'testing',
                    'transcription':['T','EH','S','T','IH','N','G'],
                    'vowel_tier':['EH','IH'],
                    'cons_tier':['T','S','T','N','G'],
                    'frequency':'28.0'}

        self.extra = {'spelling':'test',
                    'transcription':['T','EH','S','T'],
                    'frequency':'14.0',
                    'num_sylls':'3.0',
                    'some_other_label':'something'}

        self.empty = {}

        self.trans_only = {'transcription':['T','EH','S','T'],
                    'frequency':'14.0'}

        self.spelling_only = {'spelling':'test',
                    'frequency':'14.0'}

        self.no_freq = {'spelling':'test',
                    'transcription':['T','EH','S','T']}

    def test_word_init(self):
        t = Word(**self.basic)
        self.assertEqual(t.spelling, self.basic['spelling'])
        self.assertEqual(t.frequency, float(self.basic['frequency']))

    def test_word_properties(self):
        t = Word(**self.basic)
        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.basic['transcription']))

if __name__ == '__main__':
    unittest.main()
