#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Scott
#
# Created:     12/01/2015
# Copyright:   (c) Scott 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from corpustools.corpus.classes import Corpus
from corpustools.corpus.io import load_binary
import argparse
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

def KullbackLeibler(corpus, seg1, seg2, side, outfile=None, stop_check=False, call_back=False):
    """
    Calculates KL distances between two Phoneme objects in some context,
    either the left or right-hand side.
    Segments with identical distributions (ie. seg1==seg2) have a KL of zero.
    Segments with similar distributions therefore have low numbers, so *high*
    numbers indicate possible allophones.

    Parameters
    ----------
    corpus : Corpus
        Corpus to use
    seg1 : str
        First segment
    seg2 : str
        Second segment
    outfile : str
        Full path to save output
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function
    """
    if not seg1 in corpus.inventory or not seg2 in corpus.inventory:
        raise ValueError('One segment does not exist in this corpus')

    allC = defaultdict(Context)
    seg_counts = {'seg1':0, 'seg2':0}
    for word in corpus.iter_words():
        for pos,seg in word.enumerate_symbols('transcription'):
            thisc = word.get_env(pos,'transcription')
            if side.startswith('r'):
                thisc = thisc.rhs
            elif side.startswith('l'):
                thisc = thisc.lhs

            flag = False
            if seg1 == seg:
                allC[thisc].seg1 += 1
                seg_counts['seg1'] += 1
                flag = True

            if seg2 == seg:
                allC[thisc].seg2 += 1
                seg_counts['seg2'] += 1
                flag = True

            if not flag:
                allC[thisc].other += 1

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

    # seg1_features = corpus.segment_to_features(seg1)
    # seg2_features = corpus.segment_to_features(seg2)
    # feature_difference = sum([1 for feature in seg1_features.keys() if not seg1_features[f] == seg2_features[f]])

    if outfile is not None:
        if not os.path.isfile(outfile):
            outfile = os.path.join(os.getcwd(), outfile)
        if not outfile.endswith('.txt'):
            outfile += '.txt'

        with open(outfile, mode='w', encoding='utf-8') as f:
            print('Context, Context frequency, {} frequency in context, {} frequency in context\n\r'.format(seg1,seg2), file=f)
            for context,result in allC.items():
                cfrequency = freq_c[context]/totalC
                print('{},{},{},{}\n\r'.format(context,
                                cfrequency,
                                result.seg1/result.sum(),
                                result.seg2/result.sum()),
                        file=f)
        #print('Done!')

    #else:
    #    print(KL, seg1_entropy, seg2_entropy, ur, sr)

    is_spurious = check_spurious(ur, sr, corpus)

    if side.startswith('r'):
        retside = 'right'
    elif side.startswith('l'):
        retside = 'left'
    elif side.startswith('b'):
        retside = 'both'
    return seg1, seg2, retside, seg1_entropy, seg2_entropy, KL, ur, is_spurious


def check_spurious(ur, sr, corpus):
    #returns a string, not a bool, for printing to a results table
    ur = corpus.segment_to_features(ur).features
    sr = corpus.segment_to_features(sr).features
    diff = lambda flist1,flist2: len([f1 for f1,f2 in zip(sorted(flist1.values()),
                                                          sorted(flist2.values()))
                                      if not f1==f2])

    seg_diff = diff(ur, sr)
    if seg_diff == 1:
        return 'No' #minimally different, could be allophones

    for seg in corpus.inventory:
        if diff(seg.features, ur) < seg_diff:
            return 'Yes' #something else is more similar

    return 'Maybe' #nothing else is more similar
