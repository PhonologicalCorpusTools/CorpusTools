from corpustools.symbolsim.edit_distance import edit_distance

def neighborhood_density(corpus, query, max_distance=1, use_token_frequency=False):
    """Calculate the neighborhood density of a particular word in the corpus. 
    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.
    query : Word
        The word whose neighborhood density to calculate.
    max_distance : number, optional
        Maximum edit distance from the queried word to consider a word a neighbor.
    use_token_frequency : bool, optional
        If True, count neighbors in terms of their token frequency.

    Returns
    -------
    float
        The number of neighbors for the queried word.
    """
    query_transcription = corpus.find(query).transcription
    neighbors = [w for w in corpus if (len(w.transcription) <= len(query)+max_distance
                                   and len(w) >= len(query)-max_distance 
                                   and is_neighbor(w.transcription, query_transcription, max_distance))]

    def is_neighbor(w, query, max_distance):
        return edit_distance(w, query, 'transcription') <= max_distance

    # add option for token frequency

    return len(neighbors)



def neighborhood_density_2(corpus, query, max_distance=1, use_token_frequency=False):
    """Calculate the neighborhood density of a particular word in the corpus. Generates all possible neighbors of query and checks whether each is in the corpus.

    Parameters
    ----------
    corpus : Corpus
        The domain over which functional load is calculated.
    query : Word
        The word whose neighborhood density to calculate.
    max_distance : number, optional
        Maximum edit distance from the queried word to consider a word a neighbor.
    use_token_frequency : bool, optional
        If True, count neighbors in terms of their token frequency.

    Returns
    -------
    float
        The number of neighbors for the queried word.
    """
    pass