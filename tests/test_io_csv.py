
import pytest
import os

from corpustools.corpus.io.csv import (load_corpus_csv, export_corpus_csv, inspect_csv,
                                        load_feature_matrix_csv, export_feature_matrix_csv)

from corpustools.exceptions import DelimiterError

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix)

def test_inspect_example(csv_test_dir):
    example_path = os.path.join(csv_test_dir, 'example.txt')
    atts, coldelim = inspect_csv(example_path)
    assert(coldelim == ',')
    for a in atts:
        if a.name == 'frequency':
            assert(a.attribute.att_type == 'numeric')
        elif a.name == 'transcription':
            assert(a.attribute.att_type == 'tier')
            assert(a.delimiter == '.')
        elif a.name == 'spelling':
            assert(a.attribute.att_type == 'spelling')


def test_corpus_csv(csv_test_dir, unspecified_test_corpus):
    example_path = os.path.join(csv_test_dir, 'example.txt')
    with pytest.raises(DelimiterError):
        load_corpus_csv('example',example_path,delimiter='\t')
    #with pytest.raises(DelimiterError):
    #    load_corpus_csv('example',example_path,delimiter=',')


    c = load_corpus_csv('example',example_path,delimiter=',')

    assert(isinstance(c, Corpus))
    assert(c == unspecified_test_corpus)


#def test_load_with_fm(self):
    #c = load_transcription_corpus('test',self.transcription_path,' ',
                #['-','=','.'],trans_delimiter='.',
                #feature_system_path = self.full_feature_matrix_path)

    #self.assertEqual(c.lexicon.specifier,load_binary(self.full_feature_matrix_path))

    #self.assertEqual(c.lexicon['cab'].frequency, 1)

    #self.assertEqual(c.lexicon.check_coverage(),[])

    #c = load_transcription_corpus('test',self.transcription_path,' ',
                #['-','=','.'],trans_delimiter='.',
                #feature_system_path = self.missing_feature_matrix_path)

    #self.assertEqual(c.lexicon.specifier,load_binary(self.missing_feature_matrix_path))

    #self.assertEqual(sorted(c.lexicon.check_coverage()),sorted(['b','c','d']))


def test_basic_feature_matrix(features_test_dir):
    basic_path = os.path.join(features_test_dir, 'test_feature_matrix.txt')

    with pytest.raises(DelimiterError):
        load_feature_matrix_csv('test',basic_path,' ')

    fm = load_feature_matrix_csv('test',basic_path,',')

    assert(fm.name == 'test')
    assert(fm['a','feature1'] == '+')

def test_missing_value(features_test_dir):
    missing_value_path = os.path.join(features_test_dir, 'test_feature_matrix_missing_value.txt')
    fm = load_feature_matrix_csv('test',missing_value_path,',')

    assert(fm['d','feature2'] == 'n')

def test_extra_feature(features_test_dir):
    extra_feature_path = os.path.join(features_test_dir, 'test_feature_matrix_extra_feature.txt')
    fm = load_feature_matrix_csv('test',extra_feature_path,',')

    with pytest.raises(KeyError):
        fm.__getitem__(('a','feature3'))


def test_stressed(csv_test_dir):
    stressed_path = os.path.join(csv_test_dir, 'stressed.txt')
    ats,_ = inspect_csv(stressed_path, coldelim = ',')
    print(ats)
    ats[1].number_behavior = 'stress'
    c = load_corpus_csv('stressed',stressed_path,',', ats)
    assert(c.inventory['uw'].symbol == 'uw')
    assert(c.inventory.stresses == {'1': set(['uw','iy']),
                                    '0': set(['uw','iy','ah'])})
