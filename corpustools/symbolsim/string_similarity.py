'''
Created on May 12, 2014

@author: Michael
'''
from functools import partial

from corpustools.symbolsim.khorsi import make_freq_base, khorsi
from corpustools.symbolsim.edit_distance import edit_distance
from corpustools.symbolsim.phono_edit_distance import phono_edit_distance


class StringSimilarityError(Exception):
    pass

def string_similarity(corpus, query, algorithm, **kwargs):
    """
    This function computes similarity of pairs of words across a corpus.

    Parameters
    ----------
    corpus: Corpus
        The corpus object to use
    query: string, tuple, or list of tuples
        If this is a string, every word in the corpus will be compared to it,
        if this is a tuple with two strings, those words will be compared to each other,
        if this is a list of tuples, each tuple's strings will be compared to each other.
    algorithm: string
        The algorithm of string similarity to be used, currently supports
        'khorsi', 'edit_distance', and 'phono_edit_distance'
    string_type: string
        Specifies whether to use 'spelling', 'transcription' or the name of a
        transcription tier to use for comparisons
    count_what: string
        The type of frequency to use, either 'type' or 'token'
    max_rel: double
        Filters out all words that are higher than max_rel from a relatedness measure
    min_rel: double
        Filters out all words that are lower than min_rel from a relatedness measure

    Returns
    -------
    list of tuples:
        The first two elements of the tuple are the words that were compared
        and the final element is their relatedness score
    """

    string_type = kwargs.get('string_type','spelling')
    count_what = kwargs.get('count_what','type')
    if algorithm == 'khorsi':
        freq_base = make_freq_base(corpus,string_type,count_what)
        relate_func = partial(khorsi,freq_base=freq_base,
                                string_type = string_type)
    elif algorithm == 'edit_distance':
        relate_func =  partial(edit_distance, string_type = string_type)
    elif algorithm == 'phono_edit_distance':
        tier_name = kwargs.get('tier_name','transcription')
        relate_func = partial(phono_edit_distance,tier_name = tier_name, features = corpus.specifier)
    else:
        raise(StringSimilarityError('{} is not a possible string similarity algorithm.'.format(algorithm)))

    related_data = list()
    if isinstance(query,str):
        targ_word = corpus.find(query)
        relate = list()
        for word in corpus:
            relatedness = relate_func(targ_word, word)
            related_data.append( (targ_word,word,relatedness) )
        #Sort the list by most morphologically related
        related_data.sort(key=lambda t:t[-1])
        if related_data[0][1] != targ_word:
            related_data.reverse()
    elif isinstance(query, list):
        for q1,q2 in query:
            w1 = corpus.find(q1)
            w2 = corpus.find(q2)
            relatedness = relate_func(w1,w2)
            related_data.append( (w1,w2,relatedness) )
    elif isinstance(query, tuple):
        w1 = corpus.find(query[0])
        w2 = corpus.find(query[1])
        relatedness = relate_func(w1,w2)
        related_data.append((w1,w2,relatedness))

    min_rel = kwargs.get('min_rel', None)
    max_rel = kwargs.get('max_rel', None)

    filtered_data = list()
    for w1, w2, score in related_data:
        if score == None: #A relatedness score is unavailable
            continue
        elif min_rel != None:
            if max_rel != None:
                if min_rel <= score <= max_rel:
                    filtered_data.append( (w1, w2, score) )
            elif min_rel <= score:
                filtered_data.append( (w1, w2, score) )
        elif max_rel != None and score <= max_rel:
            filtered_data.append( (w1, w2, score) )
        else:
            filtered_data.append( (w1, w2, score) )

    return filtered_data


