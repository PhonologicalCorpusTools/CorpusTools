
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,corpustools_path)

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix,
                                        Environment, EnvironmentFilter, Transcription,
                                        WordToken, Discourse, SpontaneousSpeechCorpus)

class WordTokenTest(unittest.TestCase):
    def setUp(self):
        self.word_tokens = [{'begin':0,'end':1,'spelling':'a','transcription':['a','b']},
                        {'begin':1,'end':2,'spelling':'c','transcription':['c','a','b']},
                        {'begin':2,'end':3,'spelling':'a','transcription':['a','b']},
                        {'begin':3,'end':4,'spelling':'d','transcription':['a','d']}]

        self.word_type_only = {'begin':0,'end':1,'word':Word(**{'spelling':'a','transcription':['a','b']})}

        self.word_type_and = {'begin':0,'end':1,'spelling':'a2','transcription':['a','b2'],
                            'word':Word(**{'spelling':'a','transcription':['a','b']})}

    def test_init(self):
        wt = WordToken(**self.word_type_only)
        self.assertEqual(wt.spelling,'a')
        self.assertEqual(str(wt.transcription),'a.b')

        wt = WordToken(**self.word_type_and)
        self.assertEqual(wt.spelling,'a2')
        self.assertEqual(str(wt.transcription),'a.b2')

    def test_duration(self):
        for wt in self.word_tokens:
            w = WordToken(**wt)
            self.assertEqual(w.duration, 1)

class DiscourseTest(unittest.TestCase):
    def setUp(self):
        self.word_tokens = [{'begin':0,'end':1,'word':Word(**{'spelling':'a','transcription':['a','b']})},
                        {'begin':1,'end':2,'word':Word(**{'spelling':'c','transcription':['c','a','b']})},
                        {'begin':2,'end':3,'word':Word(**{'spelling':'a','transcription':['a','b']})},
                        {'begin':3,'end':4,'word':Word(**{'spelling':'d','transcription':['a','d']})}]

    def test_init(self):
        d = Discourse()
        for wt in self.word_tokens:
            d.add_word(WordToken(**wt))

        #self.assertEqual(d[0].previous_token, None)
        #self.assertEqual(d[1].previous_token, d[0])

class SpontaneousSpeechCorpusTest(unittest.TestCase):
    def setUp(self):
        self.word_tokens = [{'Begin':0,'End':1,'lookup_spelling':'a','lookup_transcription':['a','b'],'Transcription':[{'symbol':'a'},{'symbol':'b'}]},
                        {'Begin':1,'End':2,'lookup_spelling':'c','lookup_transcription':['c','a','b'],'Transcription':[{'symbol':'a'}]},
                        {'Begin':2,'End':3,'lookup_spelling':'a','lookup_transcription':['a','b'], 'Transcription':[{'symbol':'a'}]},
                        {'Begin':3,'End':4,'lookup_spelling':'d','lookup_transcription':['a','d'],'Transcription':[{'symbol':'a'},{'symbol':'d'}]}]
    def test_init(self):
        corpus = SpontaneousSpeechCorpus('','')

        discourse_info = {'name':'',
                            }
        corpus.add_discourse(self.word_tokens, discourse_info)

        d = corpus.discourses['']
        self.assertEqual(d[0].previous_token, None)
        self.assertEqual(d[1].previous_token, d[0])
        self.assertEqual(d[2].previous_token, d[1])
        self.assertEqual(d[3].previous_token, d[2])

        self.assertEqual(d[0].following_token, d[1])
        self.assertEqual(d[1].following_token, d[2])
        self.assertEqual(d[2].following_token, d[3])
        self.assertEqual(d[3].following_token, None)

        self.assertEqual(d[0].wordtype.frequency,2)
        self.assertEqual(d[1].wordtype.frequency,1)

if __name__ == '__main__':
    unittest.main()
