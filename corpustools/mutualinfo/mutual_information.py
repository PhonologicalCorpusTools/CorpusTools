# -*- coding: utf-8 -*-

import sys
import math
from collections import defaultdict

def pointwise_mi(corpus, query, sequence_type, stop_check = None, call_back = None):
    """query should be a tuple of two strings, each a segment/letter"""

    if call_back is not None:
        call_back("Generating probabilities...")
        call_back(0,0)
        cur = 0
    count_what = 'type'
    unigram_dict = corpus.get_frequency_base(sequence_type, count_what, gramsize = 1, probability=True)
    bigram_dict = corpus.get_frequency_base(sequence_type, count_what, gramsize = 2, probability=True)

    prob_s1 = unigram_dict[query[0]]
    prob_s2 = unigram_dict[query[1]]
    prob_bg = bigram_dict[query]

    if unigram_dict[query[0]] == 0.0:
        raise Exception('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[0]))
    if unigram_dict[query[1]] == 0.0:
        raise Exception('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[1]))
    if bigram_dict[query] == 0.0:
        raise Exception('Warning! Mutual information could not be calculated because the bigram {} is not in the corpus.'.format(str(query)))


    return math.log((prob_bg/(prob_s1*prob_s2)), 2)
