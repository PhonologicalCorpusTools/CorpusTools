import pytest
import sys
import os

from corpustools.kl.kl import KullbackLeibler as KL
from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        WeightedVariantContext)


def test_identical(specified_test_corpus):
    #Test 1, things that are identical
    with CanonicalVariantContext(specified_test_corpus, 'transcription', 'type') as c:
        seg1_entropy, seg2_entropy, distance, ur, is_spurious = KL(c, 's', 's','b')
    assert(distance == 0.0)
    assert(seg1_entropy == seg2_entropy)

def test_allophones(specified_test_corpus):
    #Test 2, things are supposed to be allophones
    with CanonicalVariantContext(specified_test_corpus, 'transcription', 'type') as c:
        seg1_entropy, seg2_entropy, distance, ur, is_spurious = KL(c, 's', 'ʃ','b')
    assert(abs(distance - 0.15113518339295337) < 0.001)
    assert(abs(seg1_entropy - 0.035000140096702444) < 0.001)
    assert(abs(seg2_entropy - 0.06074393445793598) < 0.001)

@pytest.mark.xfail
def test_pseudo_allophones(specified_test_corpus):
    #Test 3, things that are allophones by coincidence
    with CanonicalVariantContext(specified_test_corpus, 'transcription', 'type') as c:
        seg1_entropy, seg2_entropy, distance, ur, is_spurious = KL(c, 's', 'ɑ','b')
    assert(abs(distance - 0.23231302100802534) < 0.001)
    assert(abs(seg1_entropy - 0.03500014009670246) < 0.001)
    assert(abs(seg2_entropy - 0.07314589775440267) < 0.001)
    #assertEqual(ur,sr)#both should be None, to be fixed with _features

def test_default(specified_test_corpus):
    #Test 4, things that have no assumed relationship
    with CanonicalVariantContext(specified_test_corpus, 'transcription', 'type') as c:
        seg1_entropy, seg2_entropy, distance, ur, is_spurious = KL(c, 's', 'm','b')
    assert(abs(distance - 0.14186314747884132) < 0.001)
    assert(abs(seg1_entropy - 0.035000140096702444) < 0.001)
    assert(abs(seg2_entropy - 0.06074393445793598) < 0.001)

def test_error(specified_test_corpus):
    #Test 5, things not in the corpus
    with pytest.raises(ValueError):
        with CanonicalVariantContext(specified_test_corpus, 'transcription', 'type') as c:
            KL(c, 's', '!','')


