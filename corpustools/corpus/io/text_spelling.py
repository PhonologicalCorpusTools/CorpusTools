import os

from corpustools.corpus.classes import SpontaneousSpeechCorpus, Discourse, Attribute, Corpus

from corpustools.exceptions import PCTOSError
from .binary import load_binary

from .helper import (DiscourseData, Annotation, BaseAnnotation,
                     data_to_discourse, data_to_discourse2, AnnotationType, text_to_lines)

def inspect_discourse_spelling(path, support_corpus_path = None):
    """
    Generate a list of AnnotationTypes for a specified text file for parsing
    it as an orthographic text

    Parameters
    ----------
    path : str
        Full path to text file
    support_corpus_path : str, optional
        Full path to a corpus to look up transcriptions from spellings
        in the text

    Returns
    -------
    list of AnnotationTypes
        Autodetected AnnotationTypes for the text file
    """
    a = AnnotationType('Spelling', None, None, anchor = True, token = False)
    if os.path.isdir(path):
        for root, subdirs, files in os.walk(path):
            for filename in files:
                if not filename.lower().endswith('.txt'):
                    continue
                with open(os.path.join(root,filename),
                            encoding='utf-8-sig', mode='r') as f:
                    for line in f.readlines():
                        trial = line.strip().split()

                        a.add(trial, save = False)
    else:
        with open(path, encoding='utf-8-sig', mode='r') as f:
            for line in f.readlines():
                trial = line.strip().split()

                a.add(trial, save = False)
    annotation_types = [a]
    if support_corpus_path is not None:
        annotation_types += [AnnotationType('Transcription', None, None, base = True)]
    return annotation_types

def spelling_text_to_data(corpus_name, path, annotation_types = None,
                            support_corpus_path = None, ignore_case = True,
                            stop_check = None, call_back = None):
    name = corpus_name
    if annotation_types is None:
        annotation_types = inspect_discourse_spelling(path, support_corpus_path)

    if support_corpus_path is not None:
        if isinstance(support_corpus_path, Corpus):
            support = support_corpus_path
        else:
            if not os.path.exists(support_corpus_path):
                raise(PCTOSError("The corpus path specified ({}) does not exist".format(support_corpus_path)))
            support = load_binary(support_corpus_path)

        a = AnnotationType('Transcription', None, None,
                           attribute=Attribute('Transcription', 'transcription', 'Transcription'),
                           base=True, is_default=True)
        annotation_types.append(a)

    for a in annotation_types:
        a.reset()

    data = DiscourseData(name, annotation_types)

    lines = text_to_lines(path)
    if call_back is not None:
        call_back('Processing file...')
        call_back(0, len(lines))
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
        annotations = {}
        for word in line:
            spell = word.strip()
            spell = ''.join(x for x in spell if not x in data['Spelling'].ignored_characters)
            if spell == '':
                continue
            word = Annotation(spell)
            if support_corpus_path is not None:
                trans = None
                try:
                    trans = support.find(spell, ignore_case = ignore_case).transcription
                except KeyError:
                    trans = []
                n = data.base_levels[0]
                tier_elements = [BaseAnnotation(x) for x in trans]
                level_count = data.level_length(n)
                word.references.append(n)
                word.begins.append(level_count)
                word.ends.append(level_count + len(tier_elements))
                annotations[n] = tier_elements
            annotations['Spelling'] = [word]
            data.add_annotations(**annotations)

    return data

def load_directory_spelling(corpus_name, path, annotation_types = None,
                            support_corpus_path = None, ignore_case = False,
                            stop_check = None, call_back = None):
    """
    Loads a directory of orthographic texts

    Parameters
    ----------
    corpus_name : str
        Name of corpus
    path : str
        Path to directory of text files
    annotation_types : list of AnnotationType, optional
        List of AnnotationType specifying how to parse text files
    support_corpus_path : str, optional
        File path of corpus binary to load transcriptions from
    ignore_case : bool, optional
        Specifies whether lookups in the support corpus should ignore case
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    SpontaneousSpeechCorpus
        Corpus containing Discourses corresponding to the text files
    """
    if call_back is not None:
        call_back('Finding files...')
        call_back(0, 0)
    file_tuples = []
    for root, subdirs, files in os.walk(path):
        for filename in files:
            if not filename.lower().endswith('.txt'):
                continue
            file_tuples.append((root, filename))

    if call_back is not None:
        call_back('Parsing files...')
        call_back(0,len(file_tuples))
        cur = 0
    corpus = SpontaneousSpeechCorpus(corpus_name, path)
    if support_corpus_path is not None:
        support = load_binary(support_corpus_path)
    else:
        support = None
    for i, t in enumerate(file_tuples):
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            call_back('Parsing file {} of {}...'.format(i+1, len(file_tuples)))
            call_back(i)
        root, filename = t
        name = os.path.splitext(filename)[0]
        at = annotation_types[:]
        #it's necessary to take a copy, because the annotation types might be altered during the load_discourse_spelling
        #function, and if so this affect the annotation types on future loops in the current function
        d = load_discourse_spelling(name, os.path.join(root,filename),
                                    annotation_types=at,
                                    support_corpus_path = support, ignore_case = ignore_case,
                                    stop_check = stop_check, call_back = call_back)
        corpus.add_discourse(d)
    return corpus

def load_discourse_spelling(corpus_name, path, annotation_types = None,
                            support_corpus_path = None, ignore_case = False,
                            stop_check = None, call_back = None):
    """
    Load a discourse from a text file containing running text of
    orthography

    Parameters
    ----------
    corpus_name : str
        Informative identifier to refer to corpus

    path : str
        Full path to text file
    annotation_types : list of AnnotationType, optional
        List of AnnotationType specifying how to parse text files
    lexicon : Corpus, optional
        Corpus to store Discourse word information
    support_corpus_path : str, optional
        Full path to a corpus to look up transcriptions from spellings
        in the text
    ignore_case : bool, optional
        Specify whether to ignore case when using spellings in the text
        to look up transcriptions
    stop_check : callable, optional
        Callable that returns a boolean for whether to exit before
        finishing full calculation
    call_back : callable, optional
        Function that can handle strings (text updates of progress),
        tuples of two integers (0, total number of steps) and an integer
        for updating progress out of the total set by a tuple

    Returns
    -------
    Discourse
        Discourse object generated from the text file
    """

    data = spelling_text_to_data(corpus_name, path, annotation_types,
                support_corpus_path, ignore_case,
                stop_check, call_back)

    if data is None:
        return

    if support_corpus_path is not None:
        if isinstance(support_corpus_path, Corpus):
            #the corpus is 'preloaded' if this function is called by load_directory_spelling
            #otherwise the corpus has to be loaded once per file in a directory, which could be slow
            support = support_corpus_path
        else:
            #otherwise, it's a string representing a path to the corpus
            support = load_binary(support_corpus_path)
    else:
        support = None

    #discourse = data_to_discourse(data, lexicon, stop_check=stop_check, call_back=call_back)
    discourse = data_to_discourse2(corpus_name=data.name, wav_path=data.wav_path, annotation_types=annotation_types,
                                   support_corpus=support, ignore_case=ignore_case,
                                   stop_check=stop_check, call_back=call_back)
    if support_corpus_path is not None:
        discourse.lexicon.specifier = support.specifier

    return discourse


def export_discourse_spelling(discourse, path, single_line = False):
    """
    Export an orthography discourse to a text file

    Parameters
    ----------
    discourse : Discourse
        Discourse object to export
    path : str
        Path to export to
    single_line : bool, optional
        Flag to enforce all text to be on a single line, defaults to False.
        If False, lines are 10 words long.
    """
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
