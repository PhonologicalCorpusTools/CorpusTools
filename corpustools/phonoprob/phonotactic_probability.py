# -*- coding: utf-8 -*-

from corpustools.corpus.classes import Word

from corpustools.exceptions import PhonoProbError

from corpustools.contextmanagers import ensure_context

def phonotactic_probability_all_words(corpus_context, algorithm,
                                    probability_type = 'unigram',
                                    num_cores = -1,
                                    stop_check = None, call_back = None):
    """Calculate the phonotactic_probability of all words in the corpus and
    adds them as attributes of the words.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    algorithm : str
        Algorithm to use for calculating phonotactic probability (currently
        only 'vitevitch')
    probability_type : str
        Either 'unigram' or 'bigram' probability
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function
    """
    ensure_context(corpus_context)
    if call_back is not None:
        call_back('Calculating phonotactic probabilities...')
        call_back(0,len(corpus_context))
        cur = 0
    num_cores = -1 # Multiprocessing not yet implemented
    if num_cores == -1:
        for w in corpus_context:
            if stop_check is not None and stop_check():
                break
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            if algorithm == 'vitevitch':
                res = phonotactic_probability_vitevitch(corpus_context, w,
                                        probability_type = probability_type,
                                        stop_check = stop_check)
                setattr(w.original, corpus_context.attribute.name,res)
    if stop_check is not None and stop_check():
        corpus_context.corpus.remove_attribute(corpus_context.attribute)

def phonotactic_probability(corpus_context, query, algorithm,
                                    probability_type = 'unigram',
                                    stop_check = None, call_back = None):
    """Calculate the phonotactic_probability of a particular word.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    query : Word
        The word whose neighborhood density to calculate.
    algorithm : str
        Algorithm to use for calculating phonotactic probability (currently
        only 'vitevitch')
    probability_type : str
        Either 'unigram' or 'bigram' probability
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    float
        Phonotactic probability of the word
    """
    if algorithm == 'vitevitch':
        return phonotactic_probability_vitevitch(corpus_context, query,
                                    probability_type,
                                    stop_check, call_back)

def phonotactic_probability_vitevitch(corpus_context, query,
                                    probability_type = 'unigram',
                                    stop_check = None, call_back = None):
    """Calculate the phonotactic_probability of a particular word using
    the Vitevitch & Luce algorithm

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    query : Word
        The word whose neighborhood density to calculate.
    probability_type : str
        Either 'unigram' or 'bigram' probability
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    float
        Phonotactic probability of the word
    """
    ensure_context(corpus_context)

    if probability_type == 'unigram':
        gramsize = 1
    elif probability_type == 'bigram':
        gramsize = 2

    prob_dict = corpus_context.get_phone_probs(gramsize = gramsize)
    sequence = zip(*[getattr(query, corpus_context.sequence_type)[i:] for i in range(gramsize)])

    totprob = 0
    tot = 0
    for i,s in enumerate(sequence):
        try:
            totprob += prob_dict[s,i]
        except KeyError:
            notfound = []

            for seg in s:
                if seg not in corpus_context.inventory:
                    notfound.append(seg)
            if len(notfound):
                raise(PhonoProbError("Segments not found in the corpus: {}".format(', '.join(notfound))))
            else:
                raise(PhonoProbError("Segments not found in the corpus: {} at position: {}".format(', '.join(s),i)))
        tot += 1
    try:
        totprob = totprob / tot
    except ZeroDivisionError:
        pass
    return totprob

