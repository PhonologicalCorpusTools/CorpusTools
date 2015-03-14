import re
from collections import defaultdict
from math import *
import itertools
import queue
import copy
from math import factorial
import time


def minpair_fl(corpus, segment_pairs, frequency_cutoff = 0,
        relative_count = True, distinguish_homophones = False,
        sequence_type = 'transcription',
        stop_check = None, call_back = None):
    """Calculate the functional load of the contrast between two segments
    as a count of minimal pairs.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.
    segment_pairs : list of length-2 tuples of str
        The pairs of segments to be conflated.
    frequency_cutoff : number, optional
        Minimum frequency of words to consider, if desired.
    relative_count : bool, optional
        If True, divide the number of minimal pairs by the total count
        by the total number of words that contain either of the two segments.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and
        sock~shock (sock=punch) as just one minimal pair; but if True,
        you'll overcount alternative spellings of the same word, e.g.
        axel~actual and axle~actual. False is the value used by Wedel et al.
    sequence_type : string
        The attribute of Words to calculate FL over. Normally this will
        be the transcription, but it can also be the spelling or a
        user-specified tier.

    Returns
    -------
    int or float
        If `relative_count`==False, returns an int of the raw number of
        minimal pairs. If `relative_count`==True, returns a float of that
        count divided by the total number of words in the corpus that
        include either `s1` or `s2`.
    """

    if frequency_cutoff > 0.0:

        corpus = [word for word in corpus if word.frequency >= frequency_cutoff]
    if stop_check is not None and stop_check():
        return
    all_segments = list(itertools.chain.from_iterable(segment_pairs))

    neutralized = list()
    if call_back is not None:
        call_back('Finding and neutralizing instances of segments...')
        call_back(0,len(corpus))
        cur = 0
    for w in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        if frequency_cutoff > 0 and w.frequency < frequency_cutoff:
            continue
        if any([s in getattr(w, sequence_type) for s in all_segments]):
            n = [neutralize_segment(seg, segment_pairs)
                    for seg in getattr(w, sequence_type)]
            neutralized.append(('.'.join(n), w.spelling.lower(), getattr(w, sequence_type)))
    if stop_check is not None and stop_check():
        return


    def matches(first, second):
        return (first[0] == second[0] and first[1] != second[1]
            and 'NEUTR:' in first[0] and 'NEUTR:' in second[0]
            and first[2] != second[2])

    minpairs = list()
    if call_back is not None:
        call_back('Counting minimal pairs...')
        call_back(0,factorial(len(neutralized))/(factorial(len(neutralized)-2)*2))
        cur = 0
    for first,second in itertools.combinations(neutralized, 2):
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        if not matches(first,second):
            continue
        ordered_pair = sorted([str(first[2]), str(second[2])])
        minpairs.append(tuple(ordered_pair))

    if not distinguish_homophones:
        minpairs = set(minpairs)

    result = len(minpairs)
    if relative_count and len(neutralized) > 0:
        result /= len(neutralized)

    return result


def deltah_fl(corpus, segment_pairs, frequency_cutoff = 0,
            type_or_token = 'token', sequence_type = 'transcription',
            stop_check = None, call_back = None):
    """Calculate the functional load of the contrast between between two
    segments as the decrease in corpus entropy caused by a merger.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.
    segment_pairs : list of length-2 tuples of str
        The pairs of segments to be conflated.
    frequency_cutoff : number, optional
        Minimum frequency of words to consider, if desired.
    type_or_token : str {'type', 'token'}
        Specify whether entropy is based on type or token frequency.
    sequence_type : string
        The attribute of Words to calculate FL over. Normally this will be the
        transcription, but it can also be the spelling or a user-specified tier.

    Returns
    -------
    float
        The difference between a) the entropy of the choice among
        non-homophonous words in the corpus before a merger of `s1`
        and `s2` and b) the entropy of that choice after the merger.
    """
    if call_back is not None:
        call_back('Finding instances of segments...')
        call_back(0,len(corpus))
        cur = 0
    freq_sum = 0
    original_probs = defaultdict(float)
    for w in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        if frequency_cutoff > 0.0 and w.frequency < frequency_cutoff:
            continue

        if type_or_token == 'type':
            f = 1
        else:
            f = w.frequency

        original_probs[str(getattr(w, sequence_type))] += f
        freq_sum += f

    original_probs = {k:v/freq_sum for k,v in original_probs.items()}

    if stop_check is not None and stop_check():
        return
    preneutr_h = entropy([original_probs[item] for item in original_probs])

    neutralized_probs = defaultdict(float)
    if call_back is not None:
        call_back('Neutralizing instances of segments...')
        call_back(0,len(list(original_probs.keys())))
        cur = 0
    for k,v in original_probs.items():
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        neutralized_probs['.'.join([neutralize_segment(s, segment_pairs) for s in k.split('.')])] += v
    postneutr_h = entropy([neutralized_probs[item] for item in neutralized_probs])

    if stop_check is not None and stop_check():
        return
    result = preneutr_h - postneutr_h
    if result < 1e-10:
        result = 0.0

    return result


def relative_minpair_fl(corpus, segment, frequency_cutoff = 0,
            relative_count = True, distinguish_homophones = False,
            sequence_type = 'transcription',
            stop_check = None, call_back = None):
    """Calculate the average functional load of the contrasts between a
    segment and all other segments, as a count of minimal pairs.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.

    segment : str
        The target segment.

    frequency_cutoff : number, optional
        Minimum frequency of words to consider, if desired.

    relative_count : bool, optional
        If True, divide the number of minimal pairs by the total count
        by the total number of words that contain either of the two segments.

    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and
        sock~shock (sock=punch) as just one minimal pair; but if True,
        you'll overcount alternative spellings of the same word, e.g.
        axel~actual and axle~actual. False is the value used by Wedel et al.

    sequence_type : string
        The attribute of Words to calculate FL over. Normally this will
        be the transcription, but it can also be the spelling or a
        user-specified tier.

    Returns
    -------
    int or float
        If `relative_count`==False, returns an int of the raw number of
        minimal pairs. If `relative_count`==True, returns a float of
        that count divided by the total number of words in the corpus
        that include either `s1` or `s2`.
    """
    all_segments = list(set(itertools.chain.from_iterable([segment for word in corpus for segment in getattr(word, sequence_type)])))
    segment = segment[:]
    segment_pairs = [(segment,other) for other in all_segments if other != segment]
    results = []
    for sp in segment_pairs:
        results.append(minpair_fl(corpus, [sp], frequency_cutoff = frequency_cutoff,
            relative_count = relative_count,
            distinguish_homophones = distinguish_homophones,
            sequence_type=sequence_type,
            stop_check = stop_check, call_back = call_back))
    return sum(results)/len(segment_pairs)


def relative_deltah_fl(corpus, segment, frequency_cutoff = 0,
                type_or_token = 'token', sequence_type = 'transcription',
                stop_check = None, call_back = None):
    """Calculate the average functional load of the contrasts between a
    segment and all other segments, as the decrease in corpus entropy
    caused by a merger.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.

    segment : str
        The target segment.

    frequency_cutoff : number, optional
        Minimum frequency of words to consider, if desired.

    type_or_token : str {'type', 'token'}
        Specify whether entropy is based on type or token frequency.

    sequence_type : string
        The attribute of Words to calculate FL over. Normally this
        will be the transcription, but it can also be the spelling or a
        user-specified tier.

    Returns
    -------
    float
        The difference between a) the entropy of the choice among
        non-homophonous words in the corpus before a merger of `s1`
        and `s2` and b) the entropy of that choice after the merger.
    """
    all_segments = list(set(itertools.chain.from_iterable([segment for word in corpus for segment in getattr(w, sequence_type)])))
    segment = segment[:]
    segment_pairs = [(segment,other) for other in all_segments if other != segment]
    results = []
    for sp in segment_pairs:
        results.append(deltah_fl(corpus, [sp], frequency_cutoff = frequency_cutoff,
                type_or_token = type_or_token, sequence_type = sequence_type,
                stop_check = stop_check, call_back = call_back))
    return sum(results)/len(segment_pairs)



def collapse_segpairs_fl(**kwargs):
    corpus = kwargs.get('corpus')
    func_type = kwargs.get('func_type')
    segment_pairs = kwargs.get('segment_pairs')
    frequency_cutoff = kwargs.get('frequency_cutoff')
    relative_count = kwargs.get('relative_count')
    distinguish_homophones = kwargs.get('distinguish_homophones')
    type_or_token = kwargs.get('type_or_token')
    sequence_type = kwargs.get('sequence_type')
    q = kwargs.get('threaded_q')
    if func_type == 'min_pairs':
        fl = minpair_fl(corpus, segment_pairs, frequency_cutoff, relative_count, distinguish_homophones, sequence_type)
    elif func_type == 'entropy':
        fl = deltah_fl(corpus, segment_pairs, frequency_cutoff, type_or_token, sequence_type)
    q.put(fl)



def individual_segpairs_fl(**kwargs):
    corpus = kwargs.get('corpus')
    func_type = kwargs.get('func_type')
    segment_pairs = kwargs.get('segment_pairs')
    frequency_cutoff = kwargs.get('frequency_cutoff')
    relative_count = kwargs.get('relative_count')
    distinguish_homophones = kwargs.get('distinguish_homophones')
    type_or_token = kwargs.get('type_or_token')
    sequence_type = kwargs.get('sequence_type')
    q = kwargs.get('threaded_q')

    results = list()
    for pair in segment_pairs:
        corpus_copy = copy.deepcopy(corpus)
        if func_type == 'min_pairs':
            fl = minpair_fl(corpus_copy, [pair], frequency_cutoff, relative_count, distinguish_homophones, sequence_type)
        elif func_type == 'entropy':
            fl = deltah_fl(corpus_copy, [pair], frequency_cutoff, type_or_token, sequence_type)
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
    try: # segment is a segment
        for sp in segment_pairs:
            if segment.symbol in sp:
                return 'NEUTR:'+''.join(sp)
        return segment.symbol
    except: # segment is a str
        for sp in segment_pairs:
            if segment in sp:
                return 'NEUTR:'+''.join(sp)
        return segment


def all_pairwise_fls(corpus, relative_fl=False, algorithm='minpair', frequency_cutoff=0, relative_count=True,
                     distinguish_homophones=False, sequence_type='transcription', type_or_token='token'):
    """Calculate the functional load of the contrast between two segments as a count of minimal pairs.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.
    relative_fl : bool
        If False, return the FL for all segment pairs. If True, return the relative (average) FL for each segment.
    algorithm : str {'minpair', 'deltah'}
        Algorithm to use for calculating functional load: "minpair" for minimal pair count or "deltah" for change in entropy.
    frequency_cutoff : number, optional
        Minimum frequency of words to consider, if desired.
    relative_count : bool, optional
        If True, divide the number of minimal pairs by the total count by the total number of words that contain either of the two segments.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and sock~shock (sock=punch) as just one minimal pair; but if True, you'll overcount alternative spellings of the same word, e.g. axel~actual and axle~actual. False is the value used by Wedel et al.
    sequence_type : string
        The attribute of Words to calculate FL over. Normally this will be the transcription, but it can also be the spelling or a user-specified tier.
    type_or_token : str {'type', 'token'}
        Specify whether entropy is based on type or token frequency. Only used by the deltah algorithm.

    Returns
    -------
    list of tuple(tuple(str, st), float)
    OR
    list of (str, float)
        Normally returns a list of all Segment pairs and their respective functional load values, as length-2 tuples ordered by FL.
        If calculating relative FL, returns a dictionary of each segment and its relative (average) FL, with entries ordered by FL.
    """
    fls = {}
    total_calculations = (len(corpus.inventory)-1)**2
    ct = 1
    t = time.time()
    for i, s1 in enumerate(corpus.inventory[:-1]):
        for s2 in corpus.inventory[i+1:]:
            if s1 != '#' and s2 != '#':
                print('Performing FL calculation {} out of {} possible'.format(str(ct), str(total_calculations)))
                ct += 1
                print('Duration of last calculation: {}'.format(str(time.time() - t)))
                t = time.time()
                if type(s1) != str:
                    s1 = s1.symbol
                if type(s2) != str:
                    s2 = s2.symbol
                if algorithm == 'minpair':
                    fl = minpair_fl(corpus, [(s1, s2)], frequency_cutoff=frequency_cutoff, relative_count=relative_count, distinguish_homophones=distinguish_homophones, sequence_type=sequence_type)
                elif algorithm == 'deltah':
                    fl = deltah_fl(corpus, [(s1, s2)], frequency_cutoff=frequency_cutoff, type_or_token=type_or_token, sequence_type=sequence_type)
                fls[(s1, s2)] = fl
    if not relative_fl:
        ordered_fls = sorted([(pair, fls[pair]) for pair in fls], key=lambda p: p[1], reverse=True)
        return ordered_fls
    elif relative_fl:
        rel_fls = {}
        for s in corpus.inventory:
            if type(s) != str:
                s = s.symbol
            if s != '#':
                total = 0.0
                for pair in fls:
                    if s == pair[0] or s == pair[1]:
                        total += fls[pair]
                rel_fls[s] = total / (len(corpus.inventory) - 1)
        ordered_rel_fls = sorted([(s, rel_fls[s]) for s in rel_fls], key=lambda p: p[1], reverse=True)
        return ordered_rel_fls
