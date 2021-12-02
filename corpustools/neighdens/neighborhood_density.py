from functools import partial

from corpustools.corpus.classes import Word
from corpustools.symbolsim.edit_distance import edit_distance
from corpustools.symbolsim.khorsi import khorsi
from corpustools.symbolsim.phono_edit_distance import phono_edit_distance
from corpustools.symbolsim.phono_align import Aligner
from corpustools.multiproc import filter_mp, score_mp


def _is_edit_distance_neighbor(w, query, sequence_type, max_distance):
    w_len = len(getattr(w, sequence_type))
    query_len = len(getattr(query, sequence_type))
    if w_len > query_len + max_distance:
        return False
    if w_len < query_len - max_distance:
        return False

    # should be greater than 0, because two identical words (i.e., an edit distance of 0) are not phono neighbours!
    return 0 < edit_distance(getattr(w, sequence_type), getattr(query, sequence_type),
                         sequence_type, max_distance) <= max_distance


def _is_phono_edit_distance_neighbor(w, query, sequence_type, specifier, max_distance):
    return phono_edit_distance(getattr(w, sequence_type), getattr(query, sequence_type), sequence_type, specifier) <= max_distance


def _is_khorsi_neighbor(w, query, freq_base, sequence_type, max_distance):
    return khorsi(getattr(w, sequence_type), getattr(query, sequence_type), freq_base, sequence_type, max_distance) >= max_distance


def neighborhood_density_all_words(corpus_context, tierdict, tier_type = None, sequence_type = None,
            algorithm = 'edit_distance', max_distance = 1, output_format = 'spelling',
            num_cores = -1, settable_attr = None, collapse_homophones = False,
            stop_check = None, call_back = None):
    """Calculate the neighborhood density of all words in the corpus and
    adds them as attributes of the words.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    algorithm : str
        The algorithm used to determine distance
    max_distance : float, optional
        Maximum edit distance from the queried word to consider a word a neighbor.
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function
    settable_attr: string
        Name of attribute that neighbourhood density results will be assigned to
    """
    function = partial(neighborhood_density, corpus_context,
                        tierdict = tierdict,
                        tier_type = tier_type,
                        sequence_type = sequence_type,
                        algorithm = algorithm,
                        max_distance = max_distance,
                        collapse_homophones = collapse_homophones)
    if call_back is not None:
        call_back('Calculating neighborhood densities...')
        call_back(0,len(corpus_context))
        cur = 0

    results = dict()
    last_value_removed = None
    last_key_removed = None
    if num_cores == -1 or num_cores == 1:

        for w in corpus_context:
            if stop_check is not None and stop_check():
                return
            if last_value_removed:
                tierdict[last_key_removed].append(last_value_removed)
            w_sequence = getattr(w, corpus_context.sequence_type)
            last_key_removed = str(w_sequence)
            for i, item in enumerate(tierdict[last_key_removed]):
                if str(item) == str(w):
                    last_value_removed = tierdict[last_key_removed].pop(i)
                    break
            res = neighborhood_density(corpus_context, w, tierdict,
                        tier_type = tier_type,
                        sequence_type = sequence_type,
                        algorithm = algorithm,
                        max_distance = max_distance,
                        collapse_homophones = collapse_homophones)

            # w_t_key is the pair of spelling and transcription which will be the key for the dictionary 'results'
            # Need to add a unique number after the pair, since spelling + transcription pair may be duplicate,
            # See the documentation on the 'Collapse homophones' option for the use case scenario and also Issue #785.
            n = 0
            w_t_key = f'{w} [{w.transcription}]{n}'
            if w_t_key in results:
                while True:
                    n += 1
                    w_t_key = f'{w} [{w.transcription}]{n}'
                    if w_t_key not in results:
                        break

            results[w_t_key] = [getattr(r, output_format) for r in res[1]]
            setattr(w.original, settable_attr.name, res[0])


        # for w in corpus_context:
        #     if stop_check is not None and stop_check():
        #         return
        #     cur += 1
        #     call_back(cur)
        #     res = function(w)
        #     results[str(w)] = [getattr(r, output_format) for r in res[1]]
        #     setattr(w.original, settable_attr.name, res[0]-1)
        #     #the -1 is to account for the fact that words are counted as their own neighbour, and this is incorrect
        #     #subtracting 1 here is easier than fixing the neighbourhood density algorithm
    else:
        iterable = ((w,) for w in corpus_context)
        neighbors = score_mp(iterable, function, num_cores, call_back, stop_check, chunk_size = 1)
        for n in neighbors:
            #Have to look up the key, then look up the object due to how
            #multiprocessing pickles objects
            setattr(corpus_context.corpus.find(corpus_context.corpus.key(n[0])),
                    #corpus_context.attribute.name, n[1][0])
                    settable_attr.name, n[1][0])

    return results

def neighborhood_density(corpus_context, query, tierdict,
            algorithm = 'edit_distance', max_distance = 1, collapse_homophones = False,
            force_quadratic = False, file_type = None, tier_type=None, sequence_type = None,
            stop_check = None, call_back = None):
    """Calculate the neighborhood density of a particular word in the corpus.

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    query : Word
        The word whose neighborhood density to calculate.
    algorithm : str
        The algorithm used to determine distance
    max_distance : float, optional
        Maximum edit distance from the queried word to consider a word a neighbor
    force_quadratic : bool
        Force use of the less efficient quadratic algorithm even when finding edit 
        distance of 1 neighborhoods
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    tuple(int, set)
        Tuple of the number of neighbors and the set of neighbor Words.
    """

    matches = []                # list to contain phono neighbours
    query = ensure_query_is_word(query, corpus_context, corpus_context.sequence_type, tier_type)

    if call_back is not None:
        call_back('Finding neighbors for {}...'.format(query))
        call_back(0,len(corpus_context))
        cur = 0

    if algorithm == 'edit_distance' and max_distance == 1 and force_quadratic:
        return fast_neighborhood_density(corpus_context, query, corpus_context.sequence_type, tier_type, tierdict,
                                         file_type=file_type, collapse_homophones=collapse_homophones)

    if algorithm == 'edit_distance':
        is_neighbor = partial(_is_edit_distance_neighbor,
                                sequence_type = corpus_context.sequence_type,
                                max_distance = max_distance)
    elif algorithm == 'phono_edit_distance':
        is_neighbor = partial(_is_phono_edit_distance_neighbor,
                                specifier = corpus_context.specifier,
                                sequence_type = corpus_context.sequence_type,
                                max_distance = max_distance)
    elif algorithm == 'khorsi':
        freq_base = corpus_context.get_frequency_base()
        is_neighbor = partial(_is_khorsi_neighbor,
                                freq_base = freq_base,
                                sequence_type = corpus_context.sequence_type,
                                max_distance = max_distance)
    for w in corpus_context:            # loop over each word (w) in the corpus
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 10 == 0:
                call_back(cur)
        if not is_neighbor(w, query):                  # if *not* neighbor then do not add to 'matches'
            continue

        # the following conditional checks whether collapse homophones is True. If so, remove homophones
        if collapse_homophones:
            w_sequence = getattr(w, sequence_type)

            # if the transcription of the just-found potential neighbor is identical to
            # anything we already have as previously found neighbours, do not add the current result into 'matches.'
            if any(getattr(m, sequence_type) == w_sequence for m in matches):
                continue

        matches.append(w)
    neighbors = matches

    return (len(neighbors), neighbors)


def fast_neighborhood_density(corpus_context, query, sequence_type, tier_type,
                              tierdict, file_type=None, trans_delimiter='.', collapse_homophones = False):
    """Generates all neighbors of edit distance <= 1 and searches 
    for them in corpus_context.

    Will be faster than neighborhood_density when:
    n > m * (1 + s), where
    n: number of words in corpus
    m: length of query
    s: size of segment inventory
    """

    neighbors = list()
    query = ensure_query_is_word(query, corpus_context, sequence_type, tier_type, file_type=file_type)

    for candidate in generate_neighbor_candidates(corpus_context, query, sequence_type):
        if tier_type.att_type == 'tier':
            cand_str = trans_delimiter.join(candidate)
        else:
            cand_str = ''.join(candidate)

        if cand_str in tierdict:
            for w in tierdict[cand_str]:
                w_sequence = getattr(w, sequence_type)
                if collapse_homophones and any(getattr(word, sequence_type) == w_sequence for word in neighbors):
                    continue
                else:
                    neighbors.append(w)
    return (len(neighbors), neighbors)

def generate_neighbor_candidates(corpus_context, query, sequence_type):
    sequence = getattr(query, sequence_type)
    yield [str(c) for c in sequence]
    for i in range(len(sequence)):
        yield [str(c) for c in sequence[:i]] + [str(c) for c in sequence[i+1:]] # deletion
        for char in corpus_context.inventory:
            if str(char) not in ['#', sequence[i]]:
                yield [str(c) for c in sequence[:i]] + [str(char)] + [str(c) for c in sequence[i:]] # insertion
                yield [str(c) for c in sequence[:i]] + [str(char)] + [str(c) for c in sequence[i+1:]] # substitution
    for char in corpus_context.inventory: # final pass to get insertion at len+1
        if str(char) not in ['#', sequence[i]]:
            yield [str(c) for c in sequence[:]] + [str(char)] # insertion

def find_mutation_minpairs_all_words(corpus_context, tierdict, tier_type = None, num_cores = -1,
                                     output_format = 'spelling', collapse_homophones=False,
                                     stop_check = None, call_back = None):

    function = partial(find_mutation_minpairs, corpus_context, tier_type=tier_type, collapse_homophones = collapse_homophones)
    if call_back is not None:
        call_back('Calculating neighborhood densities...')
        call_back(0,len(corpus_context))
        cur = 0

    results = dict()
    last_value_removed = None
    last_key_removed = None
    if num_cores == -1 or num_cores == 1:
        for w in corpus_context:
            if stop_check is not None and stop_check():
                return
            if last_value_removed:
                tierdict[last_key_removed].append(last_value_removed)
            w_sequence = getattr(w, corpus_context.sequence_type)
            last_key_removed = str(w_sequence)
            for i, item in enumerate(tierdict[last_key_removed]):
                if str(item) == str(w):
                    last_value_removed = tierdict[last_key_removed].pop(i)
                    break
            res = find_mutation_minpairs(corpus_context, w,
                                         tier_type=tier_type, collapse_homophones = collapse_homophones)
            w_t_key = f'{w} [{w.transcription}]'
            results[w_t_key] = [getattr(r, output_format) for r in res[1]]
            setattr(w.original, corpus_context.attribute.name, res[0])

        # for w in corpus_context:
        #     if stop_check is not None and stop_check():
        #         return
        #     cur += 1
        #     call_back(cur)
        #     res = function(w)
        #     results[str(w)] = res[1]#[str(r) for r in res[1]]
        #     setattr(w.original, corpus_context.attribute.name, res[0])
    else:
        iterable = ((w,) for w in corpus_context)
        neighbors = score_mp(iterable, function, num_cores, call_back, stop_check, chunk_size= 1)
        for n in neighbors:
            #Have to look up the key, then look up the object due to how
            #multiprocessing pickles objects
            setattr(corpus_context.corpus.find(corpus_context.corpus.key(n[0])), corpus_context.attribute.name, n[1][0])

    return results

def find_mutation_minpairs(corpus_context, query, tier_type = None, collapse_homophones = False,
                    stop_check = None, call_back = None):
    """Find all minimal pairs of the query word based only on segment
    mutations (not deletions/insertions)

    Parameters
    ----------
    corpus_context : CorpusContext
        Context manager for a corpus
    query : Word
        The word whose minimal pairs to find
    stop_check : callable or None
        Optional function to check whether to gracefully terminate early
    call_back : callable or None
        Optional function to supply progress information during the function

    Returns
    -------
    list
        The found minimal pairs for the queried word
    """
    matches = []
    sequence_type = corpus_context.sequence_type
    query = ensure_query_is_word(query, corpus_context, corpus_context.sequence_type, tier_type)
    if call_back is not None:
        call_back('Finding neighbors...')
        call_back(0,len(corpus_context))
        cur = 0
    al = Aligner(features_tf=False, ins_penalty=float('inf'), del_penalty=float('inf'), sub_penalty=1)
    for w in corpus_context:
        w_sequence = getattr(w, sequence_type)
        query_sequence = getattr(query, sequence_type)
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 10 == 0:
                call_back(cur)
        if (len(w_sequence) > len(query_sequence)+1 or
            len(w_sequence) < len(query_sequence)-1):
            continue
        m = al.make_similarity_matrix(query_sequence, w_sequence)
        if m[-1][-1]['f'] != 1:
            continue

        w_sequence = getattr(w, sequence_type)  # This is identical to the one right after the start of for-loop. why?
        if collapse_homophones and any(getattr(m, sequence_type) == w_sequence for m in matches):
            continue
        else:
            #matches.append(str(w_sequence))
            matches.append(w)

    neighbors = set(matches)-set([query])
    return (len(neighbors), neighbors)

def ensure_query_is_word(query, corpus, sequence_type, tier_type, trans_delimiter='.', file_type=None):

    if isinstance(query, Word):
        query_word = query
    else:
        if tier_type.att_type == 'spelling':
            if file_type == sequence_type:
                query_word = Word(**{sequence_type: list(query)})
            else:
                query_word = query.replace(trans_delimiter, '')
                query_word = Word(**{sequence_type: list(query_word)})

        elif tier_type.att_type == 'tier':
            if file_type == sequence_type:
                query_with̠td = '.'.join(query) if '.' not in query else query
                for entry in corpus:
                    corpus_word_with_td = str(getattr(entry, sequence_type))
                    if query_with̠td == corpus_word_with_td:        # if a word in corpus has the same transcription
                        return entry                                # that word in the corpus is to be referred to.

                # the following should be run if no word found in corpus with the transcription
                new_query = parse(query, trans_delimiter)
                query_word = Word(**{sequence_type: new_query})
            else:   # if file contains spelling
                try:
                    query_word = corpus.corpus.find(query)
                except KeyError:
                    # if the word in the file can't be found in the corpus
                    new_query = parse(query, trans_delimiter)
                    query_word = Word(**{sequence_type: list(new_query)})

    return query_word

def parse(word, delimiter):
    return word.split(delimiter) if delimiter in word else list(word)