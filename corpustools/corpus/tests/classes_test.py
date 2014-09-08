

import unittest
import os
try:
    from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix,Segment)
except ImportError:
    import sys

    test_dir = os.path.dirname(os.path.abspath(__file__))
    corpustools_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
    sys.path.append(corpustools_path)
    from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix,Segment)

def create_unspecified_test_corpus():
    corpus_data = [{'spelling':'atema','transcription':['ɑ','t','e','m','ɑ'],'frequency':11.0},
                    {'spelling':'enuta','transcription':['e','n','u','t','ɑ'],'frequency':11.0},
                    {'spelling':'mashomisi','transcription':['m','ɑ','ʃ','o','m','i','s','i'],'frequency':5.0},
                    {'spelling':'mata','transcription':['m','ɑ','t','ɑ'],'frequency':2.0},
                    {'spelling':'nata','transcription':['n','ɑ','t','ɑ'],'frequency':2.0},
                    {'spelling':'sasi','transcription':['s','ɑ','s','i'],'frequency':139.0},
                    {'spelling':'shashi','transcription':['ʃ','ɑ','ʃ','i'],'frequency':43.0},
                    {'spelling':'shisata','transcription':['ʃ','i','s','ɑ','t','ɑ'],'frequency':3.0},
                    {'spelling':'shushoma','transcription':['ʃ','u','ʃ','o','m','ɑ'],'frequency':126.0},
                    {'spelling':'ta','transcription':['t','ɑ'],'frequency':67.0},
                    {'spelling':'tatomi','transcription':['t','ɑ','t','o','m','i'],'frequency':7.0},
                    {'spelling':'tishenishu','transcription':['t','i','ʃ','e','n','i','ʃ','u'],'frequency':96.0},
                    {'spelling':'toni','transcription':['t','o','n','i'],'frequency':33.0},
                    {'spelling':'tusa','transcription':['t','u','s','ɑ'],'frequency':32.0},
                    {'spelling':'ʃi','transcription':['ʃ','i'],'frequency':2.0}]
    corpus = Corpus('test')
    for w in corpus_data:
        corpus.add_word(Word(**w))
    return corpus

def create_specified_test_corpus():
    corpus = create_unspecified_test_corpus()
    fm_input = [{'symbol':'ɑ','EXTRA':'-','LONG':'-','ant':'-','back':'+','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'n','low':'+','mv_glot_cl':'n','nasal':'-','round':'-','son':'+',
                'strid':'-','tense':'-','voc':'+','voice':'+'},
                {'symbol':'u','EXTRA':'-','LONG':'-','ant':'-','back':'+','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'+',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'-','round':'+','son':'+',
                'strid':'-','tense':'+','voc':'+','voice':'+'},
                {'symbol':'o','EXTRA':'-','LONG':'-','ant':'-','back':'+','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'-','round':'+','son':'+',
                'strid':'-','tense':'+','voc':'+','voice':'+'},
                {'symbol':'e','EXTRA':'-','LONG':'-','ant':'-','back':'-','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'+',
                'strid':'-','tense':'+','voc':'+','voice':'+'},
                {'symbol':'s','EXTRA':'-','LONG':'-','ant':'+','back':'-','cont':'+','cor':'+',
                'del_rel':'n','distr':'-','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'-','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'-',
                'strid':'+','tense':'.','voc':'-','voice':'-'},
                {'symbol':'m','EXTRA':'-','LONG':'-','ant':'+','back':'-','cont':'-','cor':'-',
                'del_rel':'-','distr':'+','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'+','round':'-','son':'+',
                'strid':'-','tense':'-','voc':'-','voice':'+'},
                {'symbol':'i','EXTRA':'-','LONG':'-','ant':'-','back':'-','cont':'+','cor':'-',
                'del_rel':'n','distr':'n','glot_cl':'-','hi_subgl_pr':'-','high':'+',
                'lat':'n','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'+',
                'strid':'-','tense':'+','voc':'+','voice':'+'},
                {'symbol':'n','EXTRA':'-','LONG':'-','ant':'+','back':'-','cont':'-','cor':'+',
                'del_rel':'-','distr':'-','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'-','low':'-','mv_glot_cl':'n','nasal':'+','round':'-','son':'+',
                'strid':'-','tense':'-','voc':'-','voice':'+'},
                {'symbol':'ʃ','EXTRA':'-','LONG':'-','ant':'-','back':'-','cont':'+','cor':'+',
                'del_rel':'n','distr':'+','glot_cl':'-','hi_subgl_pr':'-','high':'+',
                'lat':'-','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'-',
                'strid':'+','tense':'.','voc':'-','voice':'-'},
                {'symbol':'t','EXTRA':'-','LONG':'-','ant':'+','back':'-','cont':'-','cor':'+',
                'del_rel':'-','distr':'-','glot_cl':'-','hi_subgl_pr':'-','high':'-',
                'lat':'-','low':'-','mv_glot_cl':'n','nasal':'-','round':'-','son':'-',
                'strid':'-','tense':'.','voc':'-','voice':'-'}]
    fm = FeatureMatrix('spe',fm_input)
    corpus.set_feature_matrix(fm)
    return corpus


class CorpusTest(unittest.TestCase):
    def setUp(self):
        self.corpus_data = [{'spelling':'tusa','transcription':['t','u','s','ɑ'],'frequency':32.0}]

    def test_load(self):
        corpus = Corpus('test')
        for w in self.corpus_data:
            self.assertRaises(KeyError,corpus.find,w['spelling'],True)
            corpus.add_word(Word(**w))
            self.assertEqual(corpus[w['spelling']],Word(**w))
            self.assertEqual(corpus.find(w['spelling']),Word(**w))
            self.assertTrue(w['spelling'] in corpus)

        self.assertEqual(corpus.inventory,{'#':Segment('#'),
                                        't':Segment('t'),
                                        'u':Segment('u'),
                                        's':Segment('s'),
                                        'ɑ':Segment('ɑ')})


        self.assertEqual(corpus.orthography,{'#','t','u','s','a'})

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

        self.assertRaises(AttributeError,getattr,t,'vowel_tier')

    def test_basic_word(self):
        t = Word(**self.basic)
        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.basic['transcription']))

        self.assertEqual(t.frequency, float(self.basic['frequency']))

        self.assertEqual(t.spelling, self.basic['spelling'])

        self.assertRaises(AttributeError,getattr,t,'vowel_tier')

    def test_tiered_word(self):
        t = Word(**self.tiered)

        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.tiered['transcription']))

        self.assertEqual(t.frequency, float(self.tiered['frequency']))

        self.assertEqual(t.spelling, self.tiered['spelling'])

        self.assertEqual(t.vowel_tier,self.tiered['vowel_tier'])

        self.assertEqual(t.cons_tier,self.tiered['cons_tier'])

    def test_extra_word(self):
        t = Word(**self.extra)

        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.extra['transcription']))

        self.assertEqual(t.spelling, self.extra['spelling'])

        self.assertEqual(t.frequency, float(self.extra['frequency']))

        self.assertEqual(t.num_sylls, float(self.extra['num_sylls']))

        self.assertEqual(t.some_other_label, self.extra['some_other_label'])

    def test_empty_word(self):
        pass

    def test_trans_only_word(self):
        t = Word(**self.trans_only)
        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.trans_only['transcription']))

        self.assertEqual(t.frequency, float(self.trans_only['frequency']))

        self.assertEqual(t.spelling, None)

        self.assertRaises(AttributeError,getattr,t,'vowel_tier')

    def test_spelling_only_word(self):
        t = Word(**self.spelling_only)
        self.assertEqual(t.get_transcription_string(),None)
        self.assertEqual(t.transcription,None)

        self.assertEqual(t.frequency, float(self.spelling_only['frequency']))

        self.assertEqual(t.spelling, self.spelling_only['spelling'])

        self.assertRaises(AttributeError,getattr,t,'vowel_tier')

    def test_no_freq_word(self):
        t = Word(**self.no_freq)
        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.no_freq['transcription']))

        self.assertRaises(AttributeError,getattr,t,'frequency')
        #self.assertEqual(t.frequency, None)

        self.assertEqual(t.spelling, self.no_freq['spelling'])

        self.assertRaises(AttributeError,getattr,t,'vowel_tier')

if __name__ == '__main__':
    unittest.main()
