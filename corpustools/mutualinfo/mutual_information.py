# -*- coding: utf-8 -*-

import sys
import math
from collections import defaultdict
import time

from corpustools.exceptions import MutualInfoError

def pointwise_mi(corpus, query, sequence_type,
                halve_edges = False, in_word = False,
                stop_check = None, call_back = None):
    """query should be a tuple of two strings, each a segment/letter"""
    if call_back is not None:
        call_back("Generating probabilities...")
        call_back(0,0)
        cur = 0
    count_what = 'type'
    if in_word:
        unigram_dict = get_in_word_unigram_frequencies(corpus, query, sequence_type, count_what)
        bigram_dict = get_in_word_bigram_frequency(corpus, query, sequence_type, count_what)
    else:
        unigram_dict = corpus.get_frequency_base(sequence_type, count_what, halve_edges, gramsize = 1, probability=True)
        bigram_dict = corpus.get_frequency_base(sequence_type, count_what, halve_edges, gramsize = 2, probability=True)

    #if '#' in query:
    #    raise(Exception("Word boundaries are currently unsupported."))
    try:
        prob_s1 = unigram_dict[query[0]]
    except KeyError:
        raise(MutualInfoError('The segment {} was not found in the corpus'.format(query[0])))
    try:
        prob_s2 = unigram_dict[query[1]]
    except KeyError:
        raise(MutualInfoError('The segment {} was not found in the corpus'.format(query[1])))
    try:
        prob_bg = bigram_dict[query]
    except KeyError:
        return None
        # raise(Exception('The bigram {} was not found in the corpus using {}s'.format(''.join(query),sequence_type)))

    if unigram_dict[query[0]] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[0]))
    if unigram_dict[query[1]] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[1]))
    if bigram_dict[query] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the bigram {} is not in the corpus.'.format(str(query)))

    return math.log((prob_bg/(prob_s1*prob_s2)), 2)


def get_in_word_unigram_frequencies(corpus, query, sequence_type, count_what):
    seg1_total = sum([get_frequency(word, count_what) if query[0] in getattr(word, sequence_type) else 0.0 for word in corpus])
    seg2_total = sum([get_frequency(word, count_what) if query[1] in getattr(word, sequence_type) else 0.0 for word in corpus])
    return {query[0]: seg1_total / len(corpus), query[1]: seg2_total / len(corpus)}

def get_in_word_bigram_frequency(corpus, query, sequence_type, count_what):
    total = sum([get_frequency(word, count_what) if query[0] in getattr(word, sequence_type) and query[1] in getattr(word, sequence_type) else 0.0 for word in corpus])
    return {query: total / len(corpus)}

def get_frequency(word, count_what):
    if count_what == 'type':
        return 1.0
    elif count_what == 'token':
        return float(getattr(word, 'frequency'))


def all_mis(corpus, sequence_type,
            halve_edges = False, in_word = False,
            stop_check = None, call_back = None):
    mis = {}
    total_calculations = ((len(corpus.inventory)**2)-len(corpus.inventory)/2)+1
    ct = 1
    t = time.time()
    for s1 in corpus.inventory:
        for s2 in corpus.inventory:
                print('Performing MI calculation {} out of {} possible'.format(str(ct), str(total_calculations)))
                ct += 1
                print('Duration of last calculation: {}'.format(str(time.time() - t)))
                t = time.time()
                if type(s1) != str:
                    s1 = s1.symbol
                if type(s2) != str:
                    s2 = s2.symbol
                print(s1,s2)
                mi = pointwise_mi(corpus, (s1, s2), sequence_type, halve_edges = halve_edges, in_word = in_word)
                mis[(s1,s2)] = mi

    ordered_mis = sorted([(pair, str(mis[pair])) for pair in mis], key=lambda p: p[1])

    return ordered_mis
