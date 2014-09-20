

from corpustools.symbolsim.phono_align_ex import Aligner

def phono_edit_distance(word1, word2, tier_name, features):
    """Returns an analogue to Levenshtein edit distance but with the option of counting phonological features instead of characters

    Parameters:
    w1: string
        A string containing a transcription which will be compared to another string containing a transcription
    w2: string
        The other string containing a transcription to which w1 will be compared
    features_tf: boolean
        Set to True if edit_distance using phonological features is desired or False for only characters
    features: phonological features
        Features are the set feature specifications currently be used in the corpus (i.e. Hayes, SPE, etc.)
    """

    w1 = getattr(word1,tier_name)
    w2 = getattr(word2,tier_name)


    a = Aligner(features_tf=True, features=features)

    m = a.make_similarity_matrix(w1, w2)

    return m[-1][-1]['f']


def mass_relate(corpus, query, tier_name='transcription'):
    """Given an input Word, uses a corpus to calculate the relatedness of all other words in the corpus to that input Word

    Parameters
    ----------
    query: Word
        Either a string or list of segments representing a word in a corpus
    string_type: string
        The type of segments to be used ('spelling' = roman letters, 'transcription' = IPA symbols), defaults to 'spelling'
    count_what: string
        The type of frequency, either 'type' or 'token', defaults to 'type'

    Returns
    -------
    list
        a list of all words in a corpus with their respective relatedness score to the input word w in a writeable format for .txt files
    """
    if tier_name == 'spelling':
        raise(ValueError('Phonological edit distance is not applicable to orthography.'))
    targ_word = corpus.find(query)
    relate = list()
    for word in corpus:
        relatedness = phono_edit_distance(targ_word, word, tier_name, corpus.specifier)
        relate.append( (relatedness, word) )
    #Sort the list by most morphologically related
    relate.sort(key=lambda t:t[0])

    return relate

