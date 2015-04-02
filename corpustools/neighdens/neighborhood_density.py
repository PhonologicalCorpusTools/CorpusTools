from corpustools.corpus.classes import Word
from corpustools.symbolsim.edit_distance import edit_distance
from corpustools.symbolsim.khorsi import khorsi
from corpustools.symbolsim.phono_edit_distance import phono_edit_distance
from corpustools.symbolsim.phono_align import Aligner
from corpustools.symbolsim.string_similarity import string_sim_key

from corpustools.multiprocessing import filter_mp, score_mp

from functools import partial
from math import factorial
import operator

from corpustools.exceptions import NeighDenError

def args_to_key(*args):
    return '_'.join(['neighbor']+[str(x) for x in args])

def is_edit_distance_neighbor(w, query, sequence_type, max_distance):
    if len(getattr(w, sequence_type)) > len(getattr(query, sequence_type))+max_distance:
        return False
    if len(getattr(w, sequence_type)) < len(getattr(query, sequence_type))-max_distance:
        return False
    return edit_distance(w, query, sequence_type, max_distance) <= max_distance

def is_phono_edit_distance_neighbor(w, query, sequence_type, specifier, max_distance):
    return phono_edit_distance(w, query, sequence_type, specifier) <= max_distance

def is_khorsi_neighbor(w, query, freq_base, sequence_type, max_distance):
    return khorsi(w, query, freq_base, sequence_type, max_distance) >= max_distance


def pair_if_neighbor(w, query, algorithm, sequence_type, max_distance):
    result = False
    if algorithm == 'edit_distance':
        if len(getattr(w, sequence_type)) > len(getattr(query, sequence_type))+max_distance:
            return None
        if len(getattr(w, sequence_type)) < len(getattr(query, sequence_type))-max_distance:
            return None
        result = edit_distance(w, query, sequence_type) <= max_distance
    elif algorithm == 'phonological_edit_distance' and sequence_type == 'transcription':
        result = phono_edit_distance(w, query, tiername, corpus.specifier) <= max_distance
    elif algorithm == 'khorsi':
        freq_base = freq_base = corpus.get_frequency_base(sequence_type, count_what)
        result = khorsi(w, query, freq_base, sequence_type) >= max_distance
    else:
        return None
    if result:
        return (w,query)

def generate_neighborhood_density_graph(corpus, sequence_type = 'transcription',
            algorithm = 'edit_distance', max_distance = 1,
            count_what='type', num_cores = 1,
            stop_check = None, call_back = None):
    if call_back is not None:
        call_back('Generating neighborhood density graph...')
        num_comps = factorial(len(corpus))/(factorial(len(corpus)-2)*2)
        call_back(0,num_comps/500)
    keys = list(corpus.keys())
    detail_key = args_to_key(sequence_type, algorithm, max_distance, count_what)

    iterable = ((corpus.wordlist[keys[i]],corpus.wordlist[keys[j]])
                    for i in range(len(keys)) for j in range(i+1,len(keys)))

    function = partial(is_neighbor,algorithm=algorithm, sequence_type=sequence_type,
                    max_distance=max_distance, count_what = count_what)
    edges = filter_mp(iterable, function, num_cores, call_back, stop_check)
    if stop_check is not None and stop_check():
        return
    for e in edges:
        corpus._graph.add_edge(corpus.key(e[0]), corpus.key(e[1]),key = detail_key)
    corpus._graph.graph['neighborhoods'].append(detail_key)


def neighborhood_density_graph(corpus, query, sequence_type = 'transcription',
            algorithm = 'edit_distance', max_distance = 1,
            count_what='type',
            stop_check = None, call_back = None):
    detail_key = string_sim_key(algorithm, sequence_type, count_what)
    if detail_key not in corpus._graph.graph['symbolsim']:
        raise(NeighDenError("Optimized graph not found!"))
    if stop_check is not None and stop_check():
        return
    key = corpus.key(query)
    neighbors = list()
    if algorithm == 'khorsi':
        op = operator.ge
    else:
        op = operator.le
    for k,v in corpus._graph[key].items():
        if op(v[detail_key]['weight'], max_distance):
            neighbors.append(corpus[k])
    return (len(neighbors), neighbors)

def neighborhood_density_all_words(corpus, attribute, sequence_type = 'transcription',
            algorithm = 'edit_distance', max_distance = 1,
            count_what='type', num_cores = -1,
            stop_check = None, call_back = None):
    function = partial(neighborhood_density, corpus, algorithm=algorithm, sequence_type=sequence_type,
                        max_distance=max_distance, count_what = count_what)
    if call_back is not None:
        call_back('Calculating neighborhood densities...')
        call_back(0,len(corpus))
        cur = 0
    if num_cores == -1:

        for w in corpus:
            if stop_check is not None and stop_check():
                return
            cur += 1
            call_back(cur)
            res = function(w)

            setattr(w, attribute.name, res[0])
    else:
        iterable = ((w,) for w in corpus)


        neighbors = score_mp(iterable, function, num_cores, call_back, stop_check, chunk_size= 1)
        for n in neighbors:
            #Have to look up the key, then look up the object due to how
            #multiprocessing pickles objects
            setattr(corpus.find(corpus.key(n[0])), attribute.name, n[1][0])



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
        If 'spelling', will calculate neighborhood density on spelling.
        If 'transcription' will calculate neighborhood density on transcriptions.
        Otherwise, calculate on specified tier.

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
    #detail_key = string_sim_key(algorithm, sequence_type, count_what)
    #if detail_key in corpus._graph.graph['symbolsim']:
    #    return neighborhood_density_graph(corpus, query, sequence_type,
    #        algorithm, max_distance,
    #        count_what,
    #        stop_check, call_back)
    matches = []
    if call_back is not None:
        call_back('Finding neighbors...')
        call_back(0,len(corpus))
        cur = 0
    if algorithm == 'edit_distance':
        is_neighbor = partial(is_edit_distance_neighbor,
                                sequence_type = sequence_type,
                                max_distance = max_distance)
    elif algorithm == 'phono_edit_distance':
        is_neighbor = partial(is_phono_edit_distance_neighbor,
                                specifier = corpus.specifier,
                                sequence_type = sequence_type,
                                max_distance = max_distance)
    elif algorithm == 'khorsi':
        freq_base = freq_base = corpus.get_frequency_base(sequence_type, count_what)
        is_neighbor = partial(is_khorsi_neighbor,
                                freq_base = freq_base,
                                sequence_type = sequence_type,
                                max_distance = max_distance)
    for w in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 10 == 0:
                call_back(cur)
        if not is_neighbor(w, query):
            continue
        matches.append(w)
    neighbors = set(matches)-set([query])

    return (len(neighbors), neighbors)

def find_mutation_minpairs_all_words(corpus, attribute,
                    sequence_type='transcription', num_cores = -1,
                    stop_check = None, call_back = None):
    function = partial(find_mutation_minpairs, corpus, sequence_type=sequence_type)
    if call_back is not None:
        call_back('Calculating neighborhood densities...')
        call_back(0,len(corpus))
        cur = 0
    if num_cores == -1:

        for w in corpus:
            if stop_check is not None and stop_check():
                return
            cur += 1
            call_back(cur)
            res = function(w)

            setattr(w, attribute.name, res[0])
    else:
        iterable = ((w,) for w in corpus)


        neighbors = score_mp(iterable, function, num_cores, call_back, stop_check, chunk_size= 1)
        for n in neighbors:
            #Have to look up the key, then look up the object due to how
            #multiprocessing pickles objects
            setattr(corpus.find(corpus.key(n[0])), attribute.name, n[1][0])

def find_mutation_minpairs(corpus, query,
                    sequence_type='transcription',
                    stop_check = None, call_back = None):
    """Find all minimal pairs of the query word based only on segment
    mutations (not deletions/insertions)

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

