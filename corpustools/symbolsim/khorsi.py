import math
import collections
import re
import time
from codecs import open

import corpustools

def lcs(x1, x2):
    """Returns the longest common sequence of two strings or lists of transcription characters and the remainder elements not in the longest common sequence

    Parameters
    ----------
    x1: list
        List of strings
    x2: list
        List of strings

    Returns
    -------
    list
        the list of the longest common sequence of two lists
    list
        the list of remaining elements of both x1 and x2 that are not in the longest common sequence
    """
    if len(x1) >= len(x2):
        longer = x1
        shorter = x2
    else:
        longer = x2
        shorter = x1

    stringMatches = []
    largestMatch = None
    for i in range(len(shorter),0,-1):
        #Get all possible substrings of word x1
        shorter_strings = substring_set(shorter, i)
        longer_strings = substring_set(longer, i)

        s = shorter_strings & longer_strings

        if len(s):
            break
    else:
        return [], longer+shorter

    leftover = []
    for i in range(len(shorter)):

        begin = i
        for lcs in s:
            lcs = lcs.split('.') #back to list
            end = i+len(lcs)
            if shorter[begin:end] == lcs:
                break
        else:
            lcs = None
        if lcs is not None:
            break
    leftover.extend(shorter[:begin])
    leftover.extend(shorter[end:])
    for i in range(len(longer)):
        begin = i
        end = i+len(lcs)
        if longer[begin:end] == lcs:
            break
    leftover.extend(longer[:begin])
    leftover.extend(longer[end:])
    return lcs,leftover

def substring_set(w, l):
    """Returns all substrings of a word w of length l

    Parameters
    ----------
    w: string
        a string representing a word (e.g. 'pressure')
    l: int
        a integer of a certain length

    Returns
    -------
    list
        A list of strings where each string is a properly ordered subset of w (i.e. if w='pressure', l='2', returns [pr, re, es ..., re])
    """
    #return all unique substrings of a word w of length l from 1 letter to the entire word
    substrings = set([])
    for i in range(len(w)):
        sub = w[i:(i+l)]
        if len(sub) < l:
            continue
        substrings.update(['.'.join(sub)])
    return substrings

def khorsi(word1, word2, freq_base, string_type):
    """Calculate the string similarity of two words given a set of characters and their frequencies in a corpus, Returns the value (implementation of Khorsi (2012))

    Parameters
    ----------
    w1: Word
        Word object
    w2: Word
        Word object
    freq_base: dictionary
        a dictionary where each segment is mapped to its frequency of occurrence in a corpus
    string_type: string
        The type of segments to be used ('spelling' = Roman letters, 'transcription' = IPA symbols)

    Returns
    -------
    int
        A number representing the relatedness of two words based on Khorsi (2012)
    """
    w1 = getattr(word1, string_type)
    w2 = getattr(word2, string_type)

    if string_type == 'spelling':
        w1 = list(w1)
        w2 = list(w2)
    else:
        w1 = [x.symbol for x in w1]
        w2 = [x.symbol for x in w2]

    longest, left_over = lcs(w1, w2)

    #Khorsi's algorithm
    lcs_sum = sum(math.log(1/(freq_base[x]/freq_base['total'])) for x in longest)
    leftover_sum = sum(math.log(1/(freq_base[x]/freq_base['total'])) for x in left_over)

    return lcs_sum-leftover_sum

def make_freq_base(corpus, string_type, count_what = 'type'):
    """Returns a dictionary of segments mapped to their frequency of occurrence in a corpus

    Parameters
    ---------
    string_type: string
        The type of segments to be used ('spelling' = Roman letters, 'transcription' = IPA symbols)
    count_what: string
        The type of frequency, either 'type' or 'token', defaults to 'type'

    Returns
    -------
    dictionary
        A dictionary where a segments maps to its frequency of occurrence in a corpus
    """
    freq_base = collections.defaultdict(int)

    for word in corpus:
        if count_what == 'token':
            freq = word.get_frequency()
        else:
            freq = 1

        for x in getattr(word, string_type):
            freq_base[str(x)] += freq
    freq_base['total'] = sum(value for value in freq_base.values())
    return freq_base

