
import sys
import os
import pytest

from corpustools.funcload.functional_load import (minpair_fl, deltah_fl,
                                relative_minpair_fl, relative_deltah_fl,
                                all_pairwise_fls,)
from corpustools.corpus.classes import Segment

from corpustools.contextmanagers import (CanonicalVariantContext,
                                        MostFrequentVariantContext,
                                        SeparatedTokensVariantContext,
                                        WeightedVariantContext)


#class NeutralizeTest(unittest.TestCase):
#    pass

def test_minpair(unspecified_test_corpus):

    calls = [({'segment_pairs':[('s','ʃ')],
                    'relative_count':True},0.125),
            ({'segment_pairs':[('s','ʃ')],
                    'relative_count':False},1),
            ({'segment_pairs':[('m','n')],
                    'relative_count':True},0.11111),
            ({'segment_pairs':[('m','n')],
                    'relative_count':False},1),
            ({'segment_pairs':[('e','o')],
                    'relative_count':True},0),
            ({'segment_pairs':[('e','o')],
                    'relative_count':False},0),
            ({'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'relative_count':True},0.14286),
            ({'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'relative_count':False},2),]

    with CanonicalVariantContext(unspecified_test_corpus,
                                'transcription', 'type') as c:
        for kwargs, v in calls:
            print(kwargs)
            assert(abs(minpair_fl(c, **kwargs)[0]-v) < 0.0001)

    calls = [({'segment_pairs':[('s','ʃ')],
                    'relative_count':True},0.14286),
            ({'segment_pairs':[('s','ʃ')],
                    'relative_count':False},1),
            ({'segment_pairs':[('m','n')],
                    'relative_count':True},0),
            ({'segment_pairs':[('m','n')],
                    'relative_count':False},0),
            ({'segment_pairs':[('e','o')],
                    'relative_count':True},0),
            ({'segment_pairs':[('e','o')],
                    'relative_count':False},0),

            ({'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'relative_count':True},0.09091),
            ({'segment_pairs':[('s','ʃ'),
                                    ('m','n'),
                                    ('e','o')],
                    'relative_count':False},1)]

    with CanonicalVariantContext(unspecified_test_corpus,
                                'transcription', 'type', frequency_threshold = 3) as c:
        for kwargs, v in calls:
            print(kwargs)
            assert(abs(minpair_fl(c, **kwargs)[0]-v) < 0.0001)

def test_deltah(unspecified_test_corpus):
    type_calls = [({'segment_pairs':[('s','ʃ')]},0.02547695),
            ({'segment_pairs':[('m','n')]},0.02547695),
            ({'segment_pairs':[('e','o')]},0),
            ({'segment_pairs':[('s','ʃ'),
                                ('m','n'),
                                ('e','o')]},0.05284),]

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        for kwargs, v in type_calls:
            assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

    type_calls = [({'segment_pairs':[('s','ʃ')], 'prevent_normalization':True},0.09953567),
            ({'segment_pairs':[('m','n')], 'prevent_normalization':True},0.09953567),
            ({'segment_pairs':[('e','o')], 'prevent_normalization':True},0),
            ({'segment_pairs':[('s','ʃ'),
                                ('m','n'),
                                ('e','o')], 'prevent_normalization':True},0.206450877),]

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        for kwargs, v in type_calls:
            assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)


    type_calls = [({'segment_pairs':[('s','ʃ')]},0.035015954),
            ({'segment_pairs':[('m','n')]},0),
            ({'segment_pairs':[('e','o')]},0),
            ({'segment_pairs':[('s','ʃ'),
                                ('m','n'),
                                ('e','o')]},0.035015954)]

    with CanonicalVariantContext(unspecified_test_corpus,
                            'transcription', 'type', frequency_threshold = 3) as c:
        for kwargs, v in type_calls:
            assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

    token_calls = [({'segment_pairs':[('s','ʃ')]},0.08305),
            ({'segment_pairs':[('m','n')]},0.002314),
            ({'segment_pairs':[('e','o')]},0.0),
            ({'segment_pairs':[('s','ʃ'),
                                ('m','n'),
                                ('e','o')]},0.0853641),]

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        for kwargs, v in token_calls:
            assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)



# def test_minimal_pair_wordtokens(unspecified_discourse_corpus):
#     corpus = unspecified_discourse_corpus.lexicon

#     calls = [({'segment_pairs':[('s','ʃ')],
#                     'relative_count':True},0.125),
#             ({'segment_pairs':[('s','ʃ')],
#                     'relative_count':False},1),
#             ({'segment_pairs':[('m','n')],
#                     'relative_count':True},0.11111),
#             ({'segment_pairs':[('m','n')],
#                     'relative_count':False},1),
#             ({'segment_pairs':[('e','o')],
#                     'relative_count':True},0),
#             ({'segment_pairs':[('e','o')],
#                     'relative_count':False},0),
#             ({'segment_pairs':[('s','ʃ'),
#                                     ('m','n'),
#                                     ('e','o')],
#                     'relative_count':True},0.14286),
#             ({'segment_pairs':[('s','ʃ'),
#                                     ('m','n'),
#                                     ('e','o')],
#                     'relative_count':False},2),]
#     with MostFrequentVariantContext(corpus, 'transcription', 'type') as c:
#         for kwargs, v in calls:
#             assert(abs(minpair_fl(c, **kwargs)[0]-v) < 0.0001)

#     calls = [({ 'segment_pairs':[('s','ʃ')],
#                     'relative_count':True},0.14286),
#             ({'segment_pairs':[('s','ʃ')],
#                     'relative_count':False},1),
#             ({'segment_pairs':[('m','n')],
#                     'relative_count':True},0),
#             ({'segment_pairs':[('m','n')],
#                     'relative_count':False},0),
#             ({'segment_pairs':[('e','o')],
#                     'relative_count':True},0),
#             ({'segment_pairs':[('e','o')],
#                     'relative_count':False},0),
#             ({'segment_pairs':[('s','ʃ'),
#                                     ('m','n'),
#                                     ('e','o')],
#                     'relative_count':True},0.09091),
#             ({'segment_pairs':[('s','ʃ'),
#                                     ('m','n'),
#                                     ('e','o')],
#                     'relative_count':False},1)]
#     with MostFrequentVariantContext(corpus,
#             'transcription', 'type',frequency_threshold = 3) as c:
#         for kwargs, v in calls:
#             assert(abs(minpair_fl(c, **kwargs)[0]-v) < 0.0001)

# def test_deltah_wordtokens(unspecified_discourse_corpus):
#     corpus = unspecified_discourse_corpus.lexicon
#     frequent_type_calls = [({'segment_pairs':[('s','ʃ')]},0.13333),
#             ({'segment_pairs':[('e','o')]},0),
#             ({'segment_pairs':[('s','ʃ'),
#                                 ('m','n'),
#                                 ('e','o')]},0.26667),]
#     with MostFrequentVariantContext(corpus, 'transcription', 'type') as c:
#         for kwargs, v in frequent_type_calls:
#             assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

#     frequent_type_calls = [({'segment_pairs':[('m','n')]},0),]
#     with MostFrequentVariantContext(corpus,
#                     'transcription', 'type', frequency_threshold = 3) as c:
#         for kwargs, v in frequent_type_calls:
#             assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

#     frequent_token_calls = [({'segment_pairs':[('s','ʃ')]},0.24794),
#             ({'segment_pairs':[('e','o')]},0),
#             ({'segment_pairs':[('s','ʃ'),
#                                 ('m','n'),
#                                 ('e','o')]},0.25485),]
#     with MostFrequentVariantContext(corpus, 'transcription', 'token') as c:
#         for kwargs, v in frequent_token_calls:
#             assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

#     frequent_token_calls = [({'segment_pairs':[('m','n')]},0),]
#     with MostFrequentVariantContext(corpus,
#                     'transcription', 'token', frequency_threshold = 3) as c:
#         for kwargs, v in frequent_token_calls:
#             assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

#     count_token_calls = [({'segment_pairs':[('s','ʃ'),
#                                 ('m','n'),
#                                 ('e','o')]},0.25483),
#             ({'segment_pairs':[('m','n')]},0.00691),]
#     with SeparatedTokensVariantContext(corpus, 'transcription', 'token') as c:
#         for kwargs, v in count_token_calls:
#             assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

#     count_token_calls = [({'segment_pairs':[('s','ʃ')]},0.25053),
#             ({'segment_pairs':[('e','o')]},0),]
#     with SeparatedTokensVariantContext(corpus,
#                     'transcription', 'token', frequency_threshold = 3) as c:
#         for kwargs, v in count_token_calls:
#             assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

#     relative_type_calls = [({'segment_pairs':[('m','n')]},0.13333),]
#     with WeightedVariantContext(corpus, 'transcription', 'type') as c:
#         for kwargs, v in relative_type_calls:
#             assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

#     relative_type_calls = [({'segment_pairs':[('s','ʃ'),
#                                         ('m','n'),
#                                         ('e','o')]},0.16667),
#                     ({'segment_pairs':[('s','ʃ')]},0.16667),
#                     ({'segment_pairs':[('e','o')]},0),]
#     with WeightedVariantContext(corpus,
#                     'transcription', 'type', frequency_threshold = 3) as c:
#         for kwargs, v in relative_type_calls:
#             assert(abs(deltah_fl(c, **kwargs)-v) < 0.0001)

def test_relative_minpair(unspecified_test_corpus):
    calls = [({'segment':'s',
                    'relative_count':True},0.013888),
            ({'segment':'s',
                    'relative_count':False},0.11111),
            ({'segment':'n',
                    'relative_count':True},0.0123457),
            ({'segment':'n',
                    'relative_count':False},0.11111),
            ({'segment':'o',
                    'relative_count':True},0),
            ({'segment':'o',
                    'relative_count':False},0),]

    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        for kwargs, v in calls:
            assert(abs(relative_minpair_fl(c, **kwargs)[0]-v) < 0.0001)

    calls = [({'segment':'s',
                    'relative_count':True},0.01587),
            ({'segment':'s',
                    'relative_count':False},0.11111),
            ({'segment':'n',
                    'relative_count':True},0),
            ({'segment':'n',
                    'relative_count':False},0),
            ({'segment':'o',
                    'relative_count':True},0),
            ({'segment':'o',
                    'relative_count':False},0)]


    with CanonicalVariantContext(unspecified_test_corpus,
                    'transcription', 'type', frequency_threshold = 3) as c:
        for kwargs, v in calls:
            assert(abs(relative_minpair_fl(c, **kwargs)[0]-v) < 0.0001)


def test_relative_deltah(unspecified_test_corpus):
    type_calls = [({'segment':'s'},0.00283),
            ({'segment':'n'},0.00283),
            ({'segment':'o'},0),]
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'type') as c:
        for kwargs, v in type_calls:
            assert(abs(relative_deltah_fl(c, **kwargs)[0]-v) < 0.0001)

    type_calls = [({'segment':'s'}, 0.00389),
            ({'segment':'n'},0),
            ({'segment':'o'},0),]
    with CanonicalVariantContext(unspecified_test_corpus,
                        'transcription', 'type', frequency_threshold = 3) as c:
        for kwargs, v in type_calls:
            assert(abs(relative_deltah_fl(c, **kwargs)[0]-v) < 0.0001)


    token_calls = [({'segment':'s'},0.009227777),
            ({'segment':'n'},0.0002571111),
            ({'segment':'o'},0),]
    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        for kwargs, v in token_calls:
            assert(abs(relative_deltah_fl(c, **kwargs)[0]-v) < 0.0001)


@pytest.mark.xfail
def test_mass_fl(unspecified_test_corpus):
    #This needs to be updated so that it deterministically passes
    calls = [({'algorithm':'minpair',
                    'relative_count':True},

                        ([(('s', 'ʃ'), 0.125), (('m', 'n'), 0.1111111111111111), (('i', 't'), 0.0), (('t', 'u'), 0.0),
                         (('m', 't'), 0.0), (('i', 'u'), 0.0), (('e', 'o'), 0.0), (('n', 'o'), 0.0), (('i', 'ʃ'), 0.0),
                         (('u', 'ɑ'), 0.0), (('m', 'ʃ'), 0.0), (('m', 'ɑ'), 0.0), (('t', 'ʃ'), 0.0), (('e', 'n'), 0.0),
                         (('o', 't'), 0.0), (('e', 'ɑ'), 0.0), (('n', 'u'), 0.0), (('n', 't'), 0.0), (('o', 'ʃ'), 0.0),
                         (('e', 'u'), 0.0), (('s', 't'), 0.0), (('ɑ', 'ʃ'), 0.0), (('n', 's'), 0.0), (('e', 's'), 0.0),
                         (('i', 's'), 0.0), (('m', 'u'), 0.0), (('e', 'i'), 0.0), (('i', 'n'), 0.0), (('i', 'o'), 0.0),
                         (('i', 'm'), 0.0), (('n', 'ɑ'), 0.0), (('t', 'ɑ'), 0.0), (('s', 'ɑ'), 0.0), (('s', 'u'), 0.0),
                         (('i', 'ɑ'), 0.0), (('o', 's'), 0.0), (('e', 'ʃ'), 0.0), (('u', 'ʃ'), 0.0), (('m', 'o'), 0.0),
                         (('e', 'm'), 0.0), (('o', 'u'), 0.0), (('n', 'ʃ'), 0.0), (('e', 't'), 0.0), (('o', 'ɑ'), 0.0),
                         (('m', 's'), 0.0)])),
            ({'algorithm':'minpair',
                    'relative_count':False},

                        ([(('s', 'ʃ'), 1.0), (('m', 'n'), 1.0), (('i', 't'), 0.0), (('t', 'u'), 0.0),
                         (('m', 't'), 0.0), (('i', 'u'), 0.0), (('e', 'o'), 0.0), (('n', 'o'), 0.0), (('i', 'ʃ'), 0.0),
                         (('u', 'ɑ'), 0.0), (('m', 'ʃ'), 0.0), (('m', 'ɑ'), 0.0), (('t', 'ʃ'), 0.0), (('e', 'n'), 0.0),
                         (('o', 't'), 0.0), (('e', 'ɑ'), 0.0), (('n', 'u'), 0.0), (('n', 't'), 0.0), (('o', 'ʃ'), 0.0),
                         (('e', 'u'), 0.0), (('s', 't'), 0.0), (('ɑ', 'ʃ'), 0.0), (('n', 's'), 0.0), (('e', 's'), 0.0),
                         (('i', 's'), 0.0), (('m', 'u'), 0.0), (('e', 'i'), 0.0), (('i', 'n'), 0.0), (('i', 'o'), 0.0),
                         (('i', 'm'), 0.0), (('n', 'ɑ'), 0.0), (('t', 'ɑ'), 0.0), (('s', 'ɑ'), 0.0), (('s', 'u'), 0.0),
                         (('i', 'ɑ'), 0.0), (('o', 's'), 0.0), (('e', 'ʃ'), 0.0), (('u', 'ʃ'), 0.0), (('m', 'o'), 0.0),
                         (('e', 'm'), 0.0), (('o', 'u'), 0.0), (('n', 'ʃ'), 0.0), (('e', 't'), 0.0), (('o', 'ɑ'), 0.0),
                         (('m', 's'), 0.0)]))]


    with CanonicalVariantContext(unspecified_test_corpus, 'transcription', 'token') as c:
        for kwargs, v in calls:
            for result,prediction in zip(all_pairwise_fls(c, **kwargs), v):
                assert(abs(result[1]-prediction[1]) < 0.0001)

