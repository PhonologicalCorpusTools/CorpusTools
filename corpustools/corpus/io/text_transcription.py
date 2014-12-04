import os
import re

from corpustools.corpus.classes import Corpus, Word

from .csv import DelimiterError

from .binary import load_binary

def load_transcription_corpus(corpus_name, path, delimiter, ignore_list, digraph_list = None,
                    trans_delimiter = None,feature_system_path = None,
                    stop_check = None, call_back = None, pqueue = None, oqueue = None):
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

    trans_delimiter : str
        Character to use for splitting transcriptions into a list
        of segments. If it equals '', each character in the transcription
        is interpreted as a segment.  Defaults to '.'

    feature_system_path : str
        Full path to pickled FeatureMatrix to use with the Corpus

    string_type : str
        Specifies whether text files contains spellings or transcriptions.
        Defaults to 'spelling'


    Returns
    -------
    Corpus
        Corpus object generated from the text file

    dictionary
        Dictionary with segments not in the FeatureMatrix (if specified)
        as keys and a list of words containing those segments as values

    """
    corpus = Corpus(corpus_name)
    corpus.custom = True
    if digraph_list is not None:
        pattern = '|'.join(d for d in digraph_list)
        pattern += '|\w'
        digraph_re = re.compile(pattern)

    if feature_system_path is not None:
        if not os.path.exists(feature_system_path):
            raise(OSError("The feature path specified ({}) does not exist".format(feature_system_path)))
        feature_matrix = load_binary(feature_system_path)
        corpus.set_feature_matrix(feature_matrix)

    trans_check = False
    with open(path, encoding='utf-8-sig', mode='r') as f:
        text = f.read()
        if delimiter not in text:
            e = DelimiterError('The delimiter specified does not create multiple words. Please specify another delimiter.')
            if pqueue is not None:
                pqueue.put(e)
            else:
                raise(e)

        for line in text.splitlines():
            if not line or line == '\n':
                continue
            line = line.split(delimiter)

            for word in line:
                word = word.strip()
                if trans_delimiter is not None:
                    trans = word.split(trans_delimiter)
                    if not trans_check and len(trans) > 1:
                        trans_check = True
                elif digraph_list is not None:
                    trans = digraph_re.findall(word)
                trans = [x for x in trans if not x in ignore_list]
                spell = ''.join(trans)
                d = {'spelling': spell, 'transcription': trans}
                word = Word(**d)
                corpus.add_word(word, allow_duplicates=False)
                corpus[word.spelling].frequency += 1
    if not trans_check:
        raise(DelimiterError('The transcription delimiter specified does not create multiple segments. Please specify another delimiter.'))
    transcription_errors = corpus.check_coverage()
    if pqueue is not None:
        pqueue.put(-99)
    if oqueue is not None:
        oqueue.put(corpus)
        oqueue.put(transcription_errors)
    else:
        return corpus
