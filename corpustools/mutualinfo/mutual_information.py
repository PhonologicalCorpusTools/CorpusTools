import math
import time
import csv
import regex as re

from corpustools.exceptions import MutualInfoError
from corpustools.corpus.classes.lexicon import Corpus, Word


def mi_env_filter(corpus_context, envs, context_output_path='', word_boundary=True):
    """
    Environment filter
    It extracts only those words that satisfy environment condition and
    returns a new corpus_context. The output is to be an argument of the original MI function
    as the substitute of an original corpus_context
    Spelling and frequency of each word, frequency_threshold, and other parameters of corpus_context retained.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    envs : list of EnvironmentFilter
        List of EnvironmentFilter objects that specify environments
    context_output_path : str
        Path to save the list of 'clipped' words as a txt file (optional)
    word_boundary : bool
        Whether word boundary should be considered as a part of bigram
        Defaults to True

    Returns
    -------
    CorpusContext
        with only words that satisfy environment filter.
        All transcription removed except for the two position which will be compared against the bigram user inputs
    """
    pattern = ''
    wb_in_env = [False, False]
    clipped_corpus = Corpus(corpus_context.corpus.name)

    num_lhs = len(envs[0].lhs)
    num_rhs = len(envs[0].rhs)

    if num_lhs + num_rhs == 0:
        return corpus_context

    for left_string in envs[0].lhs:
        half_env = "(" + "|".join(left_string) + ")"
        if re.search(r"#", half_env) is not None:
            wb_in_env[0] = True
        pattern = pattern + half_env
    pattern = pattern + ".."
    for right_string in envs[0].rhs:
        half_env = "(" + "|".join(right_string) + ")"
        if re.search(r"#", half_env) is not None:
            wb_in_env[1] = True
        pattern = pattern + half_env
    pattern = re.compile(pattern)

    context_pair = []
    for word in corpus_context:
        tier = getattr(word, corpus_context.sequence_type)

        if word_boundary or (wb_in_env[0] + wb_in_env[1]) == 2:
            tier_search_from = "".join(tier.with_word_boundaries())
        elif wb_in_env[0] + wb_in_env[1]:
            tier_search_from = "#" + "".join(tier) if wb_in_env[0] else "".join(tier) + "#"
        else:
            tier_search_from = "".join(tier)

        found = pattern.finditer(tier_search_from, overlapped=True)
        env_context = []
        for f in found:
            if len(env_context) == 0:
                env_context = list(f.span())
            elif f.span()[0] < env_context[1]:
                env_context[1] = f.span()[1]
            else:
                newword = tier_search_from[env_context[0]:env_context[1]]
                context_pair.append((str(word),) + clip_context(newword, word, clipped_corpus))
                env_context = list(f.span())

        if env_context:
            newword = tier_search_from[env_context[0]:env_context[1]]
            context_pair.append((str(word),) + clip_context(newword, word, clipped_corpus))

    if bool(clipped_corpus.wordlist):  # if the clipped corpus is not empty, set it as the context for calculating MI
        corpus_context.corpus = clipped_corpus
    else:    # if the matrix corpus does not have any case of satisfying the specified env., prompt a warning
        raise MutualInfoError('Warning! Mutual information could not be calculated'
                              'because the specified environment is not in the corpus.')

    if context_output_path != '':
        with open(context_output_path, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['Orthography', 'Transcription', 'Environment',  'Context'])
            for context in context_pair:
                writer.writerow([context[0], context[1], str(envs[0]), context[2]])

    return corpus_context  # corpus_context (clipped), to be fed into the original function


def clip_context(new_trans, word, clipped_corpus):
    kwargs = {}
    new_trans = list(new_trans)
    original_word = getattr(word, word._transcription_name)
    kwargs[word._transcription_name] = new_trans
    kwargs[word._spelling_name] = str(word)
    kwargs[word._freq_name] = word._frequency
    kwargs['_freq_name'] = word._freq_name

    new_word = Word(**kwargs)
    clipped_corpus.add_word(new_word, allow_duplicates=True)  # add word to clipped_corpus
    return str(original_word), ''.join(new_trans)  # print the 'word' that satisfies the environment (and to be added)


def pointwise_mi(corpus_context, query, env_filtered=False, word_boundary='Word-end only', in_word=False,
                 stop_check=None, call_back=None):
    """
    Calculate the mutual information for a bigram.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    query : tuple
        Tuple of two strings, each a segment/letter
    env_filtered : bool
        True if a env filter selected by the user.
        Defaults to False
    word_boundary : str or bool
        How to count word boundaries once per word. str if no env filter selected, bool with env filters
        'Word-end only' counts once,
        'Both sides' counts twice (word-initial and word-final), and
        'Ignored' does not count word boundaries.
        Trueː env filter selected and # can be a part of a bigram.
        Defaults to 'Word-end only' (count word boundary once in word-final position)
    in_word : bool
        Flag to calculate non-local, non-ordered mutual information,
        defaults to False
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    float
        Mutual information of the bigram
    """
    if call_back is not None:
        call_back("Generating probabilities...")
        call_back(0,0)
        cur = 0
    if in_word:
        unigram_dict = get_in_word_unigram_frequencies(corpus_context, query)
        bigram_dict = get_in_word_bigram_frequency(corpus_context, query)
    else:
        need_wd = True
        halve_edges = True

        if env_filtered or word_boundary == 'Ignored':
            need_wd = False         # if env filtered, c(orpus) already has needed word boundaries when being clipped!
        elif word_boundary == 'Both sides':
            halve_edges = False

        unigram_dict = corpus_context.get_frequency_base(gramsize = 1, halve_edges = halve_edges,
                                                         probability=True, need_wb=need_wd)
        bigram_dict = corpus_context.get_frequency_base(gramsize = 2, halve_edges = halve_edges,
                                                        probability=True, need_wb=need_wd)

    try:
        prob_s1 = unigram_dict[query[0]]
    except KeyError:
        raise(MutualInfoError('The segment {} was not found in the corpus, '
                              'or in the environment, if you specified one. '.format(query[0])))
    try:
        prob_s2 = unigram_dict[query[1]]
    except KeyError:
        raise(MutualInfoError('The segment {} was not found in the corpus, '
                              'or in the environment, if you specified one. '.format(query[1])))
    try:
        prob_bg = bigram_dict[query]
    except KeyError:
        raise MutualInfoError('The bigram {} was not found in the corpus using {}s'.format(''.join(query), corpus_context.sequence_type))


    if unigram_dict[query[0]] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[0]))
    if unigram_dict[query[1]] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the unigram {} is not in the corpus.'.format(query[1]))
    if bigram_dict[query] == 0.0:
        raise MutualInfoError('Warning! Mutual information could not be calculated because the bigram {} is not in the corpus.'.format(str(query)))

    return math.log((prob_bg/(prob_s1*prob_s2)), 2)


def get_in_word_unigram_frequencies(corpus_context, query):
    totals = [0 for x in query]
    for word in corpus_context:
        for i, q in enumerate(query):
            if q in getattr(word, corpus_context.sequence_type):
                totals[i] += word.frequency
    return {k: totals[i] / len(corpus_context) for i, k in enumerate(query)}


def get_in_word_bigram_frequency(corpus_context, query):
    total = 0
    for word in corpus_context:
        tier = getattr(word, corpus_context.sequence_type)
        if all(x in tier for x in query):
            total += word.frequency
    return {query: total / len(corpus_context)}


def all_mis(corpus_context,
            word_boundary, in_word = False,
            stop_check = None, call_back = None):
    mis = {}
    total_calculations = ((len(corpus_context.inventory)**2)-len(corpus_context.inventory)/2)+1
    ct = 1
    t = time.time()
    for s1 in corpus_context.inventory:
        for s2 in corpus_context.inventory:
                #print('Performing MI calculation {} out of {} possible'.format(str(ct), str(total_calculations)))
                ct += 1
                #print('Duration of last calculation: {}'.format(str(time.time() - t)))
                t = time.time()
                if type(s1) != str:
                    s1 = s1.symbol
                if type(s2) != str:
                    s2 = s2.symbol
                #print(s1,s2)
                mi = pointwise_mi(corpus_context, (s1, s2), word_boundary = word_boundary, in_word = in_word)
                mis[(s1,s2)] = mi

    ordered_mis = sorted([(pair, str(mis[pair])) for pair in mis], key=lambda p: p[1])

    return ordered_mis
