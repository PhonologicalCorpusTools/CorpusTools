from math import log
from collections import defaultdict
import os
from codecs import open

from corpustools.exceptions import KLError

class Context(object):

    def __init__(self):
        self.seg1 = 0
        self.seg2 = 0
        self.other = 0

    def sum(self):
        return sum([self.seg1,self.seg2,self.other])

    def __repr__(self):
        return str((self.seg1, self.seg2, self.other))

def KullbackLeibler(corpus_context, seg1, seg2, side, outfile = None,
                        stop_check = False, call_back = False):
    """
    Calculates KL distances between two Phoneme objects in some context,
    either the left or right-hand side.
    Segments with identical distributions (ie. seg1==seg2) have a KL of zero.
    Segments with similar distributions therefore have low numbers, so *high*
    numbers indicate possible allophones.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    seg1 : str
        First segment
    seg2 : str
        Second segment
    side : str
        One of 'right', 'left' or 'both'
    outfile : str
        Full path to save output
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function
    """
    ## FIXME:  This function should be refactored into in KL proper and
    ## another function that determines underlying form type things

    if isinstance(seg1, tuple):
        for x in seg1:
            if x not in corpus_context.inventory:
                raise ValueError('Segment \'{}\' does not exist in this corpus.'.format(x))
    else:
        if not seg1 in corpus_context.inventory or not seg2 in corpus_context.inventory:
            raise ValueError('Segment \'{}\' does not exist in this corpus.'.format(seg1))
        seg1 = [seg1]

    if isinstance(seg2, tuple):
        for x in seg2:
            if x not in corpus_context.inventory:
                raise ValueError('Segment \'{}\' does not exist in this corpus.'.format(x))
    else:
        if not seg2 in corpus_context.inventory:
            raise ValueError('Segment \'{}\' does not exist in this corpus.'.format(seg2))
        seg2 = [seg2]

    allC = defaultdict(Context)
    seg_counts = {'seg1':0, 'seg2':0}


    for word in corpus_context:
        tier = getattr(word, corpus_context.sequence_type)
        symbols = tier.with_word_boundaries()
        for pos in range(1, len(symbols)-1):
            seg = symbols[pos]
            thisc = (symbols[pos-1],symbols[pos+1])
            if side.startswith('r'):
                thisc = thisc[0]
            elif side.startswith('l'):
                thisc = thisc[1]

            flag = False
            if seg in seg1:
                allC[thisc].seg1 += word.frequency
                seg_counts['seg1'] += word.frequency
                flag = True

            if seg in seg2:
                allC[thisc].seg2 += word.frequency
                seg_counts['seg2'] += word.frequency
                flag = True

            if not flag:
                allC[thisc].other += word.frequency

    totalC = len(allC)
    freq_c = defaultdict(int)
    for c in allC:
        freq_c[c] += 1

    P = lambda c,s: (getattr(c,s)+1)/(seg_counts[s]+totalC)

    KL = sum(
    [(P(c,'seg1')*log(P(c,'seg1')/P(c,'seg2')))
    +(P(c,'seg2')*log(P(c,'seg2')/P(c,'seg1')))
    for c in allC.values()])

    seg1_entropy = sum(P(result,'seg1')*log(
                                        P(result,'seg1')/(freq_c[context]/totalC))
                        for (context,result) in allC.items())

    seg2_entropy = sum(P(result,'seg2')*log(
                                        P(result,'seg2')/(freq_c[context]/totalC))
                        for (context,result) in allC.items())

    ur,sr = (seg1,seg2) if seg1_entropy < seg2_entropy else (seg2,seg1)

    if outfile is not None:
        if not outfile.endswith('.txt'):
            outfile += '.txt'

        with open(outfile, mode='w', encoding='utf-8-sig') as f:
            print('Context, Context frequency, {} frequency in context, {} frequency in context\n\r'.format(seg1,seg2), file=f)
            for context,result in allC.items():
                cfrequency = freq_c[context]/totalC
                print('{},{},{},{}\n\r'.format(context,
                                cfrequency,
                                result.seg1/result.sum(),
                                result.seg2/result.sum()),
                        file=f)

    is_spurious = _check_spurious(ur, sr, corpus_context)

    if side.startswith('r'):
        retside = 'right'
    elif side.startswith('l'):
        retside = 'left'
    elif side.startswith('b'):
        retside = 'both'
    return seg1_entropy, seg2_entropy, KL, ur, is_spurious


def _check_spurious(ur, sr, corpus_context):
    if len(ur) > 1: #Set of segments, probably supplied from GUI, hack until refactor
        return 'No'
    #returns a string, not a bool, for printing to a results table
    if corpus_context.specifier is None:
        return 'Maybe'
    ur = corpus_context.corpus.segment_to_features(ur[0])#.features
    sr = corpus_context.corpus.segment_to_features(sr[0])#.features
    diff = lambda flist1,flist2: len([f1 for f1,f2 in zip(sorted(flist1.values()),
                                                          sorted(flist2.values()))
                                      if not f1==f2])

    seg_diff = diff(ur, sr)
    if seg_diff == 1:
        return 'No' #minimally different, could be allophones

    for seg in corpus_context.inventory:
        if diff(seg.features, ur) < seg_diff:
            return 'Yes' #something else is more similar

    return 'Maybe' #nothing else is more similar
