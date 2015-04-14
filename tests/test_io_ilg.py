import unittest
import pytest
import os
import sys

from corpustools.corpus.io.text_ilg import load_corpus_ilg, ilg_to_data, export_corpus_ilg

from corpustools.corpus.io.helper import AnnotationType

from corpustools.exceptions import DelimiterError, ILGWordMismatchError

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix, Discourse, Attribute)

from corpustools.utils import generate_discourse

@pytest.mark.xfail
def test_export_ilg(export_test_dir, unspecified_test_corpus):
    d = generate_discourse(unspecified_test_corpus)
    export_path = os.path.join(export_test_dir, 'test_export_ilg.txt')
    export_corpus_ilg(d, export_path)

    d2 = load_corpus_ilg('test', export_path, None, [], trans_delimiter='.')

    for k in unspecified_test_corpus.keys():
        assert(d2.lexicon[k].spelling == unspecified_test_corpus[k].spelling)
        assert(d2.lexicon[k].transcription == unspecified_test_corpus[k].transcription)
        assert(d2.lexicon[k].frequency == unspecified_test_corpus[k].frequency)
    assert(d2.lexicon == unspecified_test_corpus)

def test_ilg_data(ilg_test_dir):
    basic_path = os.path.join(ilg_test_dir, 'test_basic.txt')
    data = ilg_to_data(basic_path, [AnnotationType('spelling', 'transcription', None, token = False, anchor = True),
                                    AnnotationType('transcription', None, None, token = False, base = True, delimited = True)],
                    delimiter=None,ignore_list=[], trans_delimiter = '.')
    assert(data['spelling']._list == [{'label':'a','token':{},'transcription':(0,2)},
                                    {'label':'a','token':{},'transcription':(2,4)},
                                    {'label':'b','token':{},'transcription':(4,6)}])
    assert(data['transcription']._list == [{'label':'a'},
                                        {'label':'b'},
                                        {'label':'a'},
                                        {'label':'b'},
                                        {'label':'c'},
                                        {'label':'d'}])

def test_ilg_basic(ilg_test_dir):
    basic_path = os.path.join(ilg_test_dir, 'test_basic.txt')
    corpus = load_corpus_ilg('test', basic_path,
            [AnnotationType('spelling', 'transcription', None, token = False,
                            anchor = True),
            AnnotationType('transcription', None, None, attribute = Attribute('transcription','tier'), token = False,
                            base = True, delimited = True)],
            delimiter=None,ignore_list=[], trans_delimiter = '.')
    print(corpus.words)
    print(corpus.lexicon.words)
    assert(corpus.lexicon.find('a').frequency == 2)

def test_ilg_mismatched(ilg_test_dir):
    mismatched_path = os.path.join(ilg_test_dir, 'test_mismatched.txt')
    with pytest.raises(ILGWordMismatchError):
        t = load_corpus_ilg('test', mismatched_path,
            [AnnotationType('spelling', 'transcription', None, token = False,
                            anchor = True),
            AnnotationType('transcription', None, None, attribute = Attribute('transcription','tier'), token = False,
                            base = True, delimited = True)], delimiter=None,ignore_list=[], trans_delimiter = '.')
