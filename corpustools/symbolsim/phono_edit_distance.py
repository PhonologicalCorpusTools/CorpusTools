

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

