import os

from corpustools.corpus.classes import Corpus, Word, Discourse, WordToken

from corpustools.exceptions import DelimiterError, PCTOSError
from .binary import load_binary

from .helper import compile_digraphs, parse_transcription, DiscourseData,data_to_discourse, AnnotationType,text_to_lines

def inspect_discourse_spelling(path, support_corpus_path = None):
    annotation_types = [AnnotationType('spelling', None, None, anchor = True, token = False)]
    if support_corpus_path is not None:
        annotation_types += [AnnotationType('transcription', None, None, base = True)]
    return annotation_types

def spelling_text_to_data(path, delimiter, ignore_list, annotation_types = None,
                            support_corpus_path = None, ignore_case = True,
                            stop_check = None, call_back = None):

    name = os.path.splitext(os.path.split(path)[1])[0]
    if support_corpus_path is not None:
        if not os.path.exists(support_corpus_path):
            raise(PCTOSError("The corpus path specified ({}) does not exist".format(support_corpus_path)))
        support = load_binary(support_corpus_path)
    if annotation_types is None:
        annotation_types = inspect_discourse_spelling(path, support_corpus_path)
    data = DiscourseData(name, annotation_types)

    lines = text_to_lines(path, delimiter)
    if call_back is not None:
        call_back('Processing file...')
        call_back(0,len(lines))
        cur = 0

    for line in lines:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 20 == 0:
                call_back(cur)
        if not line or line == '\n':
            continue
        annotations = dict()
        for word in line:
            spell = word.strip()
            spell = ''.join(x for x in spell if not x in ignore_list)
            if spell == '':
                continue
            word = {'label':spell, 'token':dict()}
            if support_corpus_path is not None:
                trans = None
                try:
                    trans = support.find(spell, ignore_case = ignore_case).transcription
                except KeyError:
                    trans = list()
                n = data.base_levels[0]
                tier_elements = [{'label':x} for x in trans]
                level_count = data.level_length(n)
                word[n] = (level_count,level_count+len(tier_elements))
                annotations[n] = tier_elements
            annotations['spelling'] = [word]
            data.add_annotations(**annotations)

    return data

def load_discourse_spelling(corpus_name, path, delimiter, ignore_list, annotation_types = None,
                            support_corpus_path = None, ignore_case = False,
                            stop_check = None, call_back = None):
    """
    Load a corpus from a text file containing running text of
    orthography

    Parameters
    ----------
    corpus_name : str
        Informative identifier to refer to corpus

    path : str
        Full path to text file

    delimiter : str
        Character to use for spliting text into words

    ignore_list : list of strings
        List of characters to ignore when parsing the text

    support_corpus_path : string
        Full path to a corpus to look up transcriptions from spellings
        in the text

    ignore_case : bool
        Specify whether to ignore case when using spellings in the text
        to look up transcriptions

    stop_check : callable
        Callable that returns a boolean for whether to exit before
        finishing full calculation

    call_back : callable
        Function that can handle strings (text updates of progress),
        tuples of two integers (0, total number of steps) and an integer
        for updating progress out of the total set by a tuple

    Returns
    -------
    Discourse
        Discourse object generated from the text file

    """

    data = spelling_text_to_data(path, delimiter, ignore_list, annotation_types,
                support_corpus_path, ignore_case,
                    stop_check, call_back)
    mapping = { x.name: x.attribute for x in data.data.values()}
    discourse = data_to_discourse(data, mapping)
    return discourse

def export_discourse_spelling(discourse, path, single_line = False):
    with open(path, encoding='utf-8', mode='w') as f:
        count = 0
        for i, wt in enumerate(discourse):
            count += 1
            f.write(wt.spelling)
            if i != len(discourse) -1:
                if not single_line and count <= 10:
                    f.write(' ')
                else:
                    count = 0
                    f.write('\n')
