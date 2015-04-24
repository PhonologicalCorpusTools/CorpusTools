
import sys
import os

from corpustools.corpus.classes import Word

from corpustools.neighdens.neighborhood_density import neighborhood_density, find_mutation_minpairs#, neighborhood_density_graph


def test_basic_corpus_nd(specified_test_corpus):
    calls = [({'corpus': specified_test_corpus,
                    'query':specified_test_corpus.find('mata'),
                    'max_distance':1},1.0),
            ({'corpus': specified_test_corpus,
                    'query':specified_test_corpus.find('nata'),
                    'max_distance':2},3.0),
            ({'corpus': specified_test_corpus,
                    'query':specified_test_corpus.find('mata'),
                    'sequence_type':'spelling',
                    'max_distance':1},1.0),
            ({'corpus': specified_test_corpus,
                    'query':specified_test_corpus.find('mata'),
                    'algorithm':'phono_edit_distance',
                    'max_distance':3},1.0)]

    for c,v in calls:
        result = neighborhood_density(**c)
        assert(abs(result[0]-v) < 0.0001)


def test_basic_corpus_mutation_minpairs(specified_test_corpus):
    calls = [({'corpus': specified_test_corpus,
                    'query':Word(**{'transcription': ['s', 'ɑ', 't', 'ɑ']}),
                    },2)]

    for c,v in calls:
        result = find_mutation_minpairs(**c)
        assert(result[0] == v)
        assert(result[1] == ['n.ɑ.t.ɑ', 'm.ɑ.t.ɑ'] or result[1] == ['m.ɑ.t.ɑ', 'n.ɑ.t.ɑ'])


# def test_neighborhood_density_graph(specified_test_corpus):
#     calls = [({'corpus': specified_test_corpus,
#                     'query':specified_test_corpus.find('mata'),
#                     'max_distance':1},1.0)]

#     for c,v in calls:
#         result = neighborhood_density_graph(**c)
#         assert(result[0] == v)
#         assert(result[1] == ['n.ɑ.t.ɑ'])
