from corpustools.corpus.classes import Word
#from corpustools.symbolsim.phono_align import Aligner

#al = Aligner(features_tf=False)

#def edit_distance(word1, word2, sequence_type):
    #"""Returns the Levenshtein edit distance between a string from
     #two words word1 and word2.

     #The edit distance is the number of operations needed to transform word1 into word2,
     #three operations are possible: insert, delete, substitute

     #Parameters
     #----------
     #word1: Word
         #the first word object to be compared

     #word2: Word
         #the second word object to be compared

     #sequence_type : string
         #String specifying what attribute of the Word objects to compare,
         #can be "spelling", "transcription" or a tier name

     #Returns
     #-------
     #int:
         #the edit distance between two words
     #"""
    #m = al.make_similarity_matrix(getattr(word1, sequence_type), getattr(word2, sequence_type))
    #return m[-1][-1]['f']

#def edit_distance(word1, word2, sequence_type):
    #"""Returns the Levenshtein edit distance between a string from
     #two words word1 and word2.

     #The edit distance is the number of operations needed to transform word1 into word2,
     #three operations are possible: insert, delete, substitute

     #Parameters
     #----------
     #word1: Word
         #the first word object to be compared

     #word2: Word
         #the second word object to be compared

     #sequence_type : string
         #String specifying what attribute of the Word objects to compare,
         #can be "spelling", "transcription" or a tier name

     #Returns
     #-------
     #int:
         #the edit distance between two words
     #"""
    #m = al.make_similarity_matrix(getattr(word1, sequence_type), getattr(word2, sequence_type))
    #return m[-1][-1]['f']

def edit_distance(word1, word2, sequence_type, max_distance = None):
    """Returns the Levenshtein edit distance between a string from
    two words word1 and word2, code drawn from
    http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python.
    The number is the number of operations needed to transform word1 into word2,
    three operations are possible: insert, delete, substitute

    Parameters
    ----------
    word1: Word
        the first word object to be compared
    word2: Word
        the second word object to be compared
    string_type : string
        String specifying what attribute of the Word objects to compare,
        can be "spelling", "transcription" or a tier

    Returns
    -------
    int:
        the edit distance between two words
    """
    s1 = word1
    s2 = word2

    longer, shorter = (s1,s2) if len(s1) > len(s2) else (s2,s1)

    previous_row = range(len(shorter) + 1)
    for i, c1 in enumerate(longer):
        current_row = [i + 1]
        for j, c2 in enumerate(shorter):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        #if max_distance is not None and previous_row[-1] > max_distance:
        #    break
    return previous_row[-1]

