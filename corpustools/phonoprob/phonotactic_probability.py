# -*- coding: utf-8 -*-

from corpustools.corpus.classes import Word

def phonotactic_probability_vitevitch(corpus, query, sequence_type,
                                    count_what = 'token',
                                    probability_type = 'unigram',
                                    stop_check = None, call_back = None):

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

    if call_back is not None:
        call_back("Generating probabilities...")
        call_back(0,0)
        cur = 0
    if probability_type == 'unigram':
        gramsize = 1
    elif probability_type == 'bigram':
        gramsize = 2

    prob_dict = corpus.get_phone_probs(sequence_type, count_what,
                                        gramsize = gramsize)
    sequence = zip(*[getattr(query_word,sequence_type)[i:] for i in range(gramsize)])

    totprob = 0
    tot = 0
    for i,s in enumerate(sequence):
        totprob += prob_dict[s,i]
        tot += 1

    totprob = totprob / tot

    return totprob

