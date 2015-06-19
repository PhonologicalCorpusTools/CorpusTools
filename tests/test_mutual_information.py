
import sys
import os

from corpustools.mutualinfo.mutual_information import pointwise_mi, all_mis
from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        WeightedVariantContext)

def test_pointwise_mi(unspecified_test_corpus):
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        calls = [
                ({'corpus_context': c,
                        'query':('e', 'm')}, 2.7319821866519507),
                ({'corpus_context': c,
                        'query':('t', 'n'),
                        'in_word':True}, 0.5849625007211564),
                ({'corpus_context': c,
                        'query':('e', 'm'),
                        'halve_edges':True}, 2.7319821866519507)

            ]

        for c,v in calls:
            result = pointwise_mi(**c)
            assert(abs(result-v) < 0.0001)

    #with CanonicalVariantContext(unspecified_test_corpus, 'spelling', 'type') as c:
    #   result = pointwise_mi(c, query = ('t', 'a'))
    #   assert(result == 0)
