from functools import partial
from corpustools.corpus.classes import Word
from corpustools.symbolsim.khorsi import khorsi
from corpustools.symbolsim.edit_distance import edit_distance
from corpustools.symbolsim.phono_edit_distance import phono_edit_distance

from corpustools.exceptions import StringSimilarityError

def khorsi_wrapper(w1, w2, freq_base,sequence_type, max_distance):
    score = khorsi(getattr(w1, sequence_type), getattr(w2, sequence_type),
                   freq_base=freq_base, sequence_type=sequence_type)
    if score >= max_distance:
        return score
    else:
        return None

def edit_distance_wrapper(w1, w2, sequence_type, max_distance):
    score = edit_distance(getattr(w1, sequence_type), getattr(w2, sequence_type), sequence_type)
    if score <= max_distance:
        return score
    else:
        return None

def phono_edit_distance_wrapper(w1, w2, sequence_type, features, max_distance):
    score = phono_edit_distance(getattr(w1, sequence_type), getattr(w2, sequence_type),
                                sequence_type=sequence_type, features=features)
    if score <= max_distance:
        return score
    else:
        return None

def string_similarity(corpus_context, query, algorithm, **kwargs):
    """
    This function computes similarity of pairs of words across a corpus.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    query: string, tuple, or list of tuples
        If this is a string, every word in the corpus will be compared to it,
        if this is a tuple with two strings, those words will be compared to
        each other,
        if this is a list of tuples, each tuple's strings will be compared to
        each other.
    algorithm: string
        The algorithm of string similarity to be used, currently supports
        'khorsi', 'edit_distance', and 'phono_edit_distance'
    max_rel: double
        Filters out all words that are higher than max_rel from a relatedness measure
    min_rel: double
        Filters out all words that are lower than min_rel from a relatedness measure
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    list of tuples:
        The first two elements of the tuple are the words that were compared
        and the final element is their relatedness score
    """
    stop_check = kwargs.get('stop_check', None)
    call_back = kwargs.get('call_back', None)
    min_rel = kwargs.get('min_rel', None)
    max_rel = kwargs.get('max_rel', None)

    if algorithm == 'khorsi':
        freq_base = corpus_context.get_frequency_base()
        try:
            bound_count = freq_base['#']
            freq_base = {k:v for k,v in freq_base.items() if k != '#'}
            freq_base['total'] -= bound_count
        except KeyError:
            pass
        relate_func = partial(khorsi, freq_base=freq_base,
                                sequence_type = corpus_context.sequence_type)
    elif algorithm == 'edit_distance':
        relate_func =  partial(edit_distance,
                                sequence_type = corpus_context.sequence_type)
    elif algorithm == 'phono_edit_distance':
        relate_func = partial(phono_edit_distance,
                                sequence_type = corpus_context.sequence_type,
                                features = corpus_context.specifier)
    else:
        raise(StringSimilarityError('{} is not a possible string similarity algorithm.'.format(algorithm)))

    related_data = []
    if isinstance(query, Word):       # 'comparison type' option set to "compare one word to entire corpus"
        if call_back is not None:
            total = len(corpus_context)
            if min_rel is not None or max_rel is not None:
                total *= 2
            cur = 0
            call_back('Calculating string similarity...')
            call_back(cur,total)
        targ_word = query
        relate = list()
        for word in corpus_context:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 50 == 0:
                    call_back(cur)
            w1 = getattr(targ_word, corpus_context.sequence_type)
            w2 = getattr(word, corpus_context.sequence_type)
            relatedness = relate_func(w1, w2)

            if min_rel is not None and relatedness < min_rel:
                continue
            if max_rel is not None and relatedness > max_rel:
                continue
            related_data.append( (targ_word,word,relatedness) )
        #Sort the list by most morphologically related
        related_data.sort(key=lambda t:t[-1])
        if related_data[0][1] != targ_word:
            related_data.reverse()
    elif isinstance(query, tuple):      # 'comparison type' option set to "Compare a single pair of words to each other"
        word1 = query[0]
        word2 = query[1]

        w1 = getattr(word1, corpus_context.sequence_type)
        w2 = getattr(word2, corpus_context.sequence_type)
        relatedness = relate_func(w1,w2)

        related_data.append((word1,word2,relatedness))
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
            try:
                w1 = getattr(q1,corpus_context.sequence_type)
                w2 = getattr(q2,corpus_context.sequence_type)
                relatedness = relate_func(w1,w2)
                if min_rel is not None and relatedness < min_rel:
                    continue
                if max_rel is not None and relatedness > max_rel:
                    continue
            except:
                relatedness = "N/A"

            related_data.append((q1, q2, relatedness))

    return related_data

