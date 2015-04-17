
import pytest
import os

from corpustools.corpus.io.text_spelling import load_discourse_spelling, export_discourse_spelling
from corpustools.corpus.io.text_transcription import load_discourse_transcription, export_discourse_transcription

from corpustools.exceptions import DelimiterError

from corpustools.corpus.classes import (Word, Corpus, FeatureMatrix, Discourse)

from corpustools.utils import generate_discourse

def test_export_spelling(export_test_dir, unspecified_test_corpus):
    d = generate_discourse(unspecified_test_corpus)
    export_path = os.path.join(export_test_dir, 'test_export_spelling.txt')
    export_discourse_spelling(d, export_path, single_line = False)

    d2 = load_discourse_spelling('test', export_path, ' ', [])
    for k in unspecified_test_corpus.keys():
        assert(d2.lexicon[k].spelling == unspecified_test_corpus[k].spelling)
        assert(d2.lexicon[k].frequency == unspecified_test_corpus[k].frequency)

def test_export_transcription(export_test_dir, unspecified_test_corpus):
    d = generate_discourse(unspecified_test_corpus)
    export_path = os.path.join(export_test_dir, 'test_export_transcription.txt')
    export_discourse_transcription(d, export_path, single_line = False)

    d2 = load_discourse_transcription('test', export_path, ' ', [], trans_delimiter='.')
    words = sorted([x for x in unspecified_test_corpus], key = lambda x: x.transcription)
    words2 = sorted([x for x in d2.lexicon], key = lambda x: x.transcription)
    for i,w in enumerate(words):
        w2 = words2[i]
        assert(w.transcription == w2.transcription)
        assert(w.frequency == w2.frequency)

def test_load_spelling_no_ignore(text_test_dir):
    spelling_path = os.path.join(text_test_dir, 'test_text_spelling.txt')
    with pytest.raises(DelimiterError):
        load_discourse_spelling('test', spelling_path,"?",[])

    c = load_discourse_spelling('test',spelling_path,' ',[])

    assert(c.lexicon['ab'].frequency == 2)


def test_load_spelling_ignore(text_test_dir):
    spelling_path = os.path.join(text_test_dir, 'test_text_spelling.txt')
    c = load_discourse_spelling('test',spelling_path,' ',["'",'.'])

    assert(c.lexicon['ab'].frequency == 3)
    assert(c.lexicon['cabd'].frequency == 1)

def text_test_dir(text_test_dir):
    transcription_path = os.path.join(text_test_dir, 'test_text_transcription.txt')
    with pytest.raises(DelimiterError):
        load_discourse_transcription('test',
                            transcription_path," ",[],
                            trans_delimiter = ',')

    c = load_discourse_transcription('test',transcription_path,' ',[],trans_delimiter='.')

    assert(sorted(c.lexicon.inventory) == sorted(['#','a','b','c','d']))

def test_load_transcription_morpheme(text_test_dir):
    transcription_morphemes_path = os.path.join(text_test_dir, 'test_text_transcription_morpheme_boundaries.txt')
    c = load_discourse_transcription('test',transcription_morphemes_path,' ',['-','=','.'],trans_delimiter='.')

    assert(c.lexicon['cab'].frequency == 2)

