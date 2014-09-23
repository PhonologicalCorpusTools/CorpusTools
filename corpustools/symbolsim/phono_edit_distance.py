

from corpustools.symbolsim.phono_align_ex import Aligner

def phono_edit_distance(word1, word2, tier_name, features):
    """Returns an analogue to Levenshtein edit distance but uses
    phonological features instead of characters

    Parameters:
    word1: Word
        Word object containing transcription tiers which will be compared
        to another word containing transcription tiers
    word2: Word
        The other word containing transcription tiers to which word1 will
        be compared
    tier_name: string
        Name of the transcription tier to use for comparisons
    features: FeatureMatrix
        FeatureMatrix that contains all the segments in both transcriptions
        to be compared

    Returns
    -------
    float
        the phonological edit distance between two words
    """

    w1 = getattr(word1,tier_name)
    w2 = getattr(word2,tier_name)


    a = Aligner(features_tf=True, features=features)

    m = a.make_similarity_matrix(w1, w2)

    return m[-1][-1]['f']

