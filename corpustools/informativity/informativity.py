from math import log2
from collections import defaultdict


def context(index, word):
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
    return tuple(word.transcription[0:index - 1])


def segment_in_context_frequencies(segment, corpus_context):
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
    contexts = defaultdict(int)
    for word in corpus_context:
        i = 0
        for seg in word.transcription:
            i += 1
            if seg == segment:
                contexts[context(i, word)] += word.frequency
    return contexts


def context_frequencies(contexts, corpus_context):
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
    context_frs = defaultdict(int)
    for c in contexts:
        if c is not None:
            for word in corpus_context:
                if tuple(word.transcription[0:len(c)]) == c:
                    context_frs[c] += word.frequency
    return context_frs


def conditional_probability(segment_frs, context_frs):
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
    conditional_prs = defaultdict(float)
    for c in segment_frs:
        if context_frs[c] != 0:
            conditional_prs[c] = segment_frs[c] / context_frs[c]
        else:
            conditional_prs[c] = segment_frs[c]
    return conditional_prs


def get_informativity(corpus_context, segment, rounding=3):
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
    s_frs = segment_in_context_frequencies(segment, corpus_context)
    c_frs = context_frequencies(s_frs, corpus_context)
    c_prs = conditional_probability(s_frs, c_frs)
    informativity = round(-(sum([(s_frs[c]) * log2(c_prs[c]) for c in c_prs])) / sum([(s_frs[s]) for s in s_frs]),
                          rounding)

    summary = {
        "Corpus": corpus_context.name,
        "Segment": segment,
        "Context": "all",
        "Rounding": rounding,
        "Informativity": informativity
    }
    return summary


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