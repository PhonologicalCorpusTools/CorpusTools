

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
        self.basic_info = [{'spelling':'a','transcription':['a','b'],'frequency':32.0},
                            {'spelling':'b','transcription':['a','c'],'frequency':32.0},
                            {'spelling':'c','transcription':['c','a','b'],'frequency':32.0},
                            {'spelling':'d','transcription':['a','d'],'frequency':32.0},]


        self.homograph_info = [{'spelling':'a','transcription':['a','b'],'frequency':32.0},
                            {'spelling':'a','transcription':['a','c'],'frequency':32.0},
                            {'spelling':'c','transcription':['c','a','b'],'frequency':32.0},
                            {'spelling':'d','transcription':['a','d'],'frequency':32.0},]

    def test_basic(self):
        corpus = Corpus('test')
        for w in self.basic_info:
            self.assertRaises(KeyError,corpus.find,w['spelling'],True)
            corpus.add_word(Word(**w))
            self.assertEqual(corpus[w['spelling']],Word(**w))
            self.assertEqual(corpus.find(w['spelling']),Word(**w))
            self.assertTrue(w['spelling'] in corpus)

        self.assertEqual(corpus.inventory,{'#':Segment('#'),
                                        'a':Segment('a'),
                                        'b':Segment('b'),
                                        'c':Segment('c'),
                                        'd':Segment('d')})


        self.assertEqual(corpus.orthography,{'#','a','b','c','d'})

    def test_homographs(self):
        corpus = Corpus('test')
        for w in self.homograph_info:
            corpus.add_word(Word(**w))


        #Error, should find return an iterable of homographs?
        self.assertEqual([x.spelling for x in corpus.find('a')],['a','a'])



class WordTest(unittest.TestCase):
    def setUp(self):
        self.basic = {'spelling':'test',
                    'transcription':['a','b','c','d'],
                    'frequency':'14.0'}

        self.tiered = {'spelling':'testing',
                    'transcription':['a','b','c','d','e','f','g'],
                    'tier1':['b','e'],
                    'tier2':['a','c','e','f','g'],
                    'frequency':'28.0'}

        self.extra = {'spelling':'test',
                    'transcription':['a','b','c','d'],
                    'frequency':'14.0',
                    'num_sylls':'3.0',
                    'some_other_label':'something'}

        self.empty = {}

        self.trans_only = {'transcription':['a','b','c','d'],
                    'frequency':'14.0'}

        self.spelling_only = {'spelling':'test',
                    'frequency':'14.0'}

        self.no_freq = {'spelling':'test',
                    'transcription':['a','b','c','d']}

    def test_word_init(self):
        t = Word(**self.basic)
        self.assertEqual(t.spelling, self.basic['spelling'])
        self.assertEqual(t.frequency, float(self.basic['frequency']))

        self.assertRaises(AttributeError,getattr,t,'tier1')

    def test_basic_word(self):
        t = Word(**self.basic)
        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.basic['transcription']))

        self.assertEqual(t.frequency, float(self.basic['frequency']))

        self.assertEqual(t.spelling, self.basic['spelling'])

        self.assertRaises(AttributeError,getattr,t,'tier1')

    def test_tiered_word(self):
        t = Word(**self.tiered)

        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.tiered['transcription']))

        self.assertEqual(t.frequency, float(self.tiered['frequency']))

        self.assertEqual(t.spelling, self.tiered['spelling'])

        self.assertEqual(t.tier1,self.tiered['tier1'])

        self.assertEqual(t.tier2,self.tiered['tier2'])

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

        self.assertEqual(t.spelling, 'abcd')

        self.assertRaises(AttributeError,getattr,t,'tier1')

    def test_spelling_only_word(self):
        t = Word(**self.spelling_only)
        self.assertEqual(t.get_transcription_string(),None)
        self.assertEqual(t.transcription,None)

        self.assertEqual(t.frequency, float(self.spelling_only['frequency']))

        self.assertEqual(t.spelling, self.spelling_only['spelling'])

        self.assertRaises(AttributeError,getattr,t,'tier1')

    def test_no_freq_word(self):
        t = Word(**self.no_freq)
        self.assertEqual(t.get_transcription_string(),
                        '.'.join(self.no_freq['transcription']))

        self.assertRaises(AttributeError,getattr,t,'frequency')
        #self.assertEqual(t.frequency, None)

        self.assertEqual(t.spelling, self.no_freq['spelling'])

        self.assertRaises(AttributeError,getattr,t,'tier1')

class FeatureMatrixTest(unittest.TestCase):
    def setUp(self):
        self.basic_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+','feature2':'-'},
                            {'symbol':'c','feature1':'-','feature2':'+'},
                            {'symbol':'d','feature1':'-','feature2':'-'}]

        self.dots_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+','feature2':'.'},
                            {'symbol':'c','feature1':'-','feature2':'+'},
                            {'symbol':'d','feature1':'-','feature2':'.'}]

        self.missing_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+'},
                            {'symbol':'c','feature1':'-','feature2':'+'},
                            {'symbol':'d','feature1':'-','feature2':'-'}]

        self.missing_with_default_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+'},
                            {'symbol':'c','feature1':'-','feature2':'+'},
                            {'symbol':'d','feature1':'-','feature2':'n'}]

        self.missing_dots_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+'},
                            {'symbol':'c','feature1':'-','feature2':'+'},
                            {'symbol':'d','feature1':'-','feature2':'.'}]

    def test_basic(self):
        fm = FeatureMatrix('test',self.basic_info)
        self.assertTrue(fm.name == 'test')

        self.assertEqual(fm.get_features(), ['feature1','feature2'])
        self.assertEqual(fm.get_feature_list(), ['feature1','feature2'])

        self.assertEqual(fm.get_possible_values(),{'+','-'})

        #fails, should be sorted list?
        self.assertEqual(sorted(fm.get_segments()),sorted(['','#','a','b','c','d']))

    def test_dots(self):
        fm = FeatureMatrix('test',self.dots_info)


        self.assertEqual(fm.get_features(), ['feature1','feature2'])
        self.assertEqual(fm.get_feature_list(), ['feature1','feature2'])

        self.assertEqual(fm.get_possible_values(),{'+','-','.'})

        self.assertEqual(fm['b','feature2'],'.')

        #Fails, should be sorted list of features? Or set of features? Would need to be hashed then
        self.assertEqual(fm['b']['feature2'],'.')

    def test_missing(self):
        fm = FeatureMatrix('test',self.missing_info)

        self.assertEqual(fm.get_features(), ['feature1','feature2'])

        self.assertEqual(fm.get_possible_values(),{'+','-'})

        #Error, there should be a default default value?
        fm.validate()

    def test_missing_with_default(self):
        fm = FeatureMatrix('test',self.missing_with_default_info)

        self.assertEqual(fm.get_features(), ['feature1','feature2'])

        self.assertEqual(fm.get_possible_values(),{'+','-','n'})

        fm.validate()

        self.assertEqual(fm['b','feature2'], 'n')

    def test_add_segment(self):
        fm = FeatureMatrix('test',self.basic_info)

        fm.add_segment('e',{'feature1':'+','feature2':'-'})

        self.assertEqual(fm['e','feature1'],'+')

        #Fails, need to raise exception if the added segment contains a feature that no other segment has
        self.assertRaises(AttributeError,fm.add_segment,'e',{'feature1':'+','feature3':'-'})

    def test_add_feature(self):

        fm = FeatureMatrix('test',self.missing_with_default_info)
        fm.add_feature('feature3')

        self.assertEqual(fm['a','feature3'], 'n')

        fm = FeatureMatrix('test',self.basic_info)

        #Error, no default value
        fm.add_feature('feature3')

class CorpusFeatureMatrixTest(unittest.TestCase):
    def setUp(self):
        self.corpus_basic_info = [{'spelling':'a','transcription':['a','b'],'frequency':32.0},
                            {'spelling':'b','transcription':['a','b'],'frequency':32.0},
                            {'spelling':'c','transcription':['c','a','b'],'frequency':32.0},
                            {'spelling':'d','transcription':['a','d'],'frequency':32.0},]

        self.feature_basic_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+','feature2':'-'},
                            {'symbol':'c','feature1':'-','feature2':'+'},
                            {'symbol':'d','feature1':'-','feature2':'-'}]

        self.feature_no_d_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+','feature2':'-'},
                            {'symbol':'c','feature1':'-','feature2':'+'}]


    def test_basic(self):
        corpus = Corpus('test')
        for w in self.corpus_basic_info:
            corpus.add_word(Word(**w))

        fm = FeatureMatrix('test',self.feature_basic_info)

        corpus.set_feature_matrix(fm)

        self.assertEqual(corpus['a'].transcription[0].features,{'feature1':'+','feature2':'+'})


    def test_coverage(self):
        corpus = Corpus('test')
        for w in self.corpus_basic_info:
            corpus.add_word(Word(**w))

        fm = FeatureMatrix('test',self.feature_no_d_info)

        corpus.set_feature_matrix(fm)

        self.assertEqual(corpus.check_coverage(),['d'])


    def test_add_tier(self):
        corpus = Corpus('test')
        for w in self.corpus_basic_info:
            corpus.add_word(Word(**w))

        fm = FeatureMatrix('test',self.feature_basic_info)

        corpus.set_feature_matrix(fm)

        corpus.add_tier('t',['+feature1'])

        self.assertEqual(corpus['d'].t, [corpus['d'].transcription[0]])

        corpus.remove_tier('t')

        self.assertRaises(AttributeError,getattr,corpus['d'],'t')


class EnvironmentTest(unittest.TestCase):
    pass

class SegmentTest(unittest.TestCase):
    pass

class FeatureTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
