
def edit_distance(w1, w2, string_type):
    """Returns the Levenshtein edit distance between two strings s1 and s2, code drawn from http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python.
    The number is the number of operations needed to transform s1 into s2, three operations are possible: insert, delete, substitute

    Parameters
    ----------
    s1: Word
        the first word object to be compared
    s2: Word
        the second word object to be compared

    Returns
    -------
    int:
        the edit distance between two strings
    """
    s1 = getattr(w1, string_type)
    s2 = getattr(w2, string_type)

    if len(s1) >= len(s2):
        longer = s1
        shorter = s2
    else:
        longer = s2
        shorter = s1


    previous_row = range(len(shorter) + 1)
    for i, c1 in enumerate(longer):
        current_row = [i + 1]
        for j, c2 in enumerate(shorter):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

