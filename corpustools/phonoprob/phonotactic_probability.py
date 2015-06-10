# -*- coding: utf-8 -*-

from corpustools.corpus.classes import Word

from corpustools.exceptions import PhonoProbError

def phonotactic_probability_all_words(corpus, attribute, algorithm, sequence_type,
                                    count_what = 'token',
                                    probability_type = 'unigram',
                                    segment_delimiter = '.',
                                    num_cores = -1,
                                    stop_check = None, call_back = None):
    if call_back is not None:
        call_back('Calculating phonotactic probabilities...')
        call_back(0,len(corpus))
        cur = 0
    if num_cores == -1:
        for w in corpus:
            if stop_check is not None and stop_check():
                break
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            if algorithm == 'vitevitch':
                res = phonotactic_probability_vitevitch(corpus, w,
                                        sequence_type = sequence_type,
                                        count_what = count_what,
                                        probability_type = probability_type,
                                        stop_check = stop_check)
                setattr(w,attribute.name,res)

def phonotactic_probability(corpus, query, algorithm, sequence_type,
                                    count_what = 'token',
                                    probability_type = 'unigram',
                                    segment_delimiter = '.',
                                    stop_check = None, call_back = None):
    if algorithm == 'vitevitch':
        return phonotactic_probability_vitevitch(corpus, query, sequence_type,
                                    count_what,
                                    probability_type,
                                    segment_delimiter,
                                    stop_check, call_back)

def phonotactic_probability_vitevitch(corpus, query,
                                    probability_type = 'unigram',
                                    segment_delimiter = '.',
                                    stop_check = None, call_back = None):

    if probability_type == 'unigram':
        gramsize = 1
    elif probability_type == 'bigram':
        gramsize = 2

    prob_dict = corpus.get_phone_probs(gramsize = gramsize)
    sequence = zip(*[getattr(query, getattr(corpus, 'sequence_type'))[i:] for i in range(gramsize)])

    totprob = 0
    tot = 0
    for i,s in enumerate(sequence):
        try:
            totprob += prob_dict[s,i]
        except KeyError:
            notfound = []

            for seg in s:
                if seg not in getattr(corpus, 'corpus').inventory:
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

