from corpustools.corpus.classes.lexicon import SyllableEnvironmentFilter

from corpustools.exceptions import TPError


def calc_trans_prob(corpus_context, bigram, word_boundaries, direction, mode = 'segMode', call_back = None):
    """
    Calculate the transitional probability of a bigram.

    :param mode:
    :param corpus_context: ContextManager for a corpus
    :param bigram: either tuple of two segments, or a SyllableEnvironmentFilter
    :param word_boundaries: 'Halved', 'Both sides', or 'Ignored'
    :param direction: forwards or backwards TP (either 0 for forwards or 1 for backwards)
    :return: float: (forwards/backwards) transitional probability of a bigram
    """

    if call_back is not None:
        call_back("Generating probabilities...")
        call_back(0,0)
        cur = 0

    if mode == 'segMode':
        is_in_corpus = corpus_context.get_frequency_base()
        try:
            is_in_corpus[bigram[0]]
        except KeyError:
            raise TPError('The segment %s was not found in the corpus.' % bigram[0])
        try:
            is_in_corpus[bigram[1]]
        except KeyError:
            raise(TPError('The segment %s was not found in the corpus.' % bigram[1]))

        if word_boundaries == 'Word-end only':
            bigram_dict = corpus_context.get_frequency_base(gramsize=2, halve_edges=True, probability=True, need_wb=True)
        elif word_boundaries == 'Both sides':
            bigram_dict = corpus_context.get_frequency_base(gramsize=2, halve_edges=False, probability=True, need_wb=True)
        else:
            bigram_dict = corpus_context.get_frequency_base(gramsize=2, halve_edges=False, probability=True, need_wb=False)


        try:
            prob_bg = bigram_dict[bigram]
        except KeyError:
            raise TPError('The string \'%s\' was not found in the corpus.' % ''.join(bigram))

        if prob_bg == 0.0:
            raise TPError('Transitional probability cannot be calculated for ' + ''.join(bigram))

        # Find the probability of a_ and _b bigrams for a bigram (a, b)
        in_context_prob = 0
        if direction == 'forward':
            in_context_prob = sum([bigram_dict[pair] if pair[0] == bigram[0] else 0 for pair in bigram_dict])
        elif direction == 'backward':
            in_context_prob = sum([bigram_dict[pair] if pair[1] == bigram[1] else 0 for pair in bigram_dict])

        return prob_bg / in_context_prob

    # Calculation using syllables. WIP.
    else:
        # create an unspecified syllable, find the number of all syllables in corpus
        bigram_filter = SyllableEnvironmentFilter(corpus_context.inventory, bigram[1].middle, lhs=bigram[0].middle)
        unspecified_dict = {'contents':[], 'search_type':'Minimally contains'}
        unspecified_syll = {'onset':unspecified_dict, 'nucleus':unspecified_dict, 'coda':unspecified_dict,
                            'stress':set(list(corpus_context.inventory.stress_types.keys()) + ['None']),
                             'tone':set(list(corpus_context.inventory.tone_types.keys()) + ['None']), 'nonsegs':set()}
        num_syllables = len(corpus_context.corpus.inventory.syllables)

        # All the words that contain the two syllables in sequence
        with_combined_context = search_for_syll_context(corpus_context.corpus, bigram_filter)
        with_combined_prob = len(with_combined_context) / num_syllables

        if with_combined_prob == 0.0:
            raise TPError('The sequence \'%s\' was not found in the corpus.' % str(bigram_filter))

        # all the words that contain the first syllable followed by any syllable
        first_context_filter = SyllableEnvironmentFilter(bigram_filter.inventory, bigram_filter.lhs, rhs=[unspecified_syll])
        with_first_context = search_for_syll_context(corpus_context.corpus, first_context_filter)
        with_first_prob = len(with_first_context) / num_syllables

        # the words that contain any syllable followed by the second syllable
        second_context_filter = SyllableEnvironmentFilter(bigram_filter.inventory, bigram_filter.middle, lhs=[unspecified_syll])
        with_second_context = search_for_syll_context(corpus_context.corpus, second_context_filter)
        with_second_prob = len(with_second_context) / num_syllables

        # find transitional probability
        if direction == 'forward':
            return with_combined_prob / with_first_prob
        elif direction == 'backward':
            return with_combined_prob / with_second_prob


def search_for_syll_context(corpus, env_filter):
    with_context = []
    for word in corpus:
        tier = getattr(word, 'transcription')
        if tier.find(env_filter, 'sylMode') is not None:
            with_context.append(word)
    return with_context