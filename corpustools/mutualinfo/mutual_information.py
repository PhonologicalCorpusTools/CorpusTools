# -*- coding: utf-8 -*-

import sys
import math
from collections import defaultdict

def pointwise_mi(corpus, query, sequence_type):
    """query should be a tuple of two strings, each a segment/letter"""
    unigram_dict = defaultdict(float)
    unigram_total = 0.0
    bigram_dict = defaultdict(float)
    bigram_total = 0.0
    for word in corpus:
        for symbol in getattr(word, sequence_type):
            unigram_dict[symbol] += 1.0
            unigram_total += 1.0
        for bigram in get_bigrams(getattr(word, sequence_type)): # get_bigrams should return tuples, like query
            bigram_dict[bigram] += 1.0
            bigram_total += 1.0

    prob_s1 = unigram_dict[query[0]] / unigram_total
    prob_s2 = unigram_dict[query[1]] / unigram_total
    prob_bg = bigram_dict[query] / bigram_total

    if unigram_dict[query[0]] == 0.0:
        raise Exception('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[0]))
    if unigram_dict[query[1]] == 0.0:
        raise Exception('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[1]))
    if bigram_dict[query] == 0.0:
        raise Exception('Warning! Mutual information could not be calculated because the bigram {} is not in the corpus.'.format(str(query)))


    return math.log((prob_bg/(prob_s1*prob_s2)), 2)
        
    
def get_bigrams(input_list):
    return zip(*[input_list[i:] for i in range(2)])

