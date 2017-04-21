from math import log2
from collections import defaultdict

#for testing purposes
import os
import pickle
with open("lemurian.corpus", 'rb') as file:
    corpus = pickle.load(file)



def context(index, word, context_type="all"):
    """
    :param index: integer indicating index of segment
    :param word: str
    :return: str of all preceding segments in the word
    Based on method described in van Son & Pols (2003), and used by Cohen Priva (2015).
    """
    if context_type=="all":
        return tuple(word.transcription[0:index-1])


def segment_in_context_frequencies(segment, corpus_context, context_type="all"):
    """
    :param segment: str
    :param corpus_context:
    :return: dict with {segment : segment|context frequency,...}
    """
    contexts = defaultdict(int)
    for word in corpus_context:
        i = 0
        for seg in word.transcription:
            i += 1
            if seg == segment:
                contexts[context(i, word, context_type)] += corpus_context[word.spelling]
    return contexts


def context_frequencies(contexts, corpus_context):
    """
    :param contexts:
    :param corpus_context:
    :return:
    """
    context_frs = defaultdict(int)
    for c in contexts:
        for word in corpus_context:
            if word.startswith(c):
                context_frs[c] += corpus_context[word]
    return context_frs


def conditional_probability(segment_frs, context_frs):
    """
    :param segment_frs: dict with {segment : segment|context frequency,...}
    :param context_frs: dict with {segment : context|segment frequency,...}
    :return: dict with: {context:  conditional probability, } for 1 segment
    """
    conditional_probs=defaultdict(float)
    for c in segment_frs:
        conditional_probs[c]= round(segment_frs[c]/context_frs[c],3)
    return conditional_probs


def get_informativity(corpus_context, segment, context_type="all",precision=3):
    """
    :param corpus_context:
    :param segment: str specifying the segment to get informativity of
    :param context_method: currently only support for "all", but is placeholder for how to specify context
    :param precision: int to specify rounding
    :return: dict with summary of parameters and float informativity
    """
    s_frs= segment_in_context_frequencies(segment,corpus_context,context_type)
    c_frs= context_frequencies(s_frs, corpus_context)
    c_prs= conditional_probability(s_frs, c_frs)
    informativity=round(-(sum([(s_frs[c])*log2(c_prs[c]) for c in c_prs]))/sum([(s_frs[s]) for s in s_frs]),precision)
    summary={
        "Corpus": corpus_context,
        "Segment": segment,
        "Context": context_type,
        "Precision (rounding)": precision,
        "Informativity": informativity
    }
    return summary


def all_informativity(corpus,context_type="all",precision=3):
    """
    :param corpus:
    :param context_type: currently only "all"
    :param precision: int defaults to 3
    :return:
    """
    all_informativities = defaultdict(dict)
    for segment in corpus.inventory:
        get_informativity(corpus, segment,context_type,precision)
    return all_informativities

#print(corpus.wordlist)
get_informativity(corpus, "s")
