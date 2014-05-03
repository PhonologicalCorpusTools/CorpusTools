import re
from collections import defaultdict
from math import *
import itertools
import queue

import corpustools




def minpair_fl(s1, s2, corpus, frequency_measure=None, frequency_cutoff=0, relative_count=True, distinguish_homophones=False, threaded_q=False):
    """Given a pair of Segments, calculate the functional load of the contrast between them as a count of minimal pairs.

    `s1` and `s2` : Segment
    `corpus` : Corpus
    `frequency_measure` : The measurement of frequency you wish to use, if using a frequency cutoff
    `frequency_cutoff` : Minimum frequency of words to consider, if desired
    `relative_count` : If True, divide the number of minimal pairs by the total count by the total number of words that contain either of the two segments.
    `distinguish_homophones` : False is the value used by Wedel et al. If False, then you'll count sock~shock (sock=clothing) and sock~shock (sock=punch) as just one minimal pair; but if True, you'll overcount alternative spellings of the same word, e.g. axel~actual and axle~actual.
     """
    if threaded_q:
        q = threaded_q

    if frequency_measure != None and frequency_cutoff > 0:
        corpus = [word for word in corpus if getattr(word, frequency_measure) >= frequency_cutoff]

    corpus = [word for word in corpus if s1 in word.transcription or s2 in word.transcription]
    scope = len(corpus) # number of words with either s1 or s2

    trans_spell = set([(' '.join([str(segment) for segment in word.transcription]), word.spelling.lower()) for word in corpus])
    neutralized = [(re.sub('('+s1+'|'+s2+')', 'NEUTR', word[0]), word[1], word[0]) for word in list(trans_spell)]

    def matches(first, second):
        return (first[0] == second[0] and first[1] != second[1]
            and 'NEUTR' in first[0] and 'NEUTR' in second[0] and first[2] != second[2])

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

def deltah_fl(s1, s2, corpus, frequency_measure):
    """Given a pair of segments, calculate the functional load of the contrast between them as the decrease in corpus entropy caused by a merger.

    `s1` and `s2` : Segment
    `corpus` : Corpus
    `frequency_measure` : The measurement of frequency you wish to use
    """
    def neutralize(word, s1, s2):
        return tuple(['NEUTR' if s in [s1,s2] else s for s in word])

    freq_sum = sum([getattr(word, frequency_measure) for word in corpus])

    original_probs = defaultdict(float)
    for word in corpus:
        original_probs[' '.join([str(s) for s in word.transcription])] += getattr(word, frequency_measure)/freq_sum
    preneutr_h = entropy([original_probs[item] for item in original_probs])

    neutralized_probs = defaultdict(float)
    for item in original_probs:
        neutralized_probs[neutralize(item, s1, s2)] += original_probs[item]
    postneutr_h = entropy([neutralized_probs[item] for item in neutralized_probs])

    return preneutr_h - postneutr_h


def entropy(probabilities):
    """Let's take this function from elsewhere if possible.
    """
    return -(sum([p*log(p,2) if p > 0 else 0 for p in probabilities]))



if __name__ == '__main__':
    # TESTING
    factory = corpustools.CorpusFactory()
    c = factory.make_corpus('iphod', 'hayes', size=50000)

    print(minpair_fl('v', 'f', c, relative_count = False, frequency_measure='freq_per_mil', frequency_cutoff=2))
    print(deltah_fl('v', 'f', c, frequency_measure='freq_per_mil'))