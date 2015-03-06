
import sys
import os

from corpustools.neighdens.neighborhood_density import neighborhood_density


def test_basic_corpus(unspecified_test_corpus):
    calls = [({'corpus': unspecified_test_corpus,
                    'query':unspecified_test_corpus.find('mata'),
                    'max_distance':1},1.0),
            ({'corpus': unspecified_test_corpus,
                    'query':unspecified_test_corpus.find('nata'),
                    'max_distance':2},3.0)]

    for c,v in calls:
        result = neighborhood_density(**c)
        assert(abs(result[0]-v) < 0.0001)

