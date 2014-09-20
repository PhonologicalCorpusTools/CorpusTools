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

def mass_relate(corpus, query, algorithm, **kwargs):
    """Given an input Word, uses a corpus to calculate the relatedness of
    all other words in the corpus to that input Word

    Parameters
    ----------
    query: Word
        Either a string or list of segments representing a word in a corpus
    string_type: string
        The type of segments to be used ('spelling' = roman letters, 'transcription' = IPA symbols), defaults to 'spelling'

    Returns
    -------
    list
        a list of all words in a corpus with their respective relatedness score to the input word w in a writeable format for .txt files
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
    if isinstance(query,str):
        targ_word = corpus.find(query)
        relate = list()
        for word in corpus:
            relatedness = relate_func(targ_word, word)
            relate.append( (targ_word,word,relatedness) )
        #Sort the list by most morphologically related
        relate.sort(key=lambda t:t[-1])
        if relate[0][1] != targ_word:
            relate.reverse()
    elif isinstance(query, list):
        relate = list()
        for q1,q2 in query:
            w1 = corpus.find(q1)
            w2 = corpus.find(q2)
            relatedness = relate_func(w1,w2)
            relate.append( (w1,w2,relatedness) )
    elif isinstance(query, tuple):
        w1 = corpus.find(query[0])
        w2 = corpus.find(query[1])
        relatedness = relate_func(w1,w2)
        relate = [(w1,w2,relatedness)]
    return relate


def string_similarity(corpus, query, algorithm, **kwargs):
    """Given an input of pairs of words to compare to each other, returns such pairs and their relatedness scores

    Parameters
    ----------
    corpus: Corpus
        The corpus object to use
    relator_type: string
        The type of relator to be used to measure relatedness, e.g. 'khorsi'
    string_type: string
        The type of segments to be used ('spelling' = roman letters, 'transcription' = IPA symbols)
    count_what: string
        The type of frequency, either 'type' or 'token'
    input_data: string - .txt filename
        The name of a .txt file which contains pairs of words separated by tabs with each pair on a new line
    output_name: string
        The name of the desired output file, if output_filename == None, no file will be created and instead the data will be returned as a list
    max_rel: double
        Filters out all words that are higher than max_rel from a relatedness measure
    min_rel: double
        Filters out all words that are lower than min_rel from a relatedness measure

    Returns
    -------
    If output_filename exists, nothing is returned, a textfile is created
    If output_filename == None, a list the pairs and their relatedness scores is returned
    """


    related_data = mass_relate(corpus,query,algorithm, **kwargs)

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


