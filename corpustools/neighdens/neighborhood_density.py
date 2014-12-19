from corpustools.corpus.classes import Word
from corpustools.symbolsim.edit_distance import edit_distance
from corpustools.symbolsim.khorsi import khorsi, make_freq_base
from corpustools.symbolsim.phono_edit_distance import phono_edit_distance
from corpustools.symbolsim.phono_align import Aligner

def neighborhood_density(corpus, query, sequence_type = 'transcription',
            algorithm = 'edit_distance', max_distance = 1,
            tiername = 'transcription', count_what='type', segment_delimiter=None,
            stop_check = None, call_back = None):
    """Calculate the neighborhood density of a particular word in the corpus.
    Parameters
    ----------
    corpus : Corpus
        The domain over which neighborhood density is calculated.
    query : Word (or, dispreferred: str or list of str)
        The word whose neighborhood density to calculate. Can be coerced into a Word from a string or list of strings, e.g. if the query is not in the corpus or if called from command line.
    sequence_type : str
        If 'spelling', will calculate neighborhood density on spelling. If 'transcription' will calculate neighborhood density on transcriptions. Otherwise, calculate on specified tier.
    algorithm : str
        The algorithm used to determine distance
    max_distance : number, optional
        Maximum edit distance from the queried word to consider a word a neighbor.
    tiername : str
        The tiername to calculate distance on
    count_what : str
        If 'type', count neighbors in terms of their type frequency. If 'token', count neighbors in terms of their token frequency
    segment_delimiter : str
        If not None, splits the query by this str to make a transcription/spelling list for the query's Word object. If None, split everywhere.

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

    # for the command line interface: convert str to Word
    query_word = ensure_query_is_word(query, corpus, sequence_type, segment_delimiter)

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
            if len(getattr(w, sequence_type)) > len(getattr(query_word, sequence_type))+max_distance:
                continue
            if len(getattr(w, sequence_type)) < len(getattr(query_word, sequence_type))-max_distance:
                continue
        if not is_neighbor(w, query_word, algorithm, max_distance):
            continue
        matches.append(str(getattr(w, sequence_type)))
    neighbors = set(matches)-set([str(getattr(query_word, sequence_type))])

    return (len(neighbors), neighbors)



def find_mutation_minpairs(corpus, query, sequence_type='transcription', segment_delimiter=None):
    """Find all minimal pairs of the query word based only on segment mutations (not deletions/insertions)

    Parameters
    ----------
    corpus : Corpus
        The domain over which the search for minimal pairs is carried out
    query : Word
        The word whose minimal pairs to find
    sequence_type : str
        Tier (or spelling or transcription) on which to search for minimal pairs
    segment_delimiter : str
        If not None, splits the query by this str to make a transcription/spelling list for the query's Word object. If None, split everywhere.

    Returns
    -------
    list
        The found minimal pairs for the queried word
    """
    # for the command line interface: convert str to Word
    query_word = ensure_query_is_word(query, corpus, sequence_type, segment_delimiter)

    matches = []
    al = Aligner(features_tf=False, ins_penalty=float('inf'), del_penalty=float('inf'), sub_penalty=1)
    for w in corpus:
        if (len(getattr(w, sequence_type)) > len(getattr(query_word, sequence_type))+1 or 
            len(getattr(w, sequence_type)) < len(getattr(query_word, sequence_type))-1):
            continue
        m = al.make_similarity_matrix(getattr(query_word, sequence_type), getattr(w, sequence_type))
        if m[-1][-1]['f'] != 1:
            continue
        matches.append(str(getattr(w, sequence_type)))
    
    return set(matches)-set([str(getattr(query_word, sequence_type))])


def ensure_query_is_word(query, corpus, sequence_type, segment_delimiter):
    if isinstance(query, Word):
        query_word = query
    else:
        try:
            query_word = corpus.find(query)
        except KeyError:
            if segment_delimiter == None:
                query_word = Word(**{sequence_type: list(query)})
            else:
                query_word = Word(**{sequence_type: query.split(segment_delimiter)})
    return query_word
