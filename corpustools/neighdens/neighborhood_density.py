from corpustools.corpus.classes import Word
from corpustools.symbolsim.edit_distance import edit_distance
from corpustools.symbolsim.khorsi import khorsi, make_freq_base
from corpustools.symbolsim.phono_edit_distance import phono_edit_distance
from corpustools.symbolsim.phono_align import Aligner

def neighborhood_density(corpus, query, sequence_type = 'transcription',
            algorithm = 'edit_distance', max_distance = 1,
            count_what='type',
            stop_check = None, call_back = None):
    """Calculate the neighborhood density of a particular word in the corpus.
    Parameters
    ----------
    corpus : Corpus
        The domain over which neighborhood density is calculated.
    query : Word
        The word whose neighborhood density to calculate.
    sequence_type : str
        If 'spelling', will calculate neighborhood density on spelling. If 'transcription' will calculate neighborhood density on transcriptions. Otherwise, calculate on specified tier.
    algorithm : str
        The algorithm used to determine distance
    max_distance : number, optional
        Maximum edit distance from the queried word to consider a word a neighbor.
    count_what : str
        If 'type', count neighbors in terms of their type frequency. If 'token', count neighbors in terms of their token frequency

    Returns
    -------
    float
        The number of neighbors for the queried word.
    """
    def is_neighbor(w, query, algorithm, max_distance):
        if algorithm == 'edit_distance':
            return edit_distance(w, query, sequence_type) <= max_distance
        elif algorithm == 'phonological_edit_distance' and sequence_type == 'transcription':
            return phono_edit_distance(w, query, tiername, corpus.specifier) <= max_distance
        elif algorithm == 'khorsi':
            freq_base = freq_base = corpus.get_frequency_base(sequence_type, count_what)
            return khorsi(w, query, freq_base, sequence_type) >= max_distance
        else:
            return False

    matches = []
    if call_back is not None:
        call_back('Finding neighbors...')
        call_back(0,len(corpus))
        cur = 0
    for w in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 10 == 0:
                call_back(cur)
        if algorithm == 'edit_distance':
            if len(getattr(w, sequence_type)) > len(getattr(query, sequence_type))+max_distance:
                continue
            if len(getattr(w, sequence_type)) < len(getattr(query, sequence_type))-max_distance:
                continue
        if not is_neighbor(w, query, algorithm, max_distance):
            continue
        matches.append(w)
    neighbors = set(matches)-set([query])

    return (len(neighbors), neighbors)

def find_mutation_minpairs(corpus, query,
                    sequence_type='transcription',
                    stop_check = None, call_back = None):
    """Find all minimal pairs of the query word based only on segment mutations (not deletions/insertions)

    Parameters
    ----------
    corpus : Corpus
        The domain over which the search for minimal pairs is carried out
    query : Word
        The word whose minimal pairs to find
    sequence_type : str
        Tier (or spelling or transcription) on which to search for minimal pairs

    Returns
    -------
    list
        The found minimal pairs for the queried word
    """
    matches = []
    if call_back is not None:
        call_back('Finding neighbors...')
        call_back(0,len(corpus))
        cur = 0
    al = Aligner(features_tf=False, ins_penalty=float('inf'), del_penalty=float('inf'), sub_penalty=1)
    for w in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 10 == 0:
                call_back(cur)
        if (len(getattr(w, sequence_type)) > len(getattr(query, sequence_type))+1 or
            len(getattr(w, sequence_type)) < len(getattr(query, sequence_type))-1):
            continue
        m = al.make_similarity_matrix(getattr(query, sequence_type), getattr(w, sequence_type))
        if m[-1][-1]['f'] != 1:
            continue
        matches.append(str(getattr(w, sequence_type)))

    neighbors = list(set(matches)-set([str(getattr(query, sequence_type))]))
    return (len(neighbors), neighbors)

