from csv import DictReader, DictWriter
import pickle
import collections

from corpustools.corpus.classes import Corpus, FeatureMatrix, Word
from urllib.request import urlretrieve

class DelimiterError(Exception):
    pass

def download_binary(name,path):
    if name == 'example':
        download_link = 'https://www.dropbox.com/s/a0uar9h8wtem8cf/example.corpus?dl=1'
    elif name == 'iphod':
        download_link = 'https://www.dropbox.com/s/xb16h5ppwmo579s/iphod.corpus?dl=1'
    elif name == 'spe':
        download_link = 'https://www.dropbox.com/s/k73je4tbk6i4u4e/spe.feature?dl=1'
    elif name == 'hayes':
        download_link = 'https://www.dropbox.com/s/qe9xiq4k68cp2qx/hayes.feature?dl=1'
    filename,headers = urlretrieve(download_link,path)

def load_binary(path):
    with open(path,'rb') as f:
        obj = pickle.load(f)
    return obj
    
def save_binary(obj,path):
    with open(path,'wb') as f:
        pickle.dump(obj,f)
    
def load_corpus_csv(corpus_name,path,delimiter,trans_delimiter='.', feature_system_path = ''):
    corpus = Corpus(corpus_name)
    corpus.custom = True
    if feature_system_path:
        feature_matrix = load_binary(feature_system_path)
        corpus.set_feature_matrix(feature_matrix)
    with open(path, encoding='utf-8') as f:
        headers = f.readline()
        headers = headers.split(delimiter)
        if len(headers)==1:
            raise(DelimiterError)

        headers = [h.strip() for h in headers]
        headers[0] = headers[0].strip('\ufeff')
        if 'feature_system' in headers[-1]:
            headers = headers[0:len(headers)-1]
        
        

        transcription_errors = collections.defaultdict(list)
        
        for line in f:
            line = line.strip()
            if not line: #blank or just a newline
                continue
            d = {attribute:value.strip() for attribute,value in zip(headers,line.split(delimiter))}
            for k,v in d.items():
                if k == 'transcription' or 'tier' in k:
                    if trans_delimiter:
                        d[k] = v.split(trans_delimiter)
                    else:
                        d[k] = list(v)
            word = Word(**d)
            if word.transcription:
                #transcriptions can have phonetic symbol delimiters which is a period
                if not word.spelling:
                    word.spelling = ''.join(map(str,word.transcription))
                if corpus.has_feature_matrix():
                    try:
                        word._specify_features(corpus.get_feature_matrix())
                    except KeyError as e:
                        transcription_errors[str(e)].append(str(word))
                        continue

            corpus.add_word(word)
    
    return corpus,transcription_errors

def load_corpus_text(path,corpus_name, delimiter, ignore_list,trans_delimiter='.',feature_system_path=''):
    word_count = collections.defaultdict(int)
    corpus = Corpus(corpus_name)
    corpus.custom = True
    if feature_system_path:
        feature_matrix = load_binary(feature_system_path)
        corpus.set_feature_matrix(feature_matrix)
    with open(path, encoding='utf-8', mode='r') as f:
        for line in f.readlines():
            if not line or line == '\n':
                continue
            line = line.split(delimiter)
            for word in line:
                word = word.strip()
                word = [letter for letter in word if not letter in ignore_list]
                if not word:
                    continue
                if string_type == 'transcription':
                    word = trans_delimiter.join(word)
                elif string_type == 'spelling':
                    word = ''.join(word)
                word_count[word] += 1

    total_words = sum(word_count.values())
    headers = [string_type,'Frequency','Relative frequency']
    transcription_errors = collections.defaultdict(list)
    for w,freq in sorted(word_count.items()):
        line = [w,freq,freq/total_words]
        d = {attribute:value for attribute,value in zip(headers,line)}
        for k,v in d.items():
            if trans_delimiter in v or k == 'transcription' or 'tier' in k:
                d[k] = v.split(trans_delimiter)
        word = Word(**d)
        if word.transcription:
            if not word.spelling:
                word.spelling = ''.join(map(str,word.transcription))
            if corpus.has_feature_matrix():
                try:
                    word._specify_features(corpus.get_feature_matrix())
                except KeyError as e:
                    transcription_errors[str(e)].append(str(word))
                    continue
        corpus.add_word(word)
    return corpus,transcription_errors

def load_feature_matrix_csv(name,path,sep):
    text_input = []
    with open(path, encoding='utf-8-sig', mode='r') as f:
        reader = DictReader(f,delimiter=sep)
        for line in reader:
            if line:
                text_input.append(line)
            
    feature_matrix = FeatureMatrix(name,text_input)
    return feature_matrix

def make_safe(value):
    if isinstance(value,list):
        return '.'.join(map(make_safe,value))
    return str(value)
    
def export_corpus_csv(corpus,path):
    word = corpus.random_word()
    header = sorted(word.descriptors)
    with open(path, encoding='utf-8', mode='w') as f:
        print(','.join(header), file=f)
        for key in corpus.iter_sort():
            print(','.join(make_safe(getattr(key, value)) for value in header), file=f)
    
def export_feature_matrix_csv(feature_matrix,path):
    with open(path, encoding='utf-8', mode='w') as f:
        header = ['symbol'] + feature_matrix.get_feature_list()
        writer = DictWriter(f, header,delimiter=',')
        writer.writerow({h: h for h in header})
        for seg in feature_matrix:
            outdict = feature_matrix[seg]
            outdict['symbol'] = seg
            writer.writerow(outdict)
