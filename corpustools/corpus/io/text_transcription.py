import os
import re

from corpustools.corpus.classes import SpontaneousSpeechCorpus, Corpus, Word, Discourse, WordToken, Attribute

from corpustools.exceptions import DelimiterError, PCTOSError

from .helper import (compile_digraphs, parse_transcription, DiscourseData,
                    data_to_discourse, AnnotationType, text_to_lines,
                    Annotation, BaseAnnotation)

from .binary import load_binary

def inspect_discourse_transcription(path):
    trans_delimiters = ['.', ';', ',']

    att = Attribute('transcription','tier','Transcription')
    a = AnnotationType('transcription', None, None, attribute = att,
                                            base = True)

    if os.path.isdir(path):
        for root, subdirs, files in os.walk(path):
            for filename in files:
                if not filename.lower().endswith('.txt'):
                    continue
                with open(os.path.join(root,filename),
                            encoding='utf-8-sig', mode='r') as f:
                    for line in f.readlines():
                        trial = line.strip().split()
                        if a.trans_delimiter is None:
                            for t in trial:
                                for delim in trans_delimiters:
                                    if delim in t:
                                        a.trans_delimiter = delim
                                        break

                        a.add(trial, save = False)
    else:
        with open(path, encoding='utf-8-sig', mode='r') as f:
            for line in f.readlines():
                trial = line.strip().split()
                if a.trans_delimiter is None:
                    for t in trial:
                        for delim in trans_delimiters:
                            if delim in t:
                                a.trans_delimiter = delim
                                break

                a.add(trial, save = False)
    annotation_types = [a]
    return annotation_types

def transcription_text_to_data(path, annotation_types = None,
                            stop_check = None, call_back = None):


    name = os.path.splitext(os.path.split(path)[1])[0]

    if annotation_types is None:
        annotation_types = inspect_discourse_transcription(path)

    for a in annotation_types:
        a.reset()
    a = AnnotationType('spelling', None, None,
                attribute = Attribute('spelling','spelling','Spelling'),
                                            anchor = True)
    annotation_types.append(a)

    data = DiscourseData(name, annotation_types)

    lines = text_to_lines(path)
    if call_back is not None:
        call_back('Processing file...')
        call_back(0, len(lines))
        cur = 0
    trans_check = False
    n = 'transcription'

    for line in lines:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 20 == 0:
                call_back(cur)
        if not line or line == '\n':
            continue
        for word in line:
            annotations = dict()
            trans = parse_transcription(word, data[n].delimiter,
                            data[n].digraph_pattern, data[n].ignored)
            #if not trans_check and data[n].delimiter is not None and len(trans) > 1:
            #    trans_check = True
            spell = ''.join(trans)
            if spell == '':
                continue

            word = Annotation(spell)

            tier_elements = [BaseAnnotation(x) for x in trans]
            level_count = data.level_length(n)
            word.references.append(n)
            word.begins.append(level_count)
            word.ends.append(level_count + len(tier_elements))
            annotations[n] = tier_elements
            annotations['spelling'] = [word]
            data.add_annotations(**annotations)
    #if data[n].delimiter and not trans_check:
    #    raise(DelimiterError('The transcription delimiter specified does not create multiple segments. Please specify another delimiter.'))

    return data

def load_directory_transcription(corpus_name, path, annotation_types = None,
                                feature_system_path = None,
                                stop_check = None, call_back = None):
    if call_back is not None:
        call_back('Finding  files...')
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
    for i, t in enumerate(file_tuples):
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            call_back('Parsing file {} of {}...'.format(i+1,len(file_tuples)))
            call_back(i)
        root, filename = t
        name = os.path.splitext(filename)[0]
        d = load_discourse_transcription(name, os.path.join(root,filename),
                                    annotation_types,
                                    corpus.lexicon, None,
                                    stop_check, call_back)
        corpus.add_discourse(d)
    return corpus


def load_discourse_transcription(corpus_name, path, annotation_types = None,
                    lexicon = None, feature_system_path = None,
                    stop_check = None, call_back = None):
    """
    Load a corpus from a text file containing running transcribed text

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

    digraph_list : list of strings
        List of digraphs (sequences of two characters that should be
        treated as a single segment) to use when reading transcriptions

    trans_delimiter : str
        Character to use for splitting transcriptions into a list
        of segments. If it equals '', each character in the transcription
        is interpreted as a segment.  Defaults to '.'

    feature_system_path : str
        Full path to pickled FeatureMatrix to use with the Corpus

    string_type : str
        Specifies whether text files contains spellings or transcriptions.
        Defaults to 'spelling'

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
        Discourse  object generated from the text file

    """

    if feature_system_path is not None:
        if not os.path.exists(feature_system_path):
            raise(PCTOSError("The feature path specified ({}) does not exist".format(feature_system_path)))

    data = transcription_text_to_data(path, annotation_types,
                            stop_check, call_back)

    discourse = data_to_discourse(data, lexicon)

    if feature_system_path is not None:
        feature_matrix = load_binary(feature_system_path)
        discourse.lexicon.set_feature_matrix(feature_matrix)

    return discourse

def export_discourse_transcription(discourse, path, trans_delim = '.', single_line = False):
    with open(path, encoding='utf-8', mode='w') as f:
        count = 0
        for i, wt in enumerate(discourse):
            count += 1
            f.write(trans_delim.join(wt.transcription))
            if i != len(discourse) -1:
                if not single_line and count <= 10:
                    f.write(' ')
                else:
                    count = 0
                    f.write('\n')
