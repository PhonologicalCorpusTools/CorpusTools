
import unittest
import os
import sys

import pdb

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix, Segment,
                                        Environment, EnvironmentFilter, Transcription,
                                        WordToken, Discourse)


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

        self.assertEqual(corpus.inventory._data,{'#':Segment('#'),
                                        'a':Segment('a'),
                                        'b':Segment('b'),
                                        'c':Segment('c'),
                                        'd':Segment('d')})

        #self.assertEqual(corpus.inventory,sorted(['#','a','b','c','d']))

    def test_homographs(self):
        return
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
        self.assertEqual(str(t.transcription),
                        '.'.join(self.basic['transcription']))

        self.assertEqual(t.frequency, float(self.basic['frequency']))

        self.assertEqual(t.spelling, self.basic['spelling'])

        self.assertRaises(AttributeError,getattr,t,'tier1')

    def test_tiered_word(self):
        t = Word(**self.tiered)

        self.assertEqual(str(t.transcription),
                        '.'.join(self.tiered['transcription']))

        self.assertEqual(t.frequency, float(self.tiered['frequency']))

        self.assertEqual(t.spelling, self.tiered['spelling'])

        self.assertEqual(t.tier1,self.tiered['tier1'])

        self.assertEqual(t.tier2,self.tiered['tier2'])

    def test_extra_word(self):
        t = Word(**self.extra)

        self.assertEqual(str(t.transcription),
                        '.'.join(self.extra['transcription']))

        self.assertEqual(t.spelling, self.extra['spelling'])

        self.assertEqual(t.frequency, float(self.extra['frequency']))

        self.assertEqual(t.num_sylls, float(self.extra['num_sylls']))

        self.assertEqual(t.some_other_label, self.extra['some_other_label'])

    def test_empty_word(self):
        pass

    def test_trans_only_word(self):
        t = Word(**self.trans_only)
        self.assertEqual(str(t.transcription),
                        '.'.join(self.trans_only['transcription']))

        self.assertEqual(t.frequency, float(self.trans_only['frequency']))

        self.assertEqual(t.spelling, 'abcd')

        self.assertRaises(AttributeError,getattr,t,'tier1')

    def test_spelling_only_word(self):
        t = Word(**self.spelling_only)
        self.assertEqual(t.transcription,None)

        self.assertEqual(t.frequency, float(self.spelling_only['frequency']))

        self.assertEqual(t.spelling, self.spelling_only['spelling'])

        self.assertRaises(AttributeError,getattr,t,'tier1')

    def test_no_freq_word(self):
        t = Word(**self.no_freq)
        self.assertEqual(str(t.transcription),
                        '.'.join(self.no_freq['transcription']))

        self.assertEqual(t.frequency, 0)

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

        self.assertEqual(fm.features, ['feature1','feature2'])

        self.assertEqual(fm.possible_values,{'+','-'})

        #fails, should be sorted list?
        self.assertEqual(sorted(fm.segments),sorted(['#','a','b','c','d']))

    def test_dots(self):
        fm = FeatureMatrix('test',self.dots_info)


        self.assertEqual(fm.features, ['feature1','feature2'])

        self.assertEqual(fm.possible_values,{'+','-','.'})

        self.assertEqual(fm['b','feature2'],'.')

        #Fails, should be sorted list of _features? Or set of _features? Would need to be hashed then
        self.assertEqual(fm['b']['feature2'],'.')

    def test_missing(self):
        fm = FeatureMatrix('test',self.missing_info)

        self.assertEqual(fm.features, ['feature1','feature2'])

        self.assertEqual(fm.possible_values,{'+','-'})

        #Error, there should be a default default value?
        fm.validate()

    def test_missing_with_default(self):
        fm = FeatureMatrix('test',self.missing_with_default_info)

        self.assertEqual(fm.features, ['feature1','feature2'])

        self.assertEqual(fm.possible_values,{'+','-','n'})

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

        #self.assertEqual(corpus['a'].transcription[0]._features,{'feature1':'+','feature2':'+'})


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

        corpus.add_tier('t','+feature1')
        self.assertEqual(corpus['d'].t, [corpus['d'].transcription[0]])

        corpus.remove_attribute('t')

        self.assertRaises(AttributeError,getattr,corpus['d'],'t')

    def test_feats_to_segs(self):
        corpus = Corpus('test')
        for w in self.corpus_basic_info:
            corpus.add_word(Word(**w))

        fm = FeatureMatrix('test',self.feature_basic_info)

        corpus.set_feature_matrix(fm)

        self.assertEqual(sorted(corpus.features_to_segments(['+feature1'])),sorted(['a','b']))

class TranscriptionTest(unittest.TestCase):
    def setUp(self):
        self.cab = ['c','a','b']
        self.ab = ['a','b']
        self.ad = ['a','d']

    def test_add(self):
        ab = Transcription(self.ab)
        ad = Transcription(self.ad)

        self.assertEqual(['a','b','a','d'], ab + ad)

    def test_tier(self):
        ab = Transcription(self.ab)
        self.assertEqual(['a'], ab.match_segments(['a']))

        cab = Transcription(self.cab)
        self.assertEqual(['c','b'], cab.match_segments(['c','b']))

    def test_get(self):
        cab = Transcription(self.cab)
        self.assertEqual(['c'], cab[:1])
        self.assertEqual('c', cab[0])
        self.assertRaises(IndexError,cab.__getitem__,4)


class EnvironmentTest(unittest.TestCase):
    def setUp(self):
        self.corpus_info = [{'spelling':'a','transcription':['a','b'],'frequency':32.0},
                            {'spelling':'b','transcription':['a','b'],'frequency':32.0},
                            {'spelling':'c','transcription':['c','a','b'],'frequency':32.0},
                            {'spelling':'d','transcription':['a','d'],'frequency':32.0},]

        self.feature_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+','feature2':'-'},
                            {'symbol':'c','feature1':'-','feature2':'+'},
                            {'symbol':'d','feature1':'-','feature2':'-'}]

class EnvironmentFilterTest(unittest.TestCase):
    def setUp(self):
        self.corpus_info = [{'spelling':'a','transcription':['a','b'],'frequency':32.0},
                            {'spelling':'b','transcription':['a','b'],'frequency':32.0},
                            {'spelling':'c','transcription':['c','a','b'],'frequency':32.0},
                            {'spelling':'d','transcription':['a','d'],'frequency':32.0},]

        self.feature_info = [{'symbol':'a','feature1':'+','feature2':'+'},
                            {'symbol':'b','feature1':'+','feature2':'-'},
                            {'symbol':'c','feature1':'-','feature2':'+'},
                            {'symbol':'d','feature1':'-','feature2':'-'}]

        self.corpus = Corpus('test')
        for w in self.corpus_info:
            self.corpus.add_word(Word(**w))

        fm = FeatureMatrix('test',self.feature_info)

        self.corpus.set_feature_matrix(fm)
        self.corpus.inventory.update_features(self.corpus.specifier)

    def test_init(self):
        segs = self.corpus.features_to_segments('+feature1')
        envfilt = EnvironmentFilter(['a'], lhs = [segs])
        self.assertEqual(sorted(envfilt.lhs[0]),sorted(['a','b']))
        self.assertEqual(envfilt.rhs, None)

        segs = self.corpus.features_to_segments('-feature1')
        envfilt = EnvironmentFilter('a',rhs = [segs])
        self.assertEqual(sorted(envfilt.rhs[0]),sorted(['c','d']))
        self.assertEqual(envfilt.lhs,None)

        segs = self.corpus.features_to_segments('-feature1,-feature2')
        envfilt = EnvironmentFilter('a',rhs = [segs])
        self.assertEqual(sorted(envfilt.rhs[0]),sorted(['d']))

    def test_contains(self):
        segs = self.corpus.features_to_segments('+feature1')
        envfilt = EnvironmentFilter('a',lhs = [segs])
        env1 = Environment('a', None, lhs = ['a'], rhs = ['b'])
        env2 = Environment('a', None, lhs = ['c'], rhs = ['#'])
        env3 = Environment('a', None, lhs = ['a'], rhs = ['c'])

        self.assertTrue(env1 in envfilt)
        self.assertFalse(env2 in envfilt)

        segs = self.corpus.features_to_segments('+feature1')
        envfilt = EnvironmentFilter('a',rhs = [segs], lhs=[segs])
        self.assertTrue(env1 in envfilt)
        self.assertFalse(env2 in envfilt)
        self.assertFalse(env3 in envfilt)


def test_categories_spe(specified_test_corpus):
    cats = {'ɑ':['Vowel','Open','Near back','Unrounded'],
            'u':['Vowel','Close','Back','Rounded'],
            'o':['Vowel','Close mid','Back','Rounded'],
            'e':['Vowel','Close mid','Front','Unrounded'],
            's':['Consonant','Dental','Fricative','Voiceless'],
            'm':['Consonant','Labial','Nasal','Voiced'],
            'i':['Vowel','Close','Front','Unrounded'],
            'n':['Consonant','Dental','Nasal','Voiced'],
            'ʃ':['Consonant','Alveopalatal','Fricative','Voiceless'],
            't':['Consonant','Dental','Stop','Voiceless']}
    inv = specified_test_corpus.inventory

    for k,v in cats.items():
        assert(inv.categorize(inv[k]) == v)

def test_no_features():
    seg = Segment('')


def test_no_syllabic_feature():
    seg = Segment('')
    seg.set_features({'feature1':'+','feature2':'+'})



class SegmentTest(unittest.TestCase):
    def setUp(self):
        self.basic_info = {'a':{'feature1':'+','feature2':'+'},
                            'b':{'feature1':'+','feature2':'-'},
                            'c':{'feature1':'-','feature2':'+'},
                            'd':{'feature1':'-','feature2':'-'}}

    def test_basic_segment_properties(self):
        seg = Segment('')
        assert(str(seg) == '')
        assert(len(seg) == 0)
        assert(seg != 's')

        seg1 = Segment('a')
        seg2 = Segment('b')

        assert(seg1 < seg2)
        assert(seg1 <= seg2)

        assert(seg2 > seg1)
        assert(seg2 >= seg1)

    def test_match_feature(self):
        for s,v in self.basic_info.items():
            seg = Segment(s)
            seg.set_features(v)
            for feature, value in v.items():
                for fv in ['+','-']:
                    if fv == value:
                        self.assertTrue(seg.feature_match([fv+feature]))
                        self.assertTrue(seg.feature_match(fv+feature))
                    else:
                        self.assertTrue(not seg.feature_match([fv+feature]))

def test_redundant_features(specified_test_corpus):
    feature = ['back']
    r = specified_test_corpus.inventory.get_redundant_features(feature, others = ['+voc', '-low'])

    assert('round' in r)

