
import sys
import os

from corpustools.phonosearch import phonological_search
from corpustools.corpus.classes import EnvironmentFilter, Environment

def test_non_minimal_pair_corpus_minpair(unspecified_test_corpus):
    envs = [EnvironmentFilter(['n'],['#'])]
    results = phonological_search(unspecified_test_corpus, envs)
    print(results)
    e = results[0][1][0]
    print(e.middle, e.position, e.lhs, e.rhs)
    expected_e = Environment('n', 1, ('#',))
    print(expected_e.middle, expected_e.position, expected_e.lhs, expected_e.rhs)
    assert(e == expected_e)

