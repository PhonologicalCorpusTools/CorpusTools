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
    sequence_type: string
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

    sequence_type = kwargs.get('sequence_type', 'spelling')
    count_what = kwargs.get('count_what', 'type')
    stop_check = kwargs.get('stop_check', None)
    call_back = kwargs.get('call_back', None)
    min_rel = kwargs.get('min_rel', None)
    max_rel = kwargs.get('max_rel', None)

    if algorithm == 'khorsi':
        if sequence_type == 'spelling':
            if corpus.spelling_freq_base[count_what] is None:
                corpus.spelling_freq_base[count_what] = make_freq_base(corpus,sequence_type,count_what)
            freq_base = corpus.spelling_freq_base[count_what]
        else:
            if corpus.transcription_freq_base[count_what] is None:
                corpus.transcription_freq_base[count_what] = make_freq_base(corpus,sequence_type,count_what)
            freq_base = corpus.transcription_freq_base[count_what]
        relate_func = partial(khorsi,freq_base=freq_base,
                                sequence_type = sequence_type)
    elif algorithm == 'edit_distance':
        relate_func =  partial(edit_distance, sequence_type = sequence_type)
    elif algorithm == 'phono_edit_distance':
        tier_name = kwargs.get('tier_name','transcription')
        relate_func = partial(phono_edit_distance,tier_name = tier_name, features = corpus.specifier)
    else:
        raise(StringSimilarityError('{} is not a possible string similarity algorithm.'.format(algorithm)))

    related_data = list()
    if isinstance(query,str):
        if call_back is not None:
            total = len(corpus)
            if min_rel is not None or max_rel is not None:
                total *= 2
            cur = 0
            call_back('Calculating string similarity...')
            call_back(cur,total)
        targ_word = corpus.find(query)
        relate = list()
        for word in corpus:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 50 == 0:
                    call_back(cur)
            relatedness = relate_func(targ_word, word)

            if min_rel is not None and relatedness < min_rel:
                continue
            if max_rel is not None and relatedness > max_rel:
                continue
            related_data.append( (targ_word,word,relatedness) )
        #Sort the list by most morphologically related
        related_data.sort(key=lambda t:t[-1])
        if related_data[0][1] != targ_word:
            related_data.reverse()
    elif isinstance(query, tuple):
        w1 = corpus.find(query[0])
        w2 = corpus.find(query[1])
        relatedness = relate_func(w1,w2)
        related_data.append((w1,w2,relatedness))
    elif hasattr(query,'__iter__'):
        if call_back is not None:
            total = len(query)
            cur = 0
            call_back('Calculating string similarity...')
            if total:
                call_back(cur,total)
        for q1,q2 in query:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 50 == 0:
                    call_back(cur)
            w1 = corpus.find(q1)
            w2 = corpus.find(q2)
            relatedness = relate_func(w1,w2)
            if min_rel is not None and relatedness < min_rel:
                continue
            if max_rel is not None and relatedness > max_rel:
                continue
            related_data.append( (w1,w2,relatedness) )

    return related_data



