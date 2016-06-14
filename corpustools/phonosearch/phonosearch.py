

def phonological_search(corpus, envs, sequence_type = 'transcription',
                            call_back = None, stop_check = None):
    """
    Perform a search of a corpus for segments, with the option of only
    searching in certain phonological environments.

    Parameters
    ----------
    corpus : Corpus
        Corpus to search
    seg_list : list of strings or Segments
        Segments to search for
    envs : list
        Environments to search in
    sequence_type : string
        Specifies whether to use 'transcription' or the name of a
        transcription tier to use for comparisons
    stop_check : callable
        Callable that returns a boolean for whether to exit before
        finishing full calculation
    call_back : callable
        Function that can handle strings (text updates of progress),
        tuples of two integers (0, total number of steps) and an integer
        for updating progress out of the total set by a tuple

    Returns
    -------
    list
        A list of tuples with the first element a word and the second
        a tuple of the segment and the environment that matched
    """
    if sequence_type == 'spelling':
        return None
    if call_back is not None:
        call_back('Searching...')
        call_back(0, len(corpus))
        cur = 0
    results = []
    for word in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 20 == 0:
                call_back(cur)
        tier = getattr(word, sequence_type)
        found = []
        for env in envs:
            es = tier.find(env)
            if es is not None:
                found.extend(es)
        if found:
            results.append((word, found))
    return results
