
import sys
import os

from corpustools.mutualinfo.mutual_information import pointwise_mi, all_mis

def test_pointwise_mi(unspecified_test_corpus):
    calls = [
            ({'corpus': unspecified_test_corpus, 'sequence_type': 'transcription',
                    'query':('e', 'm')}, 2.7319821866519507),
            ({'corpus': unspecified_test_corpus, 'sequence_type': 'transcription',
                    'query':('t', 'n'),
                    'in_word':True}, 0.5849625007211564),
            ({'corpus': unspecified_test_corpus, 'sequence_type': 'transcription',
                    'query':('e', 'm'),
                    'halve_edges':True}, 2.7319821866519507)


            ## pointwise_mi can't pass sequence_type to corpus.get_frequency_base
            #         ,
            # ({'corpus': unspecified_test_corpus, 'sequence_type': 'spelling',
            #         'query':('t', 'a')}, 0)
            ]

    for c,v in calls:
        result = pointwise_mi(**c)
        assert(abs(result-v) < 0.0001)