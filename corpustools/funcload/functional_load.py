import re
from collections import defaultdict
from math import *
import itertools
from math import factorial
import time

from corpustools.exceptions import FuncLoadError 
from corpustools.funcload.io import save_minimal_pairs 
from corpustools.corpus.classes.lexicon import EnvironmentFilter


def is_minpair(first, second, corpus_context, segment_pairs, environment_filter): 
    """Return True iff first/second are a minimal pair.
    Checks that all segments in those words are identical OR a valid segment pair
    (from segment_pairs) and fit the environment_filter, and that there is at least
    one difference between first and second.

    Parameters
    ----------

    first, second: Word
        Two words to evaluate as a minimal pair. 
    corpus_context: CorpusContext
        The context manager that the corpus should be evaluated from (e.g., canonical variants).
    segment_pairs: List
        list of length-2 tuples of str
    environment_filter: Environment
        The environment in which words should be evaluated for being a minimal pair.
    
    """
    first = getattr(first, corpus_context.sequence_type)
    second = getattr(second, corpus_context.sequence_type)
    if len(first) != len(second):
        return False
    has_difference = False
    for i in range(len(first)):
        if first[i] == second[i]:
            continue
        elif (conflateable(first[i], second[i], segment_pairs) 
            and fits_environment(first, second, i, environment_filter)): 
            has_difference = True
            continue
        else:
            return False
    if has_difference:
        return True


def conflateable(seg1, seg2, segment_pairs):
    """Return True iff seg1 and seg2 are exactly one of the segment pairs
    in segment_pairs (ignoring ordering of either).

    seg1 and seg2 will never be identical in the input.

    Parameters
    ----------

    seg1, seg2: Segment
        Two segments on which minimal pairs might hinge. 
    segment_pairs: List
        list of length-2 tuples of str
    
    """
    for segment_pair in segment_pairs:
        seg_set = set(segment_pair)
        if seg1 in seg_set and seg2 in seg_set:
            return True
    return False


def fits_environment(w1, w2, index, environment_filter):
    """Return True iff for both w1 and w2 (tiers), the environment
    of its i'th element passes the environment_filter.

    """
    if not environment_filter:
        return True

    def ready_for_re(word, index):
        w = [str(seg) for seg in word]
        w[index] = '_'
        return ' '.join(w)

    w1 = ready_for_re(w1, index)
    w2 = ready_for_re(w2, index)
    env_re = make_environment_re(environment_filter) 

    return (bool(re.search(env_re, w1)) and bool(re.search(env_re, w2)))


def ready_for_re(word, index):
        w = [str(seg) for seg in word]
        w[index] = '_'
        return ' '.join(w)

def make_environment_re(environment_filter): 
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
    if re_rhs and not re_rhs.endswith('($'):
        re_rhs = ' ' + re_rhs
    return re_lhs + '_' + re_rhs


# This is the function I really edited
# I changed the parameter called 'relative_count' to 'relative_count_to_relevant_sounds' and changed its default value.
# I added a new parameter, 'relative_count_to_whole_corpus', and set its default to true.
# I updated the doc strings.
def minpair_fl(corpus_context, segment_pairs,
        relative_count_to_relevant_sounds = False, relative_count_to_whole_corpus = True, distinguish_homophones = False,
        environment_filter = None, prevent_normalization = False,
        stop_check = None, call_back = None):
    """Calculate the functional load of the contrast between two segments
    as a count of minimal pairs.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    segment_pairs : list of length-2 tuples of str
        The pairs of segments to be conflated.
    relative_count_to_relevant_sounds : bool, optional
        If True, divide the number of minimal pairs by 
        by the total number of words that contain either of the two segments.
        # changed the name of this from "relative_count" to "relative_count_to_relevant_sounds"
        # set its default to False above
    relative_count_to_whole_corpus : bool, optional
        If True, divide the number of minimal pairs by the total number of words 
        in the corpus (regardless of whether those words contain the target sounds).
        Defaults to True.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and
        sock~shock (sock=punch) as just one minimal pair; but if True,
        you'll overcount alternative spellings of the same word, e.g.
        axel~actual and axle~actual. False is the value used by Wedel et al.
    environment_filter : EnvironmentFilter
        Allows the user to restrict the neutralization process to segments in
        particular segmental contexts
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    tuple(int or float, list)
        Tuple of: 0. if `relative_count_to_relevant_sounds`==False and 
        `relative_count_to_whole_corpus`==False, an int of the raw number of
        minimal pairs; if `relative_count_to_relevant_sounds`==True, a float of that
        count divided by the total number of words in the corpus that
        include either `s1` or `s2`; if `relative_count_to_whole_corpus`==True, a
        float of the raw count divided by the total number of words in the corpus; 
        and 1. list of minimal pairs.
    """

    if stop_check is not None and stop_check():
        return

    ## Count the number of words in the corpus (needed if relative_count_to_whole_corpus is True)
    num_words_in_corpus = len(corpus_context.corpus)

    ## Filter out words that have none of the target segments
    ## (for relative_count_to_relevant_sounds as well as improving runtime)
    contain_target_segment = []
    if call_back is not None:
        call_back('Finding words with the specified segments...')
        call_back(0, len(corpus_context))
        cur = 0

    all_target_segments = list(itertools.chain.from_iterable(segment_pairs)) # creates a list of target segments from the list of tuples
    for w in corpus_context: # loops through the words in the context manager
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        tier = getattr(w, corpus_context.sequence_type)
        if any([s in tier for s in all_target_segments]):
                contain_target_segment.append(w)
    if stop_check is not None and stop_check():
        return

    ## Find minimal pairs
    minpairs = []
    if call_back is not None:
        call_back('Finding minimal pairs...')
        if len(contain_target_segment) >= 2:
            call_back(0,factorial(len(contain_target_segment))/(factorial(len(contain_target_segment)-2)*2))
        cur = 0
    for first, second in itertools.combinations(contain_target_segment, 2):
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        if is_minpair(first, second, corpus_context, segment_pairs, environment_filter):
            ordered_pair = sorted([(first, getattr(first, corpus_context.sequence_type)),
                                   (second, getattr(second, corpus_context.sequence_type))],
                                   key = lambda x: x[1]) # sort by tier/transcription
            minpairs.append(tuple(ordered_pair))

    ## Generate output 
    if not distinguish_homophones:
        actual_minpairs = {}

        for pair in minpairs:
            if stop_check is not None and stop_check():
                return
            key = (pair[0][1], pair[1][1]) # Keys are tuples of transcriptions
            if key not in actual_minpairs:
                actual_minpairs[key] = (pair[0][0], pair[1][0]) # Values are words
            else:
                pair_freq = pair[0][0].frequency + pair[1][0].frequency
                existing_freq = actual_minpairs[key][0].frequency + \
                                actual_minpairs[key][1].frequency
                if pair_freq > existing_freq:
                    actual_minpairs[key] = (pair[0][0], pair[1][0])
        result = sum((x[0].frequency + x[1].frequency)/2
                    for x in actual_minpairs.values())
    else:
        result = sum((x[0][0].frequency + x[1][0].frequency)/2 for x in minpairs)

    if relative_count_to_relevant_sounds and len(contain_target_segment) > 0:
        result /= sum(x.frequency for x in contain_target_segment)
        
    elif relative_count_to_whole_corpus:
        result = result / num_words_in_corpus
    
    return (result, minpairs)


def deltah_fl(corpus_context, segment_pairs, environment_filter = None, prevent_normalization = False,
            stop_check = None, call_back = None):
    """Calculate the functional load of the contrast between between two
    segments as the decrease in corpus entropy caused by a merger.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    segment_pairs : list of length-2 tuples of str
        The pairs of segments to be conflated.
    environment_filter : EnvironmentFilter
        Allows the user to restrict the neutralization process to segments in
        particular segmental contexts
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
    if call_back is not None:
        call_back('Finding instances of segments...')
        call_back(0, len(corpus_context))
        cur = 0
    freq_sum = 0
    original_probs = defaultdict(float)

    all_target_segments = list(itertools.chain.from_iterable(segment_pairs))
    if environment_filter:
        filled_environment = EnvironmentFilter(tuple(all_target_segments),
                                               environment_filter.lhs,
                                               environment_filter.rhs)

    for w in corpus_context:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 20 == 0:
                call_back(cur)

        f = w.frequency

        original_probs[getattr(w, corpus_context.sequence_type)] += f
        freq_sum += f

    original_probs = {k:v/freq_sum for k,v in original_probs.items()}

    if stop_check is not None and stop_check():
        return
    preneutr_h = entropy(original_probs.values())

    neutralized_probs = defaultdict(float)
    if call_back is not None:
        call_back('Neutralizing instances of segments...')
        call_back(0, len(list(original_probs.keys())))
        cur = 0
    for k,v in original_probs.items():
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        if not environment_filter or k.find(filled_environment):
            n = [neutralize_segment(seg, segment_pairs)
                    for seg in k]
            neutralized_probs['.'.join(n)] += v
    postneutr_h = entropy(neutralized_probs.values())

    if stop_check is not None and stop_check():
        return

    result = preneutr_h - postneutr_h
    if result < 1e-10:
        result = 0.0

    if not prevent_normalization and preneutr_h > 0.0:
        result = result / preneutr_h

    return result


# This function is weirdly named. It should really be something like
# average_minpair_fl
# It has also been changed so as to have two "relativizer" options:
# one to words containing the relevant segments and one to all
# words in the corpus (though it basically does the calculation
# by calling the above minpair_fl() function).
def relative_minpair_fl(corpus_context, segment,
            relative_count_to_relevant_sounds = False, relative_count_to_whole_corpus = True, 
            distinguish_homophones = False, output_filename = None, environment_filter = None,
            prevent_normalization = False, stop_check = None, call_back = None):
    """Calculate the average functional load of the contrasts between a
    segment and all other segments, as a count of minimal pairs.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    segment : str
        The target segment.
    relative_count_to_relevant_sounds : bool, optional
        If True, divide the number of minimal pairs
        by the total number of words that contain either of the two segments.
    relative_count_to_whole_corpus : bool, optional
        If True, divide the number of minimal pairs by the total number of words 
        in the corpus (regardless of whether those words contain the target sounds).
        Defaults to True.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and
        sock~shock (sock=punch) as just one minimal pair; but if True,
        you'll overcount alternative spellings of the same word, e.g.
        axel~actual and axle~actual. False is the value used by Wedel et al.
    environment_filter : EnvironmentFilter
        Allows the user to restrict the neutralization process to segments in
        particular segmental contexts
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    int or float
        If `relative_count_to_relevant_sounds`==False and `relative_count_to_whole_corpus`==False,
        returns an int of the raw number of
        minimal pairs. If `relative_count_to_relevant_sounds`==True, returns a float of
        that count divided by the total number of words in the corpus
        that include either `s1` or `s2`. If `relative_count_to_whole_corpus`==True, a
        float of the raw count divided by the total number of words in the corpus. 
    """
    all_segments = corpus_context.inventory
    segment_pairs = [(segment,other.symbol) for other in all_segments
                        if other.symbol != segment and other.symbol != '#']

    results = []
    to_output = []
    for sp in segment_pairs:
        res = minpair_fl(corpus_context, [sp],
            relative_count_to_relevant_sounds = relative_count_to_relevant_sounds,
            relative_count_to_whole_corpus = relative_count_to_whole_corpus, 
            distinguish_homophones = distinguish_homophones,
            environment_filter = environment_filter,
            prevent_normalization = prevent_normalization,
            stop_check = stop_check, call_back = call_back)
        results.append(res[0])

        if output_filename is not None:
            to_output.append((sp, res[1]))
    if output_filename is not None:
        save_minimal_pairs(output_filename, to_output)
    return sum(results)/len(segment_pairs)

def relative_deltah_fl(corpus_context, segment,
                environment_filter = None, prevent_normalization=False,
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
    all_segments = corpus_context.inventory
    segment_pairs = [(segment,other.symbol) for other in all_segments
                        if other.symbol != segment and other.symbol != '#']

    results = []
    for sp in segment_pairs:
        results.append(deltah_fl(corpus_context, [sp], prevent_normalization=prevent_normalization,
                environment_filter=environment_filter,
                stop_check = stop_check, call_back = call_back))
    return sum(results)/len(segment_pairs)


def collapse_segpairs_fl(corpus_context, **kwargs):
    func_type = kwargs.get('func_type')
    segment_pairs = kwargs.get('segment_pairs')
    relative_count = kwargs.get('relative_count')
    distinguish_homophones = kwargs.get('distinguish_homophones')
    if func_type == 'min_pairs':
        fl = minpair_fl(corpus_context, segment_pairs,
                        relative_count, distinguish_homophones,
                          environment_filter=environment_filter)
    elif func_type == 'entropy':
        fl = deltah_fl(corpus_context, segment_pairs,
          environment_filter=environment_filter)


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
                              environment_filter=environment_filter)
        elif func_type == 'entropy':
            fl = deltah_fl(corpus_context, [pair],
              environment_filter=environment_filter)
        results.append(fl)

def entropy(probabilities):
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


def neutralize_segment(segment, segment_pairs):
    for sp in segment_pairs:
        try:
            s = segment.symbol
        except AttributeError:
            s = segment
        if s in sp:
            return 'NEUTR:'+''.join(str(x) for x in sp)
    return s


# This one also now has two different "relative count" options.
def all_pairwise_fls(corpus_context, relative_fl = False,
                    algorithm = 'minpair',
                    relative_count_to_relevant_sounds = False, relative_count_to_whole_corpus = True,
                    distinguish_homophones = False,
                    environment_filter = None,
                    call_back = None, stop_check=None):
    """Calculate the functional load of the contrast between two segments as a count of minimal pairs.
    This version calculates the functional load for ALL pairs of segments in the inventory,
    which could be useful for visually mapping out phoneme inventories.

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
    relative_count_to_relevant_sounds : bool, optional
        If True, divide the number of minimal pairs by the total count
        by the total number of words that contain either of the two segments.
    relative_count_to_whole_corpus : bool, optional
        If True, divide the number of minimal pairs by the total number of words 
        in the corpus (regardless of whether those words contain the target sounds).
        Defaults to True.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and
        sock~shock (sock=punch) as just one minimal pair; but if True,
        you'll overcount alternative spellings of the same word, e.g.
        axel~actual and axle~actual. False is the value used by Wedel et al.
    environment_filter : EnvironmentFilter
        Allows the user to restrict the neutralization process to segments in
        particular segmental contexts

    Returns
    -------
    list of tuple(tuple(str, st), float)
    OR
    list of (str, float)
        Normally returns a list of all Segment pairs and their respective functional load values, as length-2 tuples ordered by FL.
        If calculating relative FL (i.e., average FL for a segment), returns a dictionary of each segment and its relative (average) FL, with entries ordered by FL.
    """
    fls = {}
    total_calculations = ((((len(corpus_context.inventory)-1)**2)-len(corpus_context.inventory)-1)/2)+1
    ct = 1
    t = time.time()
    if '' in corpus_context.inventory:
        raise Exception('Warning: Calculation of functional load for all segment pairs requires that all items in corpus have a non-null transcription.')
    
    # Count the number of words in the corpus (needed if relative_count_to_whole_corpus is True)
    num_words_in_corpus = len(corpus_context.corpus)
    
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
                            relative_count_to_relevant_sounds=relative_count_to_relevant_sounds,
                            relative_count_to_whole_corpus=relative_count_to_whole_corpus,
                            distinguish_homophones=distinguish_homophones,
                            environment_filter=environment_filter)[0]
                elif algorithm == 'deltah':
                    fl = deltah_fl(corpus_context, [(s1, s2)],
                    environment_filter=environment_filter)
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

    
    ## Filter out words that have none of the target segments
    ## (for relative_count_to_relevant_sounds as well as improving runtime)
    contain_target_segment = []
    if call_back is not None:
        call_back('Finding words with the specified segments...')
        call_back(0, len(corpus_context))
        cur = 0

    all_target_segments = list(itertools.chain.from_iterable(segment_pairs)) # creates a list of target segments from the list of tuples
    for w in corpus_context: # loops through the words in the context manager
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        tier = getattr(w, corpus_context.sequence_type)
        if any([s in tier for s in all_target_segments]):
                contain_target_segment.append(w)
    if stop_check is not None and stop_check():
        return

    ## Find minimal pairs
    minpairs = []
    if call_back is not None:
        call_back('Finding minimal pairs...')
        if len(contain_target_segment) >= 2:
            call_back(0,factorial(len(contain_target_segment))/(factorial(len(contain_target_segment)-2)*2))
        cur = 0
    for first, second in itertools.combinations(contain_target_segment, 2):
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        if is_minpair(first, second, corpus_context, segment_pairs, environment_filter):
            ordered_pair = sorted([(first, getattr(first, corpus_context.sequence_type)),
                                   (second, getattr(second, corpus_context.sequence_type))],
                                   key = lambda x: x[1]) # sort by tier/transcription
            minpairs.append(tuple(ordered_pair))

    ## Generate output 
    if not distinguish_homophones:
        actual_minpairs = {}

        for pair in minpairs:
            if stop_check is not None and stop_check():
                return
            key = (pair[0][1], pair[1][1]) # Keys are tuples of transcriptions
            if key not in actual_minpairs:
                actual_minpairs[key] = (pair[0][0], pair[1][0]) # Values are words
            else:
                pair_freq = pair[0][0].frequency + pair[1][0].frequency
                existing_freq = actual_minpairs[key][0].frequency + \
                                actual_minpairs[key][1].frequency
                if pair_freq > existing_freq:
                    actual_minpairs[key] = (pair[0][0], pair[1][0])
        result = sum((x[0].frequency + x[1].frequency)/2
                    for x in actual_minpairs.values())
    else:
        result = sum((x[0][0].frequency + x[1][0].frequency)/2 for x in minpairs)

    if relative_count_to_relevant_sounds and len(contain_target_segment) > 0:
        result /= sum(x.frequency for x in contain_target_segment)

    # added what to do if the relative count to the whole corpus is true, namely, divide by the number of words in the corpus    
    elif relative_count_to_whole_corpus:
        result = result / num_words_in_corpus
    
    return (result, minpairs)