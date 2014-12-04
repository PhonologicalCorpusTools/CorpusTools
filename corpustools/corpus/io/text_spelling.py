

from corpustools.corpus.classes import Corpus, Word

from .csv import DelimiterError

def load_spelling_corpus(corpus_name, path, delimiter, ignore_list,
                            support_corpus_path = None):
    """
    Load a corpus from a text file containing running text either in
    orthography or transcription

    Attributes
    ----------
    corpus_name : str
        Informative identifier to refer to corpus

    path : str
        Full path to text file

    delimiter : str
        Character to use for spliting text into words

    ignore_list : list of strings
        List of characters to ignore when parsing the text


    Returns
    -------
    Corpus
        Corpus object generated from the text file

    dictionary
        Dictionary with segments not in the FeatureMatrix (if specified)
        as keys and a list of words containing those segments as values

    """
    corpus = Corpus(corpus_name)
    if support_corpus_path is not None:
        if not os.path.exists(support_corpus_path):
            raise(OSError("The corpus path specified ({}) does not exist".format(support_corpus_path)))
        support = load_binary(support_corpus_path)

    with open(path, encoding='utf-8-sig', mode='r') as f:
        text = f.read()
        if delimiter not in text:
            e = DelimiterError('The delimiter specified does not create multiple words. Please specify another delimiter.')
            raise(e)

        for line in text.splitlines():
            if not line or line == '\n':
                continue
            line = line.split(delimiter)

            for word in line:
                spell = word.strip()
                spell = ''.join(x for x in spell if not x in ignore_list)
                trans = None
                if support_corpus_path:
                    try:
                        trans = support.find(spell).transcription
                    except KeyError:
                        pass
                d = {'spelling': spell, 'transcription': trans}
                word = Word(**d)
                corpus.add_word(word, allow_duplicates=False)
                corpus[word.spelling].frequency += 1

    return corpus
