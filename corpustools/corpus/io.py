from csv import DictReader, DictWriter
import pickle
import collections

from corpustools.corpus.classes import Corpus, FeatureMatrix, Word
from urllib.request import urlretrieve

class DelimiterError(Exception):
    """
    Exception for having wrong delimiter for text file
    """
    pass

def download_binary(name,path, queue = None):
    """
    Download a binary file

    Attributes
    ----------
    name : str
        Identifier of file to download

    path : str
        Full path for where to save downloaded file

    """
    def report(blocknum, bs, size):
        if queue is not None:
            queue.put((blocknum * bs * 100) / size)
    if name == 'example':
        download_link = 'https://www.dropbox.com/s/a0uar9h8wtem8cf/example.corpus?dl=1'
    elif name == 'iphod':
        download_link = 'https://www.dropbox.com/s/xb16h5ppwmo579s/iphod.corpus?dl=1'
    elif name == 'spe':
        download_link = 'https://www.dropbox.com/s/k73je4tbk6i4u4e/spe.feature?dl=1'
    elif name == 'hayes':
        download_link = 'https://www.dropbox.com/s/qe9xiq4k68cp2qx/hayes.feature?dl=1'
    filename,headers = urlretrieve(download_link,path, reporthook=report)
    if queue is not None:
        queue.put(-99)

def load_binary(path):
    """
    Unpickle a binary file

    Attributes
    ----------
    path : str
        Full path of binary file to load

    Returns
    -------
    Object
        Object generated from the text file
    """
    with open(path,'rb') as f:
        obj = pickle.load(f)
    return obj

def save_binary(obj,path):
    """
    Pickle a Corpus or FeatureMatrix object for later loading

    Attributes
    ----------
    obj : Corpus or FeatureMatrix
        Object to save

    path : str
        Full path for where to save object

    """
    with open(path,'wb') as f:
        pickle.dump(obj,f)

def load_corpus_csv(corpus_name,path,delimiter,trans_delimiter='.', feature_system_path = '',pqueue=None,oqueue=None):
    """
    Load a corpus from a column-delimited text file

    Attributes
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

    dictionary
        Dictionary with segments not in the FeatureMatrix (if specified)
        as keys and a list of words containing those segments as values

    """
    corpus = Corpus(corpus_name)
    corpus.custom = True
    if feature_system_path:
        feature_matrix = load_binary(feature_system_path)
        corpus.set_feature_matrix(feature_matrix)
    with open(path, encoding='utf-8') as f:
        headers = f.readline()
        headers = headers.split(delimiter)
        if len(headers)==1:
            e = DelimiterError('Could not parse the corpus.\n\Check that the delimiter you typed in matches the one used in the file.')
            if pqueue is not None:
                pqueue.put(e)
            else:
                raise(e)

        headers = [h.strip() for h in headers]
        headers[0] = headers[0].strip('\ufeff')
        if 'feature_system' in headers[-1]:
            headers = headers[0:len(headers)-1]



        transcription_errors = collections.defaultdict(list)
        trans_check = False

        for line in f.readlines():
            line = line.strip()
            if not line: #blank or just a newline
                continue
            d = {attribute:value.strip() for attribute,value in zip(headers,line.split(delimiter))}
            for k,v in d.items():
                if k == 'transcription' or 'tier' in k:
                    if trans_delimiter:
                        trans = v.split(trans_delimiter)
                    else:
                        trans = [x for x in v]
                    if not trans_check and len(trans) > 1:
                        trans_check = True
                    d[k] = trans
            word = Word(**d)
            if word.transcription:
                #transcriptions can have phonetic symbol delimiters which is a period
                if not word.spelling:
                    word.spelling = ''.join(map(str,word.transcription))
                if corpus.has_feature_matrix():
                    try:
                        word._specify_features(corpus.specifier)
                    except KeyError as e:
                        transcription_errors[str(e)].append(str(word))

            corpus.add_word(word)
            if pqueue is not None:
                pqueue.put(1)
    if corpus.has_transcription() and not trans_check:
        e = DelimiterError('Could not parse transcriptions with that delimiter.\n\Check that the transcription delimiter you typed in matches the one used in the file.')
        if pqueue is not None:
            pqueue.put(e)
        else:
            raise(e)

    if pqueue is not None:
        pqueue.put(-99)
    if oqueue is not None:
        oqueue.put(corpus)
        oqueue.put(transcription_errors)
    else:
        return corpus,transcription_errors

def load_corpus_text(corpus_name, path, delimiter, ignore_list,trans_delimiter='.',feature_system_path='',string_type='spelling',pqueue=None,oqueue=None):
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
    word_count = collections.defaultdict(int)
    corpus = Corpus(corpus_name)
    corpus.custom = True
    if feature_system_path:
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

                if string_type == 'transcription':
                    if trans_delimiter:
                        word = word.strip(trans_delimiter)
                        trans = word.split(trans_delimiter)
                    else:
                        trans = [x for x in word.strip()]
                    trans = [t for t in trans if not t in ignore_list]
                    if not trans_check and len(trans) > 1:
                        trans_check = True
                    word = trans_delimiter.join(trans)
                elif string_type == 'spelling':
                    word = [letter for letter in word if not letter in ignore_list]
                    word = ''.join(word)
                if not word:
                    continue
                word_count[word] += 1
    if string_type == 'transcription' and not trans_check:
        e = DelimiterError('The transcription delimiter was never found in transcriptions. Please specify another delimiter.')
        if pqueue is not None:
            pqueue.put(e)
        else:
            raise(e)
    total_words = sum(word_count.values())
    headers = [string_type,'frequency']
    transcription_errors = collections.defaultdict(list)
    for w,freq in sorted(word_count.items()):
        line = [w,freq]
        d = {attribute:value for attribute,value in zip(headers,line)}
        for k,v in d.items():
            if k == 'transcription' or 'tier' in k:
                if trans_delimiter:
                    trans = v.split(trans_delimiter)
                else:
                    trans = [x for x in v]
                d[k] = trans
        word = Word(**d)
        if word.transcription:
            if not word.spelling:
                word.spelling = ''.join(map(str,word.transcription))
        corpus.add_word(word)
        if pqueue is not None:
            pqueue.put(1)
    transcription_errors = corpus.check_coverage()
    if pqueue is not None:
        pqueue.put(-99)
    if oqueue is not None:
        oqueue.put(corpus)
        oqueue.put(transcription_errors)
    else:
        return corpus,transcription_errors

def load_feature_matrix_csv(name,path,delimiter):
    """
    Load a FeatureMatrix from a column-delimited text file

    Attributes
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
                    else:
                        newline[k] = v[0]
                text_input.append(newline)

    feature_matrix = FeatureMatrix(name,text_input)
    return feature_matrix

def make_safe(value, delimiter):
    """
    Recursively parse transcription lists into strings for saving

    Attributes
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

def export_corpus_csv(corpus,path, delimiter = ',', trans_delimiter = '.'):
    """
    Save a corpus as a column-delimited text file

    Attributes
    ----------
    corpus : Corpus
        Corpus to save to text file

    path : str
        Full path to write text file

    delimiter : str
        Character to mark boundaries between columns.  Defaults to ','

    trans_delimiter : str
        Character to mark boundaries in transcriptions.  Defaults to '.'

    """
    word = corpus.random_word()
    header = sorted(word.descriptors)
    with open(path, encoding='utf-8', mode='w') as f:
        print(delimiter.join(header), file=f)
        for key in corpus.iter_sort():
            print(delimiter.join(make_safe(getattr(key, value),trans_delimiter) for value in header), file=f)

def export_feature_matrix_csv(feature_matrix,path, delimiter = ','):
    """
    Save a FeatureMatrix as a column-delimited text file

    Attributes
    ----------
    feature_matrix : FeatureMatrix
        FeatureMatrix to save to text file

    path : str
        Full path to write text file

    delimiter : str
        Character to mark boundaries between columns.  Defaults to ','

    """
    with open(path, encoding='utf-8', mode='w') as f:
        header = ['symbol'] + feature_matrix.get_feature_list()
        writer = DictWriter(f, header,delimiter=delimiter)
        writer.writerow({h: h for h in header})
        for seg in feature_matrix.get_segments():
            #If FeatureMatrix uses dictionaries
            #outdict = feature_matrix[seg]
            #outdict['symbol'] = seg
            #writer.writerow(outdict)
            if seg in ['#','']: #wtf
                continue
            featline = feature_matrix.seg_to_feat_line(seg)
            outdict = {header[i]: featline[i] for i in range(len(header))}
            writer.writerow(outdict)
