import os

from corpustools.corpus.classes import Corpus, Word, Discourse, WordToken

from .csv import DelimiterError
from .binary import load_binary

def load_spelling_corpus(corpus_name, path, delimiter, ignore_list,
                            ignore_case = False,
                            support_corpus_path = None, stop_check = None,
                            call_back = None):
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

    discourse = Discourse(name = corpus_name)
    if support_corpus_path is not None:
        if not os.path.exists(support_corpus_path):
            raise(OSError("The corpus path specified ({}) does not exist".format(support_corpus_path)))
        support = load_binary(support_corpus_path)
    corpus = Corpus(corpus_name)

    with open(path, encoding='utf-8-sig', mode='r') as f:
        text = f.read()
        if delimiter is not None and delimiter not in text:
            e = DelimiterError('The delimiter specified does not create multiple words. Please specify another delimiter.')
            raise(e)

        lines = text.splitlines()
        if call_back is not None:
            call_back('Processing file...')
            call_back(0,len(lines))
            cur = 0
        begin = 0
        previous_time = None

        for line in lines:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            if not line or line == '\n':
                continue
            line = line.split(delimiter)
            for word in line:
                spell = word.strip()
                spell = ''.join(x for x in spell if not x in ignore_list)
                if spell == '':
                    continue
                trans = None
                if support_corpus_path is not None:
                    try:
                        trans = support.find(spell, ignore_case = ignore_case).transcription
                    except KeyError:
                        pass
                word = corpus.get_or_create_word(spell, trans)
                word.frequency += 1
                if previous_time is not None:
                    wordtoken = WordToken(word=word,
                                    begin = begin, end = begin + 1,
                                    previous_token = discourse[previous_time])
                else:
                    wordtoken = WordToken(word=word,
                                    begin = begin, end = begin + 1)
                word.wordtokens.append(wordtoken)
                discourse.add_word(wordtoken)
                if previous_time is not None:
                    discourse[previous_time].following_token_time = wordtoken.begin

                previous_time = wordtoken.begin
                begin += 1
    discourse.lexicon = corpus

    return discourse
