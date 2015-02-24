import os
import re

from corpustools.corpus.classes import Corpus, Word, Discourse, WordToken

from corpustools.exceptions import DelimiterError

from .binary import load_binary

def inspect_transcription_corpus(path):
    characters = set()
    with open(path, encoding='utf-8-sig', mode='r') as f:
        for line in f.readlines():
            characters.update(line)
    return characters

def load_transcription_corpus(corpus_name, path, delimiter, ignore_list, digraph_list = None,
                    trans_delimiter = None,feature_system_path = None,
                    stop_check = None, call_back = None):
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
    discourse = Discourse(name = corpus_name)
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
    if trans_delimiter is None:
        trans_delimiter = []
    trans_patt = ''.join([re.escape(x) for x in trans_delimiter])
    trans_patt = '['+trans_patt+']+'
    with open(path, encoding='utf-8-sig', mode='r') as f:
        text = f.read()
        if delimiter and delimiter not in text:
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
                word = word.strip()
                if trans_delimiter:
                    word = re.sub('^'+trans_patt,'',word)
                    word = re.sub(trans_patt+'$','',word)
                    trans = re.split(trans_patt,word)
                    if not trans_check and len(trans) > 1:
                        trans_check = True
                elif digraph_list and len(word) > 1:
                    trans = digraph_re.findall(word)
                else:
                    trans = list(word)
                trans = [x for x in trans if not x in ignore_list and x != '']
                spell = ''.join(trans)
                if spell == '':
                    continue
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
    if trans_delimiter and not trans_check:
        raise(DelimiterError('The transcription delimiter specified does not create multiple segments. Please specify another delimiter.'))

    discourse.lexicon = corpus
    return discourse
