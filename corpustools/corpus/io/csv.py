from csv import DictReader, DictWriter
import collections
import re
import os

from corpustools.corpus.classes import Corpus, FeatureMatrix, Word, Attribute
from corpustools.corpus.io.binary import save_binary, load_binary

from .helper import parse_transcription, AnnotationType

from corpustools.exceptions import DelimiterError, PCTError

import time

def inspect_csv(path, num_lines = 10, coldelim = None, transdelim = None):
    if coldelim is not None:
        common_delimiters = [coldelim]
    else:
        common_delimiters = [',','\t',':','|']
    if transdelim is not None:
        trans_delimiters = [transdelim]
    else:
        trans_delimiters = ['.',' ', ';', ',']

    with open(path,'r', encoding='utf-8') as f:
        lines = []
        head = f.readline().strip()
        for line in f.readlines():
            lines.append(line.strip())
        #for i in range(num_lines):
        #    line = f.readline()
        #    if not line:
        #        break
        #    lines.append(line)

    best = ''
    num = 1
    for d in common_delimiters:
        trial = len(head.split(d))
        if trial > num:
            num = trial
            best = d
    if best == '':
        raise(DelimiterError('The column delimiter specified did not create multiple columns.'))

    head = head.split(best)
    vals = {h: list() for h in head}

    for line in lines:
        l = line.strip().split(best)
        if len(l) != len(head):
            raise(PCTError('{}, {}'.format(l,head)))
        for i in range(len(head)):
            vals[head[i]].append(l[i])
    atts = list()
    for h in head:
        cat = Attribute.guess_type(vals[h][:num_lines], trans_delimiters)
        att = Attribute(Attribute.sanitize_name(h), cat, h)
        a = AnnotationType(h, None, None, token = False, attribute = att)
        if cat == 'tier':
            for t in trans_delimiters:
                if t in vals[h][0]:
                    a.trans_delimiter = t
                    break
        a.add(vals[h], save = False)
        atts.append(a)

    return atts, best

def load_corpus_csv(corpus_name, path, delimiter,
                    feature_system_path = None,
                    annotation_types = None,
                    stop_check = None, call_back = None):
    """
    Load a corpus from a column-delimited text file

    Parameters
    ----------
    corpus_name : str
        Informative identifier to refer to corpus

    path : str
        Full path to text file

    delimiter : str
        Character to use for spliting lines into columns

    trans_delimiter : str
        Character to use for splitting transcriptions into a list
        of segments. If it equals '', each character in the transcription
        is interpreted as a segment.  Defaults to '.'

    feature_system_path : str
        Full path to pickled FeatureMatrix to use with the Corpus

    Returns
    -------
    Corpus
        Corpus object generated from the text file

    """
    #begin = time.time()
    corpus = Corpus(corpus_name)
    if feature_system_path is not None and os.path.exists(feature_system_path):
        feature_matrix = load_binary(feature_system_path)
        corpus.set_feature_matrix(feature_matrix)

    if annotation_types is None:
        annotation_types, _ = inspect_csv(path, coldelim = delimiter)

    with open(path, encoding='utf-8') as f:
        headers = f.readline()
        headers = headers.split(delimiter)
        if len(headers)==1:
            e = DelimiterError(('Could not parse the corpus.\n\Check '
                                'that the delimiter you typed in matches '
                                'the one used in the file.'))
            raise(e)

        headers = [h.strip() for h in headers]
        headers[0] = headers[0].strip('\ufeff')
        if 'feature_system' in headers[-1]:
            headers = headers[0:len(headers)-1]
        headers = annotation_types
        for a in headers:
            corpus.add_attribute(a.attribute)
        trans_check = False

        for line in f.readlines():
            line = line.strip()
            if not line: #blank or just a newline
                continue
            d = {}
            for k,v in zip(headers,line.split(delimiter)):
                v = v.strip()
                if k.attribute.att_type == 'tier':
                    trans = parse_transcription(v, k.delimiter, k.digraph_pattern)
                    if not trans_check and len(trans) > 1:
                        trans_check = True
                    d[k.attribute.name] = (k.attribute, trans)
                else:
                    d[k.attribute.name] = (k.attribute, v)
            word = Word(**d)
            if word.transcription:
                #transcriptions can have phonetic symbol delimiters which is a period
                if not word.spelling:
                    word.spelling = ''.join(map(str,word.transcription))

            corpus.add_word(word)
    if corpus.has_transcription and not trans_check:
        e = DelimiterError(('Could not parse transcriptions with that delimiter. '
                            '\n\Check that the transcription delimiter you typed '
                            'in matches the one used in the file.'))
        raise(e)

    transcription_errors = corpus.check_coverage()
    return corpus

def load_feature_matrix_csv(name,path,delimiter):
    """
    Load a FeatureMatrix from a column-delimited text file

    Parameters
    ----------
    name : str
        Informative identifier to refer to feature system

    path : str
        Full path to text file

    delimiter : str
        Character to use for spliting lines into columns

    Returns
    -------
    FeatureMatrix
        FeatureMatrix generated from the text file

    """
    text_input = []
    with open(path, encoding='utf-8-sig', mode='r') as f:
        reader = DictReader(f,delimiter=delimiter)
        for line in reader:
            if line:
                if len(line.keys()) == 1:
                    raise(DelimiterError)
                if 'symbol' not in line:
                    raise(KeyError)
                #Compat
                newline = {}
                for k,v in line.items():
                    if k == 'symbol':
                        newline[k] = v
                    elif v is not None:
                        newline[k] = v[0]
                text_input.append(newline)

    feature_matrix = FeatureMatrix(name,text_input)
    feature_matrix.validate()
    return feature_matrix

def make_safe(value, delimiter):
    """
    Recursively parse transcription lists into strings for saving

    Parameters
    ----------
    value : object
        Object to make into string

    delimiter : str
        Character to mark boundaries between list elements

    Returns
    -------
    str
        Safe string

    """
    if isinstance(value,list):
        return delimiter.join(map(lambda x: make_safe(x, delimiter),value))
    return str(value)

def export_corpus_csv(corpus,path, delimiter = ',', trans_delimiter = '.', include_variants = False):
    """
    Save a corpus as a column-delimited text file

    Parameters
    ----------
    corpus : Corpus
        Corpus to save to text file

    path : str
        Full path to write text file

    delimiter : str
        Character to mark boundaries between columns.  Defaults to ','

    trans_delimiter : str
        Character to mark boundaries in transcriptions.  Defaults to '.'

    include_variants : bool
        Whether to include a column of pronunciation variants.  Defaults to False.

    """
    word = corpus.random_word()
    header = sorted(word.descriptors)
    with open(path, encoding='utf-8', mode='w') as f:
        if include_variants:
            print(delimiter.join(header + ['Variants']), file=f)
        else:
            print(delimiter.join(header), file=f)

        for word in corpus.iter_sort():
            outline = [make_safe(getattr(word, value),trans_delimiter) for value in header]
            if include_variants:
                var = word.variants()
                d = ', '
                if delimiter == ',':
                    d = '; '
                var = d.join(make_safe(x,trans_delimiter) for x in sorted(var.keys(), key = lambda y: var[y]))
                outline.append(var)
            print(delimiter.join(outline), file=f)

def export_feature_matrix_csv(feature_matrix,path, delimiter = ','):
    """
    Save a FeatureMatrix as a column-delimited text file

    Parameters
    ----------
    feature_matrix : FeatureMatrix
        FeatureMatrix to save to text file

    path : str
        Full path to write text file

    delimiter : str
        Character to mark boundaries between columns.  Defaults to ','

    """
    with open(path, encoding='utf-8', mode='w') as f:
        header = ['symbol'] + feature_matrix.features
        writer = DictWriter(f, header,delimiter=delimiter)
        writer.writerow({h: h for h in header})
        for seg in feature_matrix.segments:
            #If FeatureMatrix uses dictionaries
            #outdict = feature_matrix[seg]
            #outdict['symbol'] = seg
            #writer.writerow(outdict)
            if seg in ['#','']: #wtf
                continue
            featline = feature_matrix.seg_to_feat_line(seg)
            outdict = {header[i]: featline[i] for i in range(len(header))}
            writer.writerow(outdict)
