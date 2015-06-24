

import sys
import os

from corpustools.symbolsim.string_similarity import string_similarity
from corpustools.contextmanagers import CanonicalVariantContext, MostFrequentVariantContext, WeightedVariantContext

def test_spelling(unspecified_test_corpus):
    expected = [(unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('atema'),0),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('enuta'),4),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mashomisi'),7),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mata'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('nata'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('sasi'),5),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shashi'),6),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shisata'),6),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shushoma'),6),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ta'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tatomi'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tishenishu'),9),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('toni'),4),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tusa'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ʃi'),5)]
    expected.sort(key=lambda t:t[1])
    with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'type') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('atema'),'edit_distance')
    calced.sort(key=lambda t:t[1])
    for i, v in enumerate(expected):
        assert(calced[i] == v)

    expected = [(unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('atema'),5),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('enuta'),5),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mashomisi'),6),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mata'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('nata'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('sasi'),0),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shashi'),2),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shisata'),5),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shushoma'),6),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ta'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tatomi'),4),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tishenishu'),8),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('toni'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tusa'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ʃi'),3)]
    expected.sort(key=lambda t:t[1])
    with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'type') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('sasi'),'edit_distance')
    calced.sort(key=lambda t:t[1])
    for i, v in enumerate(expected):
        assert(calced[i] == v)

def test_transcription(unspecified_test_corpus):
    expected = [(unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('atema'),0),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('enuta'),4),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mashomisi'),6),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('mata'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('nata'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('sasi'),5),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shashi'),5),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shisata'),5),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('shushoma'),4),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ta'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tatomi'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tishenishu'),7),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('toni'),4),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('tusa'),3),
                (unspecified_test_corpus.find('atema'),unspecified_test_corpus.find('ʃi'),5)]
    expected.sort(key=lambda t:t[1])
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('atema'),'edit_distance')
    calced.sort(key=lambda t:t[1])
    for i, v in enumerate(expected):
        assert(calced[i] == v)

    expected = [(unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('atema'),5),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('enuta'),5),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mashomisi'),5),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('mata'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('nata'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('sasi'),0),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shashi'),2),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shisata'),4),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('shushoma'),6),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ta'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tatomi'),4),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tishenishu'),7),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('toni'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('tusa'),3),
                (unspecified_test_corpus.find('sasi'),unspecified_test_corpus.find('ʃi'),3)]
    expected.sort(key=lambda t:t[1])
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        calced = string_similarity(c,unspecified_test_corpus.find('sasi'),'edit_distance')
    calced.sort(key=lambda t:t[1])
    for i, v in enumerate(expected):
        assert(calced[i] == v)
