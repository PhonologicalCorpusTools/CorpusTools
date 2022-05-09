from corpustools.corpus.classes import Word


def phonological_search(corpus, envs, sequence_type='transcription', call_back=None, stop_check=None,
                        mode='segMode', result_type='positive', min_word_freq=0.0, max_word_freq=float('inf'),
                        min_phon_num = 0.0, max_phon_num=float('inf'), min_syl_num=0.0, max_syl_num=float('inf'), seg_summary=False):
    """
    Perform a search of a corpus for segments, with the option of only
    searching in certain phonological environments. Can filter by minimum word frequency,
    number of phonemes, or number of syllables.

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
    min_word_freq, max_word_freq : float 
        Minimum / Maximum token frequency in a corpus, used for filtering the results
    min_phon_num, max_phon_num : float 
        Minimum / Maximum number of phonemes in a word, used for filtering the results
    min_syl_num, max_syl_num : float 
        Minimum / Maximum number of syllables in a word, used for filtering the results. 
        Only applicable if syllable delimiters are provided
    

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

        for i, env in enumerate(envs):
            es = tier.find(env, mode)
            try:
                found.extend([[i, e] for e in es])
            except TypeError:  # when es == None
                found.append([i, es])

        fo = [f[1] for f in found]
        if result_type == 'positive':
            if not all(e is None for e in fo):   # if the word satisfies at least one environment,
                results.append((word, found))       # add it to 'results'
        else:
            if all(e is None for e in fo):
                results.append((word, found))

    # additional filters
    final_results = []
    for (word, found) in results:
        word_freq = word.frequency
        phon_num = len(str(word.transcription).split("."))
        if word_freq >= min_word_freq and word_freq <= max_word_freq:
            if phon_num >= min_phon_num and phon_num <= max_phon_num: 
                if len(corpus.inventory.syllables) == 0:
                    final_results.append((word, found))
                else:
                    syll_len = len(word.transcription._syllable_list)
                    if syll_len >= min_syl_num and syll_len <= max_syl_num:
                        final_results.append((word, found))

    # if the search does not have any result
    if len(final_results) == 0:                   # if nothing in 'results', take the side way
        word = Word(**{'spelling': 'N/A'})        # fake word to be a (invisible) placeholder in the result window
        found = [None] * len(found)               # fake 'None' environment to be an indicator that it has no hit
        final_results.append((word, found))
        return final_results

    return final_results


