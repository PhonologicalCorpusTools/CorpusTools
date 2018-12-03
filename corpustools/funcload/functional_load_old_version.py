import re
from collections import defaultdict
from math import *
import itertools
import time

from .io import save_minimal_pairs


def _merge_segment_pairs(tier, segment_pairs, environment_filters):
    """Merge the specified segment pairs for the given tier of segments if 
    its position fits one of the environment filters. Return a string.
    """
    merged = []
    for i in range(len(tier)):
        merged.append(_check_to_add_merged(tier, i, segment_pairs, environment_filters))
    return ' '.join(merged)

def _check_to_add_merged(tier, i, segment_pairs, environment_filters):
    for sp in segment_pairs:
        if tier[i] in sp and _fits_environment(tier, i, environment_filters):
            return 'NEUTR:'+str(sp[0])+'/'+str(sp[1])
    return tier[i]

def _ready_for_re(word, index):
    w = [str(seg) for seg in word]
    w[index] = '_'
    return ' '.join(w)

def _fits_environment(tier, index, environment_filters):
    """
    Return True iff for tier, the environment
    of its index'th element fits passes one of the environment_filters.
    """
    if not environment_filters:
        return True
    ef_res = []
    for ef in environment_filters:
        tier_re = _ready_for_re(tier, index)
        ef_res.append(_make_environment_re(ef))

    return any([bool(re.search(env_re, tier_re)) for env_re in ef_res])

def _make_environment_re(environment_filter):
    if environment_filter.lhs:
        re_lhs = ' '.join(['('+('|'.join([seg for seg in position])+')') for position in environment_filter.lhs])
        re_lhs = re_lhs.replace('#', '^')
    else:
        re_lhs = ''

    if environment_filter.rhs:
        re_rhs = ' '.join(['('+('|'.join([seg for seg in position])+')') for position in environment_filter.rhs])
        re_rhs = re_rhs.replace('#', '$')
    else:
        re_rhs = ''

    if re_lhs and not re_lhs.endswith('^)'):
        re_lhs += ' '
    if re_rhs and not re_rhs.startswith('($'):
        re_rhs = ' ' + re_rhs

    return re_lhs + '_' + re_rhs


def _entropy(probabilities):
    """Calculate the entropy of a choice from the provided probability distribution.

    Parameters
    ---------
    probabilities : list of floats
        Contains the probability of each item in the list.

    Returns
    -------
    float
        Entropy
    """
    return -(sum([p*log(p,2) if p > 0 else 0 for p in probabilities]))


def minpair_fl(corpus_context, segment_pairs,
        relative_count = True, distinguish_homophones = False,
        environment_filters = None, prevent_normalization = False,
        stop_check = None, call_back = None):
    """Calculate the functional load of the contrast between two segments
    as a count of minimal pairs.

    Begin by creating a representation of each transcription that has collapsed
    all segment pairs (subject to the environment filter) and creating a dict
    with these segment-merged representations as keys, with lists of their
    respective words as values. Minimal pairs are then each pair of words within
    the list of words with the same segment-merged representation.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    segment_pairs : list of length-2 tuples of str
        The pairs of segments to be conflated.
    relative_count : bool, optional
        If True, divide the number of minimal pairs by the total count
        by the total number of words that contain either of the two segments.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and
        sock~shock (sock=punch) as just one minimal pair; but if True,
        you'll overcount alternative spellings of the same word, e.g.
        axel~actual and axle~actual. False is the value used by Wedel et al.
    environment_filters : list of EnvironmentFilter
        Allows the user to restrict the neutralization process to segments in
        particular segmental contexts
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    tuple(int or float, list)
        Tuple of: 0. if `relative_count`==False, an int of the raw number of
        minimal pairs; if `relative_count`==True, a float of that
        count divided by the total number of words in the corpus that
        include either `s1` or `s2`; and 1. list of minimal pairs.
    """
    if stop_check is not None and stop_check():
        return

    if not environment_filters:
        environment_filters = []

    all_target_segments = list(itertools.chain.from_iterable(segment_pairs))
    merged_dict = defaultdict(list)
    contain_target_segment_count = 0

    ## Create dict of words in lexicon, with segment-merged transcriptions as keys
    cur = 0
    for w in corpus_context:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        tier = getattr(w, corpus_context.sequence_type)
        ## Only add words with at least one of the target segments in the right
        ## environment (for relative_count, and to improve time/space efficiency)
        if any([s in all_target_segments and _fits_environment(tier, i, environment_filters) 
                for i, s in enumerate(tier)]):
            contain_target_segment_count += 1
            ## Create segment-pair-merged (neutralized) representations
            merged = _merge_segment_pairs(tier, segment_pairs, environment_filters)
            if 'NEUTR' in merged:
                merged_dict[merged].append(w)
    if stop_check is not None and stop_check():
        return

    ## Generate output
    result = 0
    minpairs = []
    for entry in merged_dict:
        if len(merged_dict[entry]) == 1: # can't contain a pair
            continue

        pairs = itertools.combinations(merged_dict[entry], 2)
        minpair_transcriptions = set()
        for w1, w2 in pairs:
            if (getattr(w1, corpus_context.sequence_type) != getattr(w2, corpus_context.sequence_type)):
                # avoids counting homophones
                if w1.spelling != w2.spelling: # avoids pronunc. variants
                    ordered_pair = sorted([(w1, getattr(w1, corpus_context.sequence_type)),
                                    (w2, getattr(w2, corpus_context.sequence_type))],
                                    key = lambda x: x[1]) # sort by tier/transcription
                    trans_pair = tuple([transcription for _, transcription in ordered_pair])
                    if distinguish_homophones:
                        result += 1
                    else:
                        if trans_pair not in minpair_transcriptions:
                            result += 1
                    minpair_transcriptions.add(trans_pair)
                    minpairs.append(tuple(ordered_pair))

    if relative_count and contain_target_segment_count > 0:
        result /= float(contain_target_segment_count)
    return (result, minpairs, segment_pairs, prevent_normalization)


def deltah_fl(corpus_context, segment_pairs, environment_filters = None,
              prevent_normalization = False, stop_check = None, call_back = None):
    """Calculate the functional load of the contrast between between two
    segments as the decrease in corpus entropy caused by a merger.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    segment_pairs : list of length-2 tuples of str
        The pairs of segments to be conflated.
    environment_filters : list of EnvironmentFilter
        Allows the user to restrict the neutralization process to segments in
    prevent_normalization : bool
        Prevents division of the entropy difference by the pre-merger entropy
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    float
        The difference between a) the entropy of the choice among
        non-homophonous words in the corpus before a merger of `s1`
        and `s2` and b) the entropy of that choice after the merger.
    """
    if not environment_filters:
        environment_filters = []

    original_sum = 0
    original_probs = defaultdict(float)
    neutralized_sum = 0
    neutralized_probs = defaultdict(float)

    cur = 0
    for w in corpus_context:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 20 == 0:
                call_back(cur)

        original_tier = getattr(w, corpus_context.sequence_type)
        original_probs[original_tier] += w.frequency
        original_sum += w.frequency

        neutralized_tier = _merge_segment_pairs(original_tier, segment_pairs, environment_filters)
        neutralized_probs[neutralized_tier] += w.frequency
        neutralized_sum += w.frequency


    if corpus_context.type_or_token == 'type':
        preneutr_h = log(len(original_probs), 2)
    else:
        original_probs = {k:v/original_sum for k,v in original_probs.items()}
        preneutr_h = _entropy(original_probs.values())

    if stop_check is not None and stop_check():
        return

    if corpus_context.type_or_token == 'type':
        postneutr_h = log(len(neutralized_probs), 2)
    else:
        neutralized_probs = {k:v/neutralized_sum for k,v in neutralized_probs.items()}
        postneutr_h = _entropy(neutralized_probs.values())

    if stop_check is not None and stop_check():
        return
        
    result = preneutr_h - postneutr_h
    if result < 1e-10:
        result = 0.0

    if not prevent_normalization and preneutr_h > 0.0:
        pre_norm = result
        result = result / preneutr_h
    else:
        pre_norm = result

    return (result, pre_norm)


def relative_minpair_fl(corpus_context, segment,
            relative_count = True, distinguish_homophones = False,
            output_filename = None, environment_filters = None,
            prevent_normalization = False,
            stop_check = None, call_back = None):
    """Calculate the average functional load of the contrasts between a
    segment and all other segments, as a count of minimal pairs.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    segment : str
        The target segment.
    relative_count : bool, optional
        If True, divide the number of minimal pairs by the total count
        by the total number of words that contain either of the two segments.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and
        sock~shock (sock=punch) as just one minimal pair; but if True,
        you'll overcount alternative spellings of the same word, e.g.
        axel~actual and axle~actual. False is the value used by Wedel et al.
    environment_filters : list of EnvironmentFilter
        Allows the user to restrict the neutralization process to segments in
        particular segmental contexts
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    int or float
        If `relative_count`==False, returns an int of the raw number of
        minimal pairs. If `relative_count`==True, returns a float of
        that count divided by the total number of words in the corpus
        that include either `s1` or `s2`.
    """
    if not environment_filters:
        environment_filters = []

    all_segments = corpus_context.inventory
    segment_pairs = [(segment,other.symbol) for other in all_segments
                        if other.symbol != segment and other.symbol != '#']

    results = []
    results_dict = {}
    to_output = []
    for sp in segment_pairs:
        res = minpair_fl(corpus_context, [sp],
            relative_count = relative_count,
            distinguish_homophones = distinguish_homophones,
            environment_filters = environment_filters,
            prevent_normalization = prevent_normalization,
            stop_check = stop_check, call_back = call_back)

        results_dict[sp] = res[0]
        results.append(res[0])
        print('Functional load of {}: {}'.format(sp, res[0]))

        if output_filename is not None:
            to_output.append((sp, res[1]))
    if output_filename is not None:
        save_minimal_pairs(output_filename, to_output)

    result = sum(results)/len(segment_pairs)
    return (result, results_dict, float(sum(results)))


def relative_deltah_fl(corpus_context, segment,
                environment_filters = None,
                prevent_normalization = False,
                stop_check = None, call_back = None):
    """Calculate the average functional load of the contrasts between a
    segment and all other segments, as the decrease in corpus entropy
    caused by a merger.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    segment : str
        The target segment.
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    float
        The difference between a) the entropy of the choice among
        non-homophonous words in the corpus before a merger of `s1`
        and `s2` and b) the entropy of that choice after the merger.
    """
    if not environment_filters:
        environment_filters = []

    all_segments = corpus_context.inventory
    segment_pairs = [(segment,other.symbol) for other in all_segments
                        if other.symbol != segment and other.symbol != '#']

    results = []
    results_dict = {}
    for sp in segment_pairs:
        res, pre_norm = deltah_fl(corpus_context, [sp],
                environment_filters=environment_filters,
                prevent_normalization = False,
                stop_check = stop_check, call_back = call_back)
        results.append(res)
        results_dict[sp] = res
        print('Functional load of {}: {}'.format(sp, res))

    result = sum(results)/len(segment_pairs)
    return (result, results_dict, float(sum(results)))



def collapse_segpairs_fl(corpus_context, **kwargs):
    func_type = kwargs.get('func_type')
    segment_pairs = kwargs.get('segment_pairs')
    relative_count = kwargs.get('relative_count')
    distinguish_homophones = kwargs.get('distinguish_homophones')
    if func_type == 'min_pairs':
        fl = minpair_fl(corpus_context, segment_pairs,
                        relative_count, distinguish_homophones,
                          environment_filters=environment_filters)
    elif func_type == 'entropy':
        fl = deltah_fl(corpus_context, segment_pairs,
          environment_filters=environment_filters)



def individual_segpairs_fl(corpus_context, **kwargs):
    func_type = kwargs.get('func_type')
    segment_pairs = kwargs.get('segment_pairs')
    relative_count = kwargs.get('relative_count')
    distinguish_homophones = kwargs.get('distinguish_homophones')

    results = []
    for pair in segment_pairs:
        if func_type == 'min_pairs':
            fl = minpair_fl(corpus_context, [pair],
                            relative_count, distinguish_homophones,
                              environment_filters=environment_filters)
        elif func_type == 'entropy':
            fl = deltah_fl(corpus_context, [pair],
              environment_filters=environment_filters)
        results.append(fl)


def neutralize_segment(segment, segment_pairs):
    for sp in segment_pairs:
        try:
            s = segment.symbol
        except AttributeError:
            s = segment
        if s in sp:
            return 'NEUTR:'+''.join(str(x) for x in sp)
    return s


def all_pairwise_fls(corpus_context, relative_fl = False,
                    algorithm = 'minpair',
                    prevent_normalization = False,
                    relative_count = True, distinguish_homophones = False,
                    environment_filters = None):
    """Calculate the functional load of the contrast between two segments as a count of minimal pairs.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    relative_fl : bool
        If False, return the FL for all segment pairs. If True, return
        the relative (average) FL for each segment.
    algorithm : str {'minpair', 'deltah'}
        Algorithm to use for calculating functional load: "minpair" for
        minimal pair count or "deltah" for change in entropy.
    relative_count : bool, optional
        If True, divide the number of minimal pairs by the total count
        by the total number of words that contain either of the two segments.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and
        sock~shock (sock=punch) as just one minimal pair; but if True,
        you'll overcount alternative spellings of the same word, e.g.
        axel~actual and axle~actual. False is the value used by Wedel et al.
    environment_filters : list of EnvironmentFilter
        Allows the user to restrict the neutralization process to segments in
        particular segmental contexts

    Returns
    -------
    list of tuple(tuple(str, st), float)
    OR
    list of (str, float)
        Normally returns a list of all Segment pairs and their respective functional load values, as length-2 tuples ordered by FL.
        If calculating relative FL, returns a dictionary of each segment and its relative (average) FL, with entries ordered by FL.
    """
    if not environment_filters:
        environment_filters = []

    fls = {}
    total_calculations = ((((len(corpus_context.inventory)-1)**2)-len(corpus_context.inventory)-1)/2)+1
    ct = 1
    t = time.time()
    if '' in corpus_context.inventory:
        raise Exception('Warning: Calculation of functional load for all segment pairs requires that all items in corpus have a non-null transcription.')
    for i, s1 in enumerate(corpus_context.inventory[:-1]):
        for s2 in corpus_context.inventory[i+1:]:
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
                    fl = minpair_fl(corpus_context, [(s1, s2)],
                            relative_count=relative_count,
                            distinguish_homophones=distinguish_homophones,
                            environment_filters=environment_filters)[0]
                elif algorithm == 'deltah':
                    fl = deltah_fl(corpus_context, [(s1, s2)],
                    environment_filters=environment_filters)
                fls[(s1, s2)] = fl
    if not relative_fl:
        ordered_fls = sorted([(pair, fls[pair]) for pair in fls], key=lambda p: p[1], reverse=True)
        return ordered_fls
    elif relative_fl:
        rel_fls = {}
        for s in corpus_context.inventory:
            if type(s) != str:
                s = s.symbol
            if s != '#':
                total = 0.0
                for pair in fls:
                    if s == pair[0] or s == pair[1]:
                        total += fls[pair]
                rel_fls[s] = total / (len(corpus_context.inventory) - 1)
        ordered_rel_fls = sorted([(s, rel_fls[s]) for s in rel_fls], key=lambda p: p[1], reverse=True)
        return ordered_rel_fls
