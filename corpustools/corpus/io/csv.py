from csv import DictReader, DictWriter
import os

from corpustools.corpus.classes.lexicon import Corpus, FeatureMatrix, Word, Attribute, Transcription
from corpustools.corpus.io.binary import save_binary, load_binary

from .helper import parse_transcription, AnnotationType, SyllableBaseAnnotation

from corpustools.exceptions import DelimiterError, PCTEncodingError, PCTError
import corpustools.gui.modernize as modernize

import time
import pdb

def inspect_csv(path, num_lines = 10, coldelim = None, transdelim = None):
    """
    Generate a list of AnnotationTypes for a specified text file for parsing
    it as a column-delimited file

    Parameters
    ----------
    path : str
        Full path to text file
    num_lines: int, optional
        The number of lines to parse from the file
    coldelim: str, optional
        A prespecified column delimiter to use, will autodetect if not
        supplied
    transdelim : list, optional
        A prespecfied set of transcription delimiters to look for, will
        autodetect if not supplied

    Returns
    -------
    list of AnnotationTypes
        Autodetected AnnotationTypes for the text file
    """
    if coldelim is not None:
        common_delimiters = [coldelim]
    else:
        common_delimiters = [',','\t',':','|']
    if transdelim is not None:
        trans_delimiters = [transdelim]
    else:
        trans_delimiters = ['.',' ', ';', ',']

    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            lines = []
            head = f.readline().strip()
            for line in f.readlines():
                if line != '\n':
                    lines.append(line.strip())
    except UnicodeDecodeError:
        raise(PCTEncodingError("PCT cannot decode your text file. Make sure it is in UTF-8.\n\n"
                               "To convert your file to UTF-8, please open it in Notepad or TextEdit "
                               "and then 'Save as' with the encoding set to 'UTF-8.'"))

    best = ''  ## best guess for the column delimiter (candidates: ',', 'tab', ':', and '|')
    num = 1
    for d in common_delimiters:
        trial = len(head.split(d))
        if trial > num:
            num = trial
            best = d
    if best == '':
        raise(DelimiterError('The column delimiter specified did not create multiple columns.'))

    head = head.split(best)
    vals = {h: list() for h in head}     # creating a dictionary object with headers (i.e., the 1st row in the file) as keys

    for line in lines:                   # for-loop each row in the file.
        l = line.strip().split(best)     # and split it with the best column delimiter
        if len(l) != len(head):
            raise(PCTError('{}, {}'.format(l,head)))
        for i in range(len(head)):
            vals[head[i]].append(l[i])
    atts = list()
    freq_flag = False  # Bool. flag for freq. the first numeric column makes it True and becomes the only freq for corpus
    for h in head:
        if h in ['Transcription', 'transcription']:         # if the header explicitly says 'transcription' then 'tier'
            cat = 'tier'
        else:   # if not, guess the attribute (numeric, tier, factor, or spelling) depending on the type of contents
            cat = Attribute.guess_type(vals[h][:num_lines], trans_delimiters)
        if cat == 'numeric' and not freq_flag:
            cat = 'freq'
            freq_flag = True
        att = Attribute(Attribute.sanitize_name(h), cat, h)
        a = AnnotationType(h, None, None, token=False, attribute=att)
        if cat == 'tier':
            for t in trans_delimiters:
                if t in vals[h][0] or t in vals[h][-1]:
                    a.trans_delimiter = t
                    break
        a.add(vals[h], save=False)
        atts.append(a)

    return atts, best

def check_feature_coverage_csv(corpus_name, path, delimiter, annotation_types=None, feature_system_path=None,
                               stop_check=None, call_back=None):

    if feature_system_path is not None and os.path.exists(feature_system_path):
        feature_matrix = load_binary(feature_system_path)
        feature_matrix = modernize.modernize_specifier(feature_matrix)

    if annotation_types is None:
        annotation_types, delimiter = inspect_csv(path, coldelim=delimiter)

    for a in annotation_types:
        a.reset()

    missing = set()

    with open(path, encoding='utf-8-sig') as f:
        headers = f.readline()
        headers = headers.split(delimiter)
        if len(headers) == 1:
            e = DelimiterError(('Could not parse the corpus.\n\Check that the column delimiter you typed in matches '
                                'the one used in the file.'))
            raise e
        headers = annotation_types

        for line in f.readlines():
            line = line.strip()
            if not line:
                continue

            for k, v in zip(headers, line.split(delimiter)):
                v = v.strip()
                if k.attribute.att_type == 'tier':
                    ignored = k.ignored_characters
                    if ignored is not None:
                        v = ''.join(x for x in v if x not in ignored)

                    sd = k.syllable_delimiter
                    if sd is not None:
                        syllables = v.split(sd)
                    else:
                        syllables = [v]

                    td = k.trans_delimiter
                    stress_spec = set(k.stress_specification.keys())
                    tone_spec = set(k.tone_specification.keys())
                    supra_spec = stress_spec.union(tone_spec)
                    for syllable in syllables:
                        syllable = ''.join(x for x in syllable if x not in supra_spec)

                        if td is None:
                            if k.digraph_pattern is not None:
                                string = k.digraph_pattern.findall(syllable)
                            else:
                                string = [x for x in syllable]
                        else:
                            string = syllable.split(td)

                        for seg in string:
                            if seg == '':
                                continue

                            if seg not in feature_matrix.segments:
                                missing.add(seg)


def load_corpus_csv(corpus_name, path, delimiter, annotation_types=None, feature_system_path=None,
                    stop_check=None, call_back=None):
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
    annotation_types : list of AnnotationType, optional
        List of AnnotationType specifying how to parse text files
    feature_system_path : str
        Full path to pickled FeatureMatrix to use with the Corpus
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    Corpus
        Corpus object generated from the text file

    """
    check_feature_coverage_csv(corpus_name, path, delimiter, annotation_types, feature_system_path,
                               stop_check, call_back)

    corpus = Corpus(corpus_name)
    if feature_system_path is not None and os.path.exists(feature_system_path):
        feature_matrix = load_binary(feature_system_path)
        feature_matrix = modernize.modernize_specifier(feature_matrix)
        corpus.set_feature_matrix(feature_matrix)

    if annotation_types is None:
        annotation_types, delimiter = inspect_csv(path, coldelim=delimiter)

    for a in annotation_types:
        a.reset()

    if call_back is not None:
        call_back('Loading...')
        call_back(0, 0)
        cur = 0

    with open(path, encoding='utf-8-sig') as f:
        headers = f.readline()
        headers = headers.split(delimiter)
        if len(headers) == 1:
            e = DelimiterError(('Could not parse the corpus.\nCheck that the column delimiter you typed in matches '
                                'the one used in the file.'))
            raise e
        headers = annotation_types

        for a in headers:
            corpus.add_attribute(a.attribute)

        trans_check = True

        for line in f.readlines():
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                call_back(cur)

            line = line.strip()
            if not line:  # blank or just a newline
                continue

            d = {}      # d is the dictionary to be fed as the argument of Word()
            for k, v in zip(headers, line.split(delimiter)):
                v = v.strip()
                if k.attribute.att_type == 'tier':      # if dealing with a transcription column
                    trans = parse_transcription(v, k, feature_matrix=feature_matrix, corpus=corpus)  # trans is a list of BaseAnnotation
                    if not trans_check and len(trans) > 1:
                        trans_check = True
                    d[k.attribute.name] = (k.attribute, trans)
                else:
                    d[k.attribute.name] = (k.attribute, v)
            word = Word(**d)
            if word.transcription:
                #transcriptions can have phonetic symbol delimiters
                if not word.spelling:
                    word.spelling = ''.join(map(str, word.transcription))

            corpus.add_word(word, allow_duplicates=True)

    if corpus.specifier is not None:
        corpus.inventory.update_features(corpus.specifier)

    if corpus.has_transcription and any(len(word.transcription) > 1 for word in corpus):
        if not trans_check:
            e = DelimiterError(('Could not parse transcriptions with that delimiter. '
                            '\nCheck that the transcription delimiter you typed '
                            'in matches the one used in the file.'))
            raise e

    if stop_check is not None and stop_check():
        return

    return corpus


def load_feature_matrix_csv(name, path, delimiter, stop_check=None, call_back=None):
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
    stop_check : callable, optional
        Optional function to check whether to gracefully terminate early
    call_back : callable, optional
        Optional function to supply progress information during the function

    Returns
    -------
    FeatureMatrix
        FeatureMatrix generated from the text file

    """
    text_input = []
    with open(path, encoding='utf-8-sig', mode='r') as f:
        reader = DictReader(f, delimiter = delimiter)
        lines = list(reader)

    if call_back is not None:
        call_back('Reading file...')
        call_back(0, len(lines))

    for i, line in enumerate(lines):
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            call_back(i)
        if line:
            if len(line.keys()) == 1:
                raise DelimiterError
            if 'symbol' not in line:
                raise KeyError
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

def make_safe(value, seg_delimiter, syll_delimiter=None):
    """
    Recursively parse transcription lists into strings for saving

    Parameters
    ----------
    value : object
        Object to make into string

    seg_delimiter : str
        Character to mark boundaries between segments

    syll_delimiter : str, optional
        Character to mark boundaries between syllables

    Returns
    -------
    str
        Safe string
    """
    if isinstance(value, Transcription):
        if syll_delimiter is not None:
            return syll_delimiter.join(map(lambda x: make_safe(list(x), seg_delimiter), value._syllable_list))
        else:
            return seg_delimiter.join(map(lambda x: make_safe(x, seg_delimiter), value.list))
    elif isinstance(value, list):
        return seg_delimiter.join(map(lambda x: make_safe(x, seg_delimiter), value))

    return str(value)

def export_corpus_csv(corpus, path,
                    delimiter = ',', trans_delimiter = '.', syll_delimiter = None,
                    variant_behavior = None):
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
    syll_delimiter : str, optional
        Character to mark boundaries in syllables.  Defaults to 'None'. Only active when syllable exists.
    variant_behavior : str, optional
        How to treat variants, 'token' will have a line for each variant,
        'column' will have a single column for all variants for a word,
        and the default will not include variants in the output
    """
    header = []
    for a in corpus.attributes:
        header.append(str(a))

    if variant_behavior == 'token':
        for a in corpus.attributes:
            if a.att_type == 'tier':
                header.append('Token_' + str(a))
        header.append('Token_Frequency')
    elif variant_behavior == 'column':
        header += ['Variants']

    with open(path, encoding='utf-8-sig', mode='w') as f:
        print(delimiter.join(header), file=f)

        for word in corpus.iter_sort():
            word_outline = []
            for a in corpus.attributes:
                word_outline.append(make_safe(getattr(word, a.name), trans_delimiter, syll_delimiter))
            if variant_behavior == 'token':
                var = word.variants()
                for v, freq in var.items():
                    token_line = []
                    for a in corpus.attributes:
                        if a.att_type == 'tier':
                            if a.name == 'transcription':
                                token_line.append(make_safe(v, trans_delimiter))
                            else:
                                segs = a.range
                                t = v.match_segments(segs)
                                token_line.append(make_safe(v, trans_delimiter))
                    token_line.append(make_safe(freq, trans_delimiter))
                    print(delimiter.join(word_outline + token_line), file=f)
                continue
            elif variant_behavior == 'column':
                var = word.variants()
                d = ', '
                if delimiter == ',':
                    d = '; '
                var = d.join(make_safe(x,trans_delimiter) for x in sorted(var.keys(), key = lambda y: var[y]))
                word_outline.append(var)
            print(delimiter.join(word_outline), file=f)

def export_feature_matrix_csv(feature_matrix, path, delimiter = ','):
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
    with open(path, encoding='utf-8-sig', mode='w', newline='') as f:
        header = ['symbol'] + feature_matrix.features
        writer = DictWriter(f, header, delimiter=delimiter)

        writer.writeheader()    # write header (list of features)
        #  writer.writerow({h: h for h in header})

        for seg in feature_matrix.segments:     # loop over each seg in inventory and write its feature values as a row
            #If FeatureMatrix uses dictionaries
            #outdict = feature_matrix[seg]
            #outdict['symbol'] = seg
            #writer.writerow(outdict)
            if seg in ['#','']: #wtf
                continue
            featline = feature_matrix.seg_to_feat_line(seg)
            outdict = {header[i]: featline[i] for i in range(len(header))}
            writer.writerow(outdict)

