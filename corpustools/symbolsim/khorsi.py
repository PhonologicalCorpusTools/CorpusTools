
from collections import defaultdict
from math import log

def lcs(x1, x2):
    """Returns the longest common sequence of two lists of characters
    and the remainder elements not in the longest common sequence

    Parameters
    ----------
    x1: list
        List of characters

    x2: list
        List of characters

    Returns
    -------
    list
        the list of the longest common sequence of two lists

    list
        the list of remaining elements of both x1 and x2 that are not in
        the longest common sequence
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
    if lcs is None:
        lcs = []
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
    w: list
        List of characters representing a word

    l: int
        Length of substrings to generate

    Returns
    -------
    set
        A set of substrings of the specified length
    """
    #return all unique substrings of a word w of length l from 1 letter to the entire word
    substrings = set([])
    for i in range(len(w)):
        sub = w[i:(i+l)]
        if len(sub) < l:
            continue
        substrings.update(['.'.join(sub)])
    return substrings

def khorsi(word1, word2, freq_base, sequence_type, max_distance = None):
    """Calculate the string similarity of two words given a set of
    characters and their frequencies in a corpus based on Khorsi (2012)

    Parameters
    ----------
    word1: Word
        First Word object to compare

    word2: Word
        Second Word object to compare

    freq_base: dictionary
        a dictionary where each segment is mapped to its frequency of
        occurrence in a corpus

    sequence_type: string
        The type of segments to be used ('spelling' = Roman letters,
        'transcription' = IPA symbols)

    Returns
    -------
    float
        A number representing the relatedness of two words based on Khorsi (2012)
    """
    w1 = word1
    w2 = word2
    if sequence_type == 'spelling':
        w1 = list(w1)
        w2 = list(w2)
    longest, left_over = lcs(w1, w2)
    #print(w1,w2)
    #print(longest,left_over)

    #Khorsi's algorithm
    #print([(freq_base[x]/freq_base['total']) for x in longest])
    khorsi_sum = 0
    for x in longest:
        khorsi_sum += log(1/(freq_base[x]/freq_base['total']))
    for x in left_over:
        khorsi_sum -= log(1/(freq_base[x]/freq_base['total']))
        if max_distance is not None and khorsi_sum < max_distance:
            break
    return khorsi_sum

