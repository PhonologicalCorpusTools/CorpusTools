import re
from collections import defaultdict
from math import *
import itertools
import queue

import corpustools




def minpair_fl(corpus, s1=None, s2=None, feature=None, frequency_measure=None, frequency_cutoff=0, relative_count=True, distinguish_homophones=False, threaded_q=False):
    """Calculate the functional load of the contrast between two segments as a count of minimal pairs.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.
    s1 : Segment
        The first of the segments to have their functional load calculated, if using segmental neutralization.
    s2 : Segment
        The second of the segments to have their functional load calculated, if using segmental neutralization.
    feature : str
        The feature to have its functional load calculated, if using featural neutralization.
    frequency_measure : str or None, optional
        The measurement of frequency you wish to use, if using a frequency cutoff.
    frequency_cutoff : number, optional
        Minimum frequency of words to consider, if desired. Type depends on `frequency_measure`.
    relative_count : bool, optional
        If True, divide the number of minimal pairs by the total count by the total number of words that contain either of the two segments.
    distinguish_homophones : bool, optional
        If False, then you'll count sock~shock (sock=clothing) and sock~shock (sock=punch) as just one minimal pair; but if True, you'll overcount alternative spellings of the same word, e.g. axel~actual and axle~actual. False is the value used by Wedel et al.

    Returns
    -------
    int or float
        If `relative_count`==False, returns an int of the raw number of minimal pairs. If `relative_count`==True, returns a float of that count divided by the total number of words in the corpus that include either `s1` or `s2`.
     """
    if s1 and s2:
        ntype = 'seg'
    elif feature:
        ntype = 'feat'

    if threaded_q:
        q = threaded_q

    if frequency_measure != None and frequency_cutoff > 0:
        corpus = [word for word in corpus if getattr(word, frequency_measure) >= frequency_cutoff]

    if ntype == 'seg':
        corpus = [word for word in corpus if s1 in word.transcription or s2 in word.transcription]
    scope = len(corpus) # number of words with either s1 or s2

    trans_spell = [(tuple(word.transcription), word.spelling.lower()) for word in corpus]

    if ntype == 'seg':
        neutr_str = make_neutr_str(segment1=s1, segment2=s2)
        neutralized = [(' '.join([neutr_str if seg in [s1,s2] else seg for seg in word[0]]), word[1], word[0]) for word in list(trans_spell)]
    elif ntype == 'feat':
        neutralized = [(' '.join([make_neutr_str(feature=feature, fsegment=seg) for seg in word[0]]), word[1], word[0]) for word in list(trans_spell)]

    def matches(first, second):
        return (first[0] == second[0] and first[1] != second[1]
            and any(['NEUTR' in s for s in first[0]]) and any(['NEUTR' in s for s in second[0]]) and first[2] != second[2])

    for f,s in itertools.combinations(neutralized, 2):
        print(f)
        print(s)
        print(matches(f,s))

    minpairs = [(first, second) for first, second in itertools.combinations(neutralized, 2) if matches(first, second)]

    if distinguish_homophones == False:
        minpairs = list(set([tuple(sorted([mp[0][2],mp[1][2]])) for mp in minpairs]))

    # print(minpairs)
    result = len(minpairs)
    if relative_count:
        result /= scope

    if not threaded_q:
        return result
    else:
        threaded_q.put(result)
        return None

def deltah_fl(s1, s2, corpus, frequency_measure, threaded_q=False):
    """Calculate the functional load of the contrast between between two segments as the decrease in corpus entropy caused by a merger.

    Parameters
    ----------
    s1 : Segment
        The first of the segments to have their functional load calculated.
    s2 : Segment
        The second of the segments to have their functional load calculated.
    corpus : Corpus
        The domain over which functional load is calculated.
    frequency_measure : str or None, optional
        The measurement of frequency you wish to use, if using a frequency cutoff.

    Returns
    -------
    float
        The difference between a) the entropy of the choice among non-homophonous words in the corpus before a merger of `s1` and `s2` and b) the entropy of that choice after the merger.
    """

    def neutralize(word, s1, s2):
        return tuple(['NEUTR' if s in [s1,s2] else s for s in word])

    if frequency_measure == 'type':
        freq_sum = len(corpus)
    else:
        freq_sum = sum([getattr(word, frequency_measure) for word in corpus])

    original_probs = defaultdict(float)
    if frequency_measure == 'type':
        for word in corpus:
            original_probs[' '.join([str(s) for s in word.transcription])] += 1/freq_sum
    else:
        for word in corpus:
            original_probs[' '.join([str(s) for s in word.transcription])] += getattr(word, frequency_measure)/freq_sum
    preneutr_h = entropy([original_probs[item] for item in original_probs])

    neutralized_probs = defaultdict(float)
    for item in original_probs:
        neutralized_probs[neutralize(item, s1, s2)] += original_probs[item]
    postneutr_h = entropy([neutralized_probs[item] for item in neutralized_probs])

    result = preneutr_h - postneutr_h

    if not threaded_q:
        return result
    else:
        threaded_q.put(result)
        return None

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

def make_neutr_str(segment1=None, segment2=None, feature=None, fsegment=None):
    """Create a string that will replace neutralized segments.

    Parameters
    ----------
    segment1 : Segment
        The first segment to be neutralized, if using segmental neutralization.
    segment2 : Segment
        The second segment to be neutralized, if using segmental neutralization.
    feature : str
        The feature by which to neutralize fsegment, if using feature neutralization.
    fsegment : Segment
        The segment to have its `feature` neutralized, if using feature neutralization.

    Returns
    -------
    str
    """
    if segment1 and segment2:
        return 'NEUTR:{}{}'.format(segment1,segment2)
    elif feature and fsegment:
        fseg_feats = {f:fsegment.features[f] for f in fsegment.features if f != feature}
        return 'NEUTR({}):{}'.format(feature, ','.join(fseg_feats[f]+f for f in fseg_feats))
    else:
        raise ValueError('make_neutr_str requires either two segments or a feature and a target segment.')



if __name__ == '__main__':
    # TESTING
    factory = corpustools.CorpusFactory()
    c = factory.make_corpus('iphod', 'hayes', size=1000)

    # minpair_fl(c, s1='t', s2='d', relative_count = False)
    minpair_fl(c, feature='voice', relative_count = False)

    # print(deltah_fl('v', 'f', c))