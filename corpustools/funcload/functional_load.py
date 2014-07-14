import re
from collections import defaultdict
from math import *
import itertools
import queue
import copy

from corpustools.corpus.classes import CorpusFactory




def minpair_fl(corpus, segment_pairs, frequency_cutoff=0, relative_count=True, distinguish_homophones=False, threaded_q=False):
    """Calculate the functional load of the contrast between two segments as a count of minimal pairs.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.
    segment_pairs : list of length-2 tuples of Segments
        The pairs of Segments to be conflated.
    frequency_cutoff : number, optional
        Minimum frequency of words to consider, if desired.
    relative_count : bool, optional
        If True, divide the number of minimal pairs by the total count by the total number of words that contain either of the two segments.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and sock~shock (sock=punch) as just one minimal pair; but if True, you'll overcount alternative spellings of the same word, e.g. axel~actual and axle~actual. False is the value used by Wedel et al.

    Returns
    -------
    int or float
        If `relative_count`==False, returns an int of the raw number of minimal pairs. If `relative_count`==True, returns a float of that count divided by the total number of words in the corpus that include either `s1` or `s2`.
     """
    if threaded_q:
        q = threaded_q

    if frequency_cutoff > 0:
        corpus = [word for word in corpus if word.frequency >= frequency_cutoff]

    all_segments = list(itertools.chain.from_iterable(segment_pairs))

    corpus = [word for word in corpus if any([s in word for s in all_segments])]
    scope = len(corpus)

    trans_spell = [(tuple(word.transcription), word.spelling.lower()) for word in corpus]

    neutralized = [(' '.join([neutralize_segment(seg, segment_pairs) for seg in word[0]]), word[1], word[0]) for word in list(trans_spell)]


    def matches(first, second):
        return (first[0] == second[0] and first[1] != second[1]
            and 'NEUTR:' in first[0] and 'NEUTR:' in second[0] and first[2] != second[2])

    minpairs = [(first, second) for first, second in itertools.combinations(neutralized, 2) if matches(first, second)]

    if distinguish_homophones == False:
        minpairs = list(set([mp[0][0] for mp in minpairs]))

    result = len(minpairs)
    if relative_count:
        result /= scope

    if not threaded_q:
        return result
    else:
        threaded_q.put(result)
        return None


def deltah_fl(corpus, segment_pairs, frequency_cutoff=0, type_or_token='token', threaded_q=False):
    """Calculate the functional load of the contrast between between two segments as the decrease in corpus entropy caused by a merger.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.
    segment_pairs : list of length-2 tuples of Segments
        The pairs of Segments to be conflated.
    frequency_cutoff : number, optional
        Minimum frequency of words to consider, if desired.
    type_or_token : str {'type', 'token'}
        Specify whether entropy is based on type or token frequency.

    Returns
    -------
    float
        The difference between a) the entropy of the choice among non-homophonous words in the corpus before a merger of `s1` and `s2` and b) the entropy of that choice after the merger.
    """
    if type_or_token == None:
        type_or_token = 'token'
    if frequency_cutoff > 0:
        corpus = [word for word in corpus if word.frequency >= frequency_cutoff]

    if type_or_token == 'type':
        freq_sum = len(corpus)
    else: # token frequencies
        freq_sum = sum([word.frequency for word in corpus])

    original_probs = defaultdict(float)
    if type_or_token == 'type':
        for word in corpus:
            original_probs[' '.join([str(s) for s in word.transcription])] += 1.0/freq_sum
    elif type_or_token == 'token':
        for word in corpus:
            original_probs[' '.join([str(s) for s in word.transcription])] += float(word.frequency)/freq_sum
    preneutr_h = entropy([original_probs[item] for item in original_probs])

    neutralized_probs = defaultdict(float)
    for item in original_probs:
        neutralized_probs[' '.join([neutralize_segment(s, segment_pairs) for s in item.split(' ')])] += original_probs[item]
    postneutr_h = entropy([neutralized_probs[item] for item in neutralized_probs])

    result = preneutr_h - postneutr_h
    if result < 1e-10:
        result = 0.0

    if not threaded_q:
        return result
    else:
        threaded_q.put(result)
        return None

def collapse_segpairs_fl(**kwargs):
    corpus = kwargs.get('corpus')
    func_type = kwargs.get('func_type')
    segment_pairs = kwargs.get('segment_pairs')
    frequency_cutoff = kwargs.get('frequency_cutoff')
    relative_count = kwargs.get('relative_count')
    distinguish_homophones = kwargs.get('distinguish_homophones')
    type_or_token = kwargs.get('type_or_token')
    q = kwargs.get('threaded_q')
    if func_type == 'min_pairs':
        fl = minpair_fl(corpus, segment_pairs, frequency_cutoff, relative_count, distinguish_homophones)
    elif func_type == 'entropy':
        fl = deltah_fl(corpus, segment_pairs, frequency_cutoff, type_or_token)
    q.put(fl)



def individual_segpairs_fl(**kwargs):
    corpus = kwargs.get('corpus')
    func_type = kwargs.get('func_type')
    segment_pairs = kwargs.get('segment_pairs')
    frequency_cutoff = kwargs.get('frequency_cutoff')
    relative_count = kwargs.get('relative_count')
    distinguish_homophones = kwargs.get('distinguish_homophones')
    type_or_token = kwargs.get('type_or_token')
    q = kwargs.get('threaded_q')

    results = list()
    for pair in segment_pairs:
        corpus_copy = copy.deepcopy(corpus)
        if func_type == 'min_pairs':
            fl = minpair_fl(corpus_copy, [pair], frequency_cutoff, relative_count, distinguish_homophones)
        elif func_type == 'entropy':
            fl = deltah_fl(corpus_copy, [pair], frequency_cutoff, type_or_token)
        results.append(fl)

    q.put(results)


def entropy(probabilities):
    """Calculate the entropy of a choice from the provided probability distribution.

    Parameters
    ---------
    probabilities : list of floats
        Contains the probability of each item in the list.

    Returns
    -------
    float
    """
    return -(sum([p*log(p,2) if p > 0 else 0 for p in probabilities]))


def neutralize_segment(segment, segment_pairs):
    try: # segment is a Segment
        for sp in segment_pairs:
            if segment.symbol in sp:
                return 'NEUTR:'+''.join(sp)
        return segment.symbol
    except: # segment is a str
        for sp in segment_pairs:
            if segment in sp:
                return 'NEUTR:'+''.join(sp)
        return segment
