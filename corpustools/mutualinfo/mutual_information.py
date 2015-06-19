# -*- coding: utf-8 -*-

import sys
import math
from collections import defaultdict
from corpustools.corpus.classes.lexicon import CorpusIntegrityError

import time

from corpustools.exceptions import MutualInfoError

def pointwise_mi(corpus_context, query, halve_edges = False, in_word = False,
                stop_check = None, call_back = None):
    """
    Calculate the mutual information for a bigram.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    query : tuple
        Tuple of two strings, each a segment/letter
    halve_edges : bool
        Flag whether to only count word boundaries once per word rather than
        twice, defaults to False
    in_word : bool
        Flag to calculate non-local, non-ordered mutual information,
        defaults to False
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    float
        Mutual information of the bigram
    """
    if call_back is not None:
        call_back("Generating probabilities...")
        call_back(0,0)
        cur = 0
    if in_word:
        unigram_dict = get_in_word_unigram_frequencies(corpus_context, query)
        bigram_dict = get_in_word_bigram_frequency(corpus_context, query)
    else:
        unigram_dict = corpus_context.get_frequency_base(gramsize = 1, halve_edges = halve_edges, probability=True)
        bigram_dict = corpus_context.get_frequency_base(gramsize = 2, halve_edges = halve_edges, probability=True)

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
        raise MutualInfoError('The bigram {} was not found in the corpus using {}s'.format(''.join(query),sequence_type))


    if unigram_dict[query[0]] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[0]))
    if unigram_dict[query[1]] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[1]))
    if bigram_dict[query] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the bigram {} is not in the corpus.'.format(str(query)))


    return math.log((prob_bg/(prob_s1*prob_s2)), 2)


def get_in_word_unigram_frequencies(corpus_context, query):
    totals = [0 for x in query]
    for word in corpus_context:
        for i, q in enumerate(query):
            if q in getattr(word, corpus_context.sequence_type):
                totals[i] += word.frequency
    return {k: totals[i] / len(corpus_context) for i, k in enumerate(query)}

def get_in_word_bigram_frequency(corpus_context, query):
    total = 0
    for word in corpus_context:
        tier = getattr(word, corpus_context.sequence_type)
        if all(x in tier for x in query):
            total += word.frequency
    return {query: total / len(corpus_context)}

def all_mis(corpus_context,
            halve_edges = False, in_word = False,
            stop_check = None, call_back = None):
    mis = {}
    total_calculations = ((len(corpus_context.inventory)**2)-len(corpus_context.inventory)/2)+1
    ct = 1
    t = time.time()
    for s1 in corpus_context.inventory:
        for s2 in corpus_context.inventory:
                #print('Performing MI calculation {} out of {} possible'.format(str(ct), str(total_calculations)))
                ct += 1
                #print('Duration of last calculation: {}'.format(str(time.time() - t)))
                t = time.time()
                if type(s1) != str:
                    s1 = s1.symbol
                if type(s2) != str:
                    s2 = s2.symbol
                #print(s1,s2)
                mi = pointwise_mi(corpus_context, (s1, s2), halve_edges = halve_edges, in_word = in_word)
                mis[(s1,s2)] = mi

    ordered_mis = sorted([(pair, str(mis[pair])) for pair in mis], key=lambda p: p[1])

    return ordered_mis
