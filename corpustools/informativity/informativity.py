from math import log2
from collections import defaultdict


def context(index, word, sequence_type = 'transcription'):
    """Get the context for a given segment, specified by its index. The context is 
    all preceding segments in the word. In the future, functionality to set the number
    of segments will be added. "All" is the preferred context type in Cohen Priva (2015).

    Parameters
    ----------
    index: int 
        Segment index
    word: Word 
        Word object from which the context will be obtained

    Returns
    -------
    tuple (Segment, ...)
        Tuple of context Segments     
   """
    return tuple(getattr(word, sequence_type)[0:index - 1])


def segment_in_context_frequencies(segment, corpus_context, sequence_type='transcription',
                                   stop_check=None, call_back=None):
    """Gets the frequencies of a segment occurring in a given context

    Parameters
    ----------
    segment: str
    corpus_context: CorpusContext
        Context manager for a corpus

   Returns
    ----------
    dict {tuple : int,...}
        Dictionary with tuple of context Segments as key, and integer of frequency as value
    """
    if call_back is not None:
        call_back('Calculating segment frequencies...')
        call_back(0, len(corpus_context))
        cur = 0
    contexts = defaultdict(int)
    for word in corpus_context:
        i = 0
        if stop_check is not None and stop_check():
            return 'quit'
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        for seg in getattr(word, sequence_type):
            i += 1
            if seg == segment:
                contexts[context(i, word, sequence_type)] += word.frequency
    return contexts


def context_frequencies(contexts, corpus_context, sequence_type='transcription', stop_check=None, call_back=None):
    """Given a dictionary (or list/iterable) of contexts and a corpus, gets frequencies for the
     contexts regardless of the following segment.

    Parameters
    ----------
    contexts: dict (or other iterable)
        Dictionary or other iterable of tuples containing contexts
    corpus_context: CorpusContext
        Context manager for a corpus

    Returns
    ----------
    dict {tuple : int,...}
        Dictionary with tuple of context segments as key, and integer of frequency as value
    """
    if call_back is not None:
        call_back('Calculating context frequencies...')
        call_back(0, len(contexts))
        cur = 0
    context_frs = defaultdict(int)
    for c in contexts:
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        if c is not None:
            for word in corpus_context:
                if stop_check is not None and stop_check():
                    return 'quit'
                if tuple(getattr(word, sequence_type)[0:len(c)]) == c:
                    context_frs[c] += word.frequency
    return context_frs


def conditional_probability(segment_frs, context_frs, stop_check=None, call_back=None):
    """Gets the conditional probability of a segment occurring in a given context.

    Parameters
    ----------
    segment_frs: dict {Segment : int, ...}
        Dictionary of segment frequencies, specifically {Segment : frequency of segment|context ,...}
    context_frs: dict {Segment : int, ...}
        Dictionary of context frequencies, specifically {Segment : frequency of context|segment ,...}

    Returns
    ----------
    dict {tuple:float,...}
        Dictionary with tuple of context Segments as key, and float of conditional probability
         of the given Segment occurring in that context
    """
    if call_back is not None:
        call_back('Calculating informativity...')
        call_back(0, -1)
        cur = 0
    conditional_prs = defaultdict(float)
    for c in segment_frs:
        if stop_check is not None and stop_check():
            return 'quit'
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        if context_frs[c] != 0:
            conditional_prs[c] = segment_frs[c] / context_frs[c]
        else:
            conditional_prs[c] = segment_frs[c]
    return conditional_prs

def get_multiple_informativity(corpus, segment_list, sequence_type = 'transcription', rounding=3, type_or_token='token',
                               call_back = None, stop_check=None):
    # s_frs = segment_in_context_frequencies(segment, corpus_context, sequence_type)
    # seg_frequencies = {seg:segment_in_context_frequencies(seg, corpus, sequence_type) for seg in segment_list}
    seg_frequencies = {seg:defaultdict(int) for seg in segment_list}
    context_frequencies = {seg:defaultdict(int) for seg in segment_list}
    seg_conditional_probs = {seg:defaultdict(float) for seg in segment_list}
    corpus_size = len(corpus)
    if call_back is not None:
        call_back('Calculating segment frequencies...')
        call_back(0, corpus_size)
        cur = 0
    for word in corpus:
        i = 0
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)

        for seg in getattr(word, sequence_type):
            i += 1
            if seg in segment_list:
                if type_or_token == 'token':
                    seg_frequencies[seg][context(i, word, sequence_type)] += word.frequency
                else:
                    seg_frequencies[seg][context(i, word, sequence_type)] += 1

    if call_back is not None:
        call_back('Calculating context frequencies...')
        call_back(0, corpus_size)
        cur = 0
    for word in corpus:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        for seg in segment_list:
            for c in seg_frequencies[seg]:
                if c is not None:
                    if tuple(getattr(word, sequence_type)[0:len(c)]) == c:
                        if type_or_token == 'token':
                            context_frequencies[seg][c] += word.frequency
                        else:
                            context_frequencies[seg][c] += 1

    if call_back is not None:
        call_back('Calculating context frequencies...')
        call_back(0, len(segment_list))
        cur = 0
    for seg in segment_list:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        seg_conditional_probs[seg] = conditional_probability(seg_frequencies[seg], context_frequencies[seg])
        if not seg_conditional_probs[seg]:
            seg_conditional_probs[seg] = 0

    if call_back is not None:
        call_back('Calculating informativity...')
        call_back(0, len(segment_list))
        cur = 0
    seg_summary = list()
    for seg in segment_list:
        if call_back is not None:
            cur += 1
            if cur % 100 == 0:
                call_back(cur)
        informativity = calculate_informativity(seg_frequencies[seg], seg_conditional_probs[seg], rounding)
        summary = {
            "Corpus": corpus.name,
            "Segment": seg,
            "Informativity": informativity,
            "Context": "all",
            "Rounding": rounding,
            "Type or token": type_or_token,
            "Transcription tier": sequence_type,
            "Pronunciation variants": None}

        seg_summary.append(summary)

    return seg_summary


def get_informativity(corpus_context, segment, sequence_type = 'transcription', rounding=3,
                      stop_check=None, call_back=None):
    """Calculate the informativity of one segment. 

    Parameters
    ----------
    corpus_context: CorpusContext
        Context manager for a corpus
    segment: Segment 
        The Segment for which informativity should be calculated
    rounding: int 
        Integer indicates the number of decimal places

    Returns
    ----------
    dict 
        Dictionary provides a summary of the parameters, with string keys. Value
        for informativity is a float with specified rounding
    """
    s_frs = segment_in_context_frequencies(segment, corpus_context, sequence_type, stop_check, call_back)
    if s_frs == 'quit':
        return
    c_frs = context_frequencies(s_frs, corpus_context, sequence_type, stop_check, call_back)
    if c_frs == 'quit':
        return
    c_prs = conditional_probability(s_frs, c_frs, stop_check, call_back)
    if c_prs == 'quit':
        return
    informativity = calculate_informativity(s_frs, c_prs, rounding)

    summary = {
        "Corpus": corpus_context.name,
        "Segment": segment,
        "Context": "all",
        "Rounding": rounding,
        "Informativity": informativity
    }
    return summary

def calculate_informativity(s_frs, c_prs, rounding):
    informativity=round(-(sum([(s_frs[c]) * log2(c_prs[c]) for c in c_prs]))/sum([(s_frs[s]) for s in s_frs]), rounding)
    if informativity is -0.0:
        informativity = 0.0
    return informativity


def all_informativity(corpus_context, rounding=3):
    """

    Parameters
    ----------
    corpus_context: CorpusContext
        Context manager for a corpus
    rounding: int 
        Integer indicates the number of decimal places

    Returns
    ----------
    dict {Segment: dict, ...}
        Dictionary of dictionaries containing informativity summaries, 
        with Segment objects as keys. 
    """
    all_informativities = defaultdict(dict)
    for segment in corpus_context.inventory:
        all_informativities[str(segment)] = get_informativity(corpus_context, segment, rounding)
    return all_informativities


if __name__ == '__main__':
    # ------------------------------------------------------------------#
    # TESTING
    # The following code will not be included in the actual PCT release,
    # and is here for the purposes of testing for the LIBR 559C project.
    # All testing is done with the Lemurian corpus - lemurian.corpus
    # ------------------------------------------------------------------#

    # Additional imports for testing purposes
    import pickle
    from corpustools.corpus.classes import Segment

    # Load the corpus
    corpus_path = "lemurian.corpus"
    with open(corpus_path, 'rb') as file:
        corpus_in = pickle.load(file)

    # Corpus information
    print("Corpus: ", corpus_in.name)
    print("Segments in the lemurian corpus: ", [seg for seg in corpus_in.inventory], "\n")

    # Informativity of a single segment
    print("Informativity for one segment:")
    print(get_informativity(corpus_in, Segment("m"), rounding=3), "\n")

    # Informativity for all segments in inventory
    print("Informativity for all segments in inventory:")
    output = all_informativity(corpus_in, rounding=4)
    for s in sorted(output.keys()):
        print(s, output[s])
    #remove ROUNDING from output, since this is already handled in PCT's global settings