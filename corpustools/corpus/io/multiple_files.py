
import os
import re
import gc

FILLERS = set(['uh','um','okay','yes','yeah','oh','heh','yknow','um-huh',
                'uh-uh','uh-huh','uh-hum','mm-hmm'])

from corpustools.corpus.classes import SpontaneousSpeechCorpus
from .helper import DiscourseData,data_to_discourse, AnnotationType, find_wav_path

def phone_match(one,two):
    if one != two and one not in two:
        return False
    return True

def inspect_discourse_multiple_files(word_path, dialect):
    if dialect == 'buckeye':
        annotation_types = [AnnotationType('spelling', 'surface_transcription', None, anchor = True),
                            AnnotationType('transcription', None, 'spelling', base = True, token = False),
                            AnnotationType('surface_transcription', None, 'spelling', base = True, token = True),
                            AnnotationType('category', None, 'spelling', base = False, token = True)]
    elif dialect == 'timit':

        annotation_types = [AnnotationType('spelling', 'transcription', None, anchor = True),
                            AnnotationType('transcription', None, 'spelling', base = True, token = True)]
    else:
        raise(NotImplementedError)
    return annotation_types

def multiple_files_to_data(word_path, phone_path, dialect, annotation_types = None,
                           call_back = None, stop_check = None):
    if annotation_types is None:
        annotation_types = inspect_discourse_multiple_files(word_path, dialect)
    name = os.path.splitext(os.path.split(word_path)[1])[0]

    if call_back is not None:
        call_back('Reading files...')
        call_back(0,0)
    words = read_words(word_path, dialect)
    phones = read_phones(phone_path, dialect)

    data = DiscourseData(name, annotation_types)

    if call_back is not None:
        call_back('Parsing files...')
        call_back(0,len(words))
        cur = 0
    for i, w in enumerate(words):
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 20 == 0:
                call_back(cur)
        annotations = dict()
        word = {'label':w['spelling'], 'token': dict()}
        beg = w['begin']
        end = w['end']
        if dialect == 'timit':
            found_all = False
            found = []
            while not found_all:
                p = phones.pop(0)
                if p['begin'] < beg:
                    continue
                found.append(p)
                if p['end'] == end:
                    found_all = True
            n = 'transcription'
            level_count = data.level_length(n)
            word[n] = (level_count,level_count+len(found))
            annotations[n] = found
        elif dialect == 'buckeye':
            if w['transcription'] is None:
                for n in data.base_levels:
                    level_count = data.level_length(n)
                    word[n] = (level_count,level_count)
            else:
                for n in data.base_levels:
                    if data[n].token:
                        expected = w[n]
                        found = []
                        while len(found) < len(expected):
                            cur_phone = phones.pop(0)
                            if phone_match(cur_phone['label'],expected[len(found)]) \
                                and cur_phone['end'] >= beg and cur_phone['begin'] <= end:
                                    found.append(cur_phone)
                            if not len(phones) and i < len(words)-1:
                                print(name)
                                print(w)
                                raise(Exception)
                    else:
                        found = [{'label':x} for x in w[n]]
                    level_count = data.level_length(n)
                    word[n] = (level_count,level_count+len(found))
                    annotations[n] = found
                for at in annotation_types:
                    if at.base:
                        continue
                    if at.anchor:
                        continue
                    value = w[at.name]
                    if at.delimited:
                        value = [{'label':x} for x in parse_transcription(ti.mark,
                                            at.attribute.delimiter,
                                            digraph_pattern)]
                    if at.token:
                        word['token'][at.name] = value
                    else:
                        word[at.name] = value
        annotations[data.word_levels[0]] = [word]
        data.add_annotations(**annotations)
    return data

def load_directory_multiple_files(corpus_name, path, dialect,
                                    annotation_types = None,
                                    feature_system_path = None,
                                    stop_check = None, call_back = None):
    if call_back is not None:
        call_back('Finding  files...')
        call_back(0, 0)
    file_tuples = []
    for root, subdirs, files in os.walk(path):
        for filename in files:
            if stop_check is not None and stop_check():
                return
            if not (filename.lower().endswith('.words') or filename.lower().endswith('.wrd')):
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
        name,ext = os.path.splitext(filename)
        if ext == '.words':
            phone_ext = '.phones'
        else:
            phone_ext = '.phn'
        word_path = os.path.join(root,filename)
        phone_path = os.path.splitext(word_path)[0] + phone_ext
        d = load_discourse_multiple_files(name, word_path, phone_path,
                                            dialect, annotation_types, feature_system_path,
                                            stop_check, None)
        corpus.add_discourse(d)
        gc.collect()
    return corpus

def load_discourse_multiple_files(corpus_name, word_path,phone_path, dialect,
                                    annotation_types = None,
                                    feature_system_path = None,
                                    stop_check = None, call_back = None):
    data = multiple_files_to_data(word_path,phone_path, dialect,
                                    annotation_types,
                                    call_back, stop_check)
    if corpus_name is not None:
        data.name = corpus_name
    data.wav_path = find_wav_path(word_path)
    mapping = { x.name: x.attribute for x in data.data.values()}
    discourse = data_to_discourse(data, mapping)
    del data
    return discourse

def read_phones(path, dialect, sr = None):
    output = list()
    with open(path,'r') as file_handle:
        if dialect == 'timit':
            if sr is None:
                sr = 16000
            for line in file_handle:

                l = line.strip().split(' ')
                start = float(l[0])
                end = float(l[1])
                phone = l[2]
                if sr is not None:
                    start /= sr
                    end /= sr
                output.append({'label':phone,'begin':begin,'end':end})
        elif dialect == 'buckeye':
            f = re.split("#\r{0,1}\n",file_handle.read())[1]
            flist = f.splitlines()
            begin = 0.0
            for l in flist:
                line = re.split("\s+\d{3}\s+",l.strip())
                end = float(line[0])
                label = re.split(" {0,1};| {0,1}\+",line[1])[0]
                output.append({'label':label,'begin':begin,'end':end})
                begin = end

        else:
            raise(NotImplementedError)
    return output

def read_words(path, dialect, sr = None):
    output = list()
    with open(path,'r') as file_handle:
        if dialect == 'timit':
            for line in file_handle:

                l = line.strip().split(' ')
                start = float(l[0])
                end = float(l[1])
                word = l[2]
                if sr is not None:
                    start /= sr
                    end /= sr
                output.append({'spelling':word, 'begin':start, 'end':end})
        elif dialect == 'buckeye':
            f = re.split(r"#\r{0,1}\n",file_handle.read())[1]
            begin = 0.0
            flist = f.splitlines()
            for l in flist:
                line = re.split("; | \d{3} ",l.strip())
                end = float(line[0])
                word = line[1]
                if word[0] != "<" and word[0] != "{":
                    citation = line[2].split(' ')
                    phonetic = line[3].split(' ')
                    category = line[4]
                else:
                    citation = None
                    phonetic = None
                    category = None
                if word in FILLERS:
                    category = 'UH'
                line = {'spelling':word,'begin':begin,'end':end,
                        'transcription':citation,'surface_transcription':phonetic,
                        'category':category}
                output.append(line)
                begin = end
        else:
            raise(NotImplementedError)
    return output

def align_multiple_files(words, phones, wavs, speaker_source, stop_check, call_back):

    if call_back is not None:
        call_back('Matching files...')
        call_back(0,len(words))
        cur = 0
    dialogs = {}
    for p in words:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            call_back(cur)
        name = os.path.splitext(os.path.split(p)[1])[0]
        dialogs[name] = {'words':p}
        if speaker_source == 'filename':
            dialogs[name]['speaker'] = name[:3] #Hack?
        elif speaker_source == 'directory':
            dialogs[name]['speaker'] =  os.path.basename(os.path.dirname(p))
        else:
            dialogs[name]['speaker'] = None
    for p2 in phones:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            call_back(cur)
        name = os.path.splitext(os.path.split(p2)[1])[0]
        dialogs[name]['phones'] = p2
    for p3 in wavs:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            call_back(cur)
        name = os.path.splitext(os.path.split(p3)[1])[0]
        try:
            dialogs[name]['wav'] = p3
        except KeyError:
            pass
    return dialogs
