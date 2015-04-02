'''
Created on May 12, 2014

@author: Michael
'''
from functools import partial
from math import factorial
from corpustools.corpus.classes import Word
from corpustools.symbolsim.khorsi import khorsi
from corpustools.symbolsim.edit_distance import edit_distance
from corpustools.symbolsim.phono_edit_distance import phono_edit_distance

from corpustools.multiprocessing import score_mp, PCTMultiprocessingError

from corpustools.exceptions import StringSimilarityError

def string_sim_key(algorithm, sequence_type, count_what):
    if algorithm == 'khorsi':
        return 'string_sim_{}_{}_{}'.format(algorithm, sequence_type, count_what)
    else:
        return 'string_sim_{}_{}'.format(algorithm, sequence_type)

def khorsi_wrapper(w1, w2, freq_base,
                                sequence_type, max_distance):
    score = khorsi(w1, w2, freq_base = freq_base, sequence_type = sequence_type)
    if score >= max_distance:
        return score
    else:
        return None

def edit_distance_wrapper(w1, w2, sequence_type, max_distance):
    score = edit_distance(w1, w2, sequence_type)
    if score <= max_distance:
        return score
    else:
        return None

def phono_edit_distance_wrapper(w1, w2, sequence_type, features, max_distance):
    score = phono_edit_distance(w1, w2, sequence_type = sequence_type,features = features)
    if score <= max_distance:
        return score
    else:
        return None

def optimize_string_similarity(corpus, algorithm, sequence_type, count_what, num_cores = -1,
                            max_distance = 10,
                            call_back = None, stop_check = None):
    return
    if num_cores == -1:
        raise(PCTMultiprocessingError("This function requires multiprocessing."))
    if call_back is not None:
        call_back('Generating neighborhood density graph...')
        num_comps = factorial(len(corpus))/(factorial(len(corpus)-2)*2)
        call_back(0,num_comps/500)
    detail_key = string_sim_key(algorithm, sequence_type, count_what)

    keys = list(corpus.keys())
    iterable = ((corpus.wordlist[keys[i]],corpus.wordlist[keys[j]])
                    for i in range(len(keys)) for j in range(i+1,len(keys)))

    if algorithm == 'khorsi':
        freq_base = corpus.get_frequency_base(sequence_type, count_what)
        function = partial(khorsi_wrapper,freq_base=freq_base,
                                sequence_type = sequence_type,
                                max_distance = max_distance)
    elif algorithm == 'edit_distance':
        function =  partial(edit_distance_wrapper, sequence_type = sequence_type,
                                            max_distance = max_distance)
    elif algorithm == 'phono_edit_distance':
        function = partial(phono_edit_distance_wrapper,sequence_type = sequence_type,
                                                        features = corpus.specifier,
                                                        max_distance = max_distance)

    edges = score_mp(iterable, function, num_cores, call_back, stop_check)
    for e in edges:
        corpus._graph.add_edge(corpus.key(e[0]), corpus.key(e[1]),key = detail_key, weight = e[2])
    if detail_key not in corpus._graph.graph['symbolsim']:
        corpus._graph.graph['symbolsim'].append(detail_key)

def string_similarity(corpus, query, algorithm, **kwargs):
    """
    This function computes similarity of pairs of words across a corpus.

    Parameters
    ----------
    corpus: Corpus
        The corpus object to use

    query: string, tuple, or list of tuples
        If this is a string, every word in the corpus will be compared to it,
        if this is a tuple with two strings, those words will be compared to
        each other,
        if this is a list of tuples, each tuple's strings will be compared to
        each other.

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
        freq_base = corpus.get_frequency_base(sequence_type, count_what)
        try:
            bound_count = freq_base['#']
            freq_base = {k:v for k,v in freq_base.items() if k != '#'}
            freq_base['total'] -= bound_count
        except KeyError:
            pass
        relate_func = partial(khorsi,freq_base=freq_base,
                                sequence_type = sequence_type)
    elif algorithm == 'edit_distance':
        relate_func =  partial(edit_distance, sequence_type = sequence_type)
    elif algorithm == 'phono_edit_distance':
        relate_func = partial(phono_edit_distance,sequence_type = sequence_type, features = corpus.specifier)
    else:
        raise(StringSimilarityError('{} is not a possible string similarity algorithm.'.format(algorithm)))

    related_data = list()
    if isinstance(query,Word):
        if call_back is not None:
            total = len(corpus)
            if min_rel is not None or max_rel is not None:
                total *= 2
            cur = 0
            call_back('Calculating string similarity...')
            call_back(cur,total)
        targ_word = query
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
        w1 = query[0]
        w2 = query[1]
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
            w1 = q1
            w2 = q2
            relatedness = relate_func(w1,w2)
            if min_rel is not None and relatedness < min_rel:
                continue
            if max_rel is not None and relatedness > max_rel:
                continue
            related_data.append( (w1,w2,relatedness) )

    return related_data


def ensure_query_is_word(query, corpus, sequence_type, segment_delimiter):
    if isinstance(query, Word):
        query_word = query
    else:
        try:
            query_word = corpus.find(query)
        except KeyError:
            if segment_delimiter == None:
                query_word = Word(**{sequence_type: list(query)})
            else:
                query_word = Word(**{sequence_type: query.split(segment_delimiter)})
    return query_word
