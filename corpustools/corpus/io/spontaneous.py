import os
import re

from corpustools.corpus.classes import SpontaneousSpeechCorpus, Speaker

from .textgrid import TextGrid, IntervalTier, PointTier

phone_file_extensions = ['phones','phn']
word_file_extensions = ['words','wrd']


FILLERS = set(['uh','um','okay','yes','yeah','oh','heh','yknow','um-huh',
                'uh-uh','uh-huh','uh-hum','mm-hmm'])

def process_tier_names(name):
    if '-' in name:
        speaker,tier_name = name.split('-')
    elif '_' in name:
        speaker,tier_name = name.split('_')
    else:
        tier_name = name
        speaker = ''
    speaker = speaker.strip()
    tier_name = tier_name.strip().lower()
    return speaker, tier_name


def textgrids_to_data(path):
    phone_names = ['phone','phones','segment','segments','transcription', 'seg']
    word_names = ['word','words']
    tg = TextGrid()
    tg.read(path)
    words = list()
    phones = list()
    for tier in tg:
        speaker, tier_name = process_tier_names(tier.name)
        if tier_name not in word_names:
            continue

        for i in tier:
            name = i.mark
            if name is None:
                name = '<SIL>'
            w = {'word':name, 'begin':i.minTime, 'end': i.maxTime, 'speaker':speaker}
            words.append(w)

    #figure out phones
    for wi,w in enumerate(words):
        beg = w['begin']
        end = w['end']
        for tier in tg:
            speaker, tier_name = process_tier_names(tier.name)
            if tier_name in word_names:
                continue
            if tier_name in phone_names:
                phones = []
                for i in tier:
                    if i.maxTime < beg:
                        continue
                    if i.minTime >= end:
                        break
                    if not i.mark:
                        continue
                    phoneBegin = i.minTime
                    phoneEnd = i.maxTime
                    if phoneBegin < beg:
                        phoneBegin = beg
                    if phoneEnd > end:
                        phoneEnd = end
                    p = {'label':i.mark,'begin':phoneBegin,'end':phoneEnd}
                    phones.append(p)
                words[wi]['phones'] = phones
            else:
                if isinstance(tier,PointTier):
                    continue
                for i in tier:
                    if i.maxTime < beg:
                        continue
                    if not i.mark:
                        continue
                    if i.minTime >= end:
                        break
                    if i.minTime <= beg and i.maxTime >= end:
                        words[wi][tier_name.replace(' ','_')] = i.mark
    return words

def align_dialog_info(words, phones, wavs, stop_check, call_back):

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
        dialogs[name]['wav'] = p3
    return dialogs

def align_textgrid_info(textgrids, wavs, stop_check, call_back):
    if call_back is not None:
        call_back('Matching files...')
        call_back(0,len(textgrids))
        cur = 0
    dialogs = {}
    for p in textgrids:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            call_back(cur)
        name = os.path.splitext(os.path.split(p)[1])[0]
        dialogs[name] = {'textgrid':p}
    for p3 in wavs:
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            call_back(cur)
        name = os.path.splitext(os.path.split(p3)[1])[0]
        dialogs[name]['wav'] = p3
    return dialogs

def import_spontaneous_speech_corpus(directory, dialect = 'textgrid', stop_check = None, call_back = None):
    name = os.path.split(directory)[1]
    corpus = SpontaneousSpeechCorpus(name,directory)

    words = []
    phones = []
    textgrids = []
    wavs = []
    if call_back is not None:
        call_back('Finding files...')
        call_back(0,1)
        cur = 0
    for root, subdirs, files in os.walk(directory):
        if stop_check is not None and stop_check():
            return
        for f in files:
            if dialect == 'textgrid' and f.lower().endswith('.textgrid'):
                textgrids.append(os.path.join(root,f))
            elif dialect == 'buckeye' and f.endswith('.words'):
                words.append(os.path.join(root,f))
            elif dialect == 'buckeye' and f.endswith('.phones'):
                phones.append(os.path.join(root,f))
            elif dialect == 'timit' and f.endswith('.wrd'):
                words.append(os.path.join(root,f))
            elif dialect == 'timit' and f.endswith('.phn'):
                phones.append(os.path.join(root,f))
            elif f.endswith('.wav'):
                wavs.append(os.path.join(root,f))
    if dialect == 'textgrid':
        dialogs = align_textgrid_info(textgrids, wavs, stop_check, call_back)
    else:
        dialogs = align_dialog_info(words, phones, wavs, stop_check, call_back)
    print(len(dialogs))
    if call_back is not None:
        call_back('Processing discourses...')
        call_back(0,len(dialogs))
        cur = 0

    for d, v in dialogs.items():
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            call_back(cur)
        discourse_info = {'name':d}
        if dialect == 'textgrid':
            if 'textgrid' not in v:
                continue
            data = textgrids_to_data(v['textgrid'])
            print(len(data))
            discourse_info['speaker'] = Speaker('')
        else:
            if 'words' not in v:
                continue
            if 'phones' not in v:
                continue
            data = files_to_data(v['words'], v['phones'], dialect)
            if dialect == 'buckeye':
                discourse_info['speaker'] = Speaker(d[:3])
            elif dialect == 'timit':
                disourse_info['speaker'] = Speaker(os.path.split(v['words'])[-2])

        if 'wav' in v:
            discourse_info['wav_path'] = v['wav']
        corpus.add_discourse(data, discourse_info)
    return corpus

def phone_match(one,two):
    if one != two and one not in two:
        return False
    return True

def files_to_data(word_path,phone_path, dialect):

    words = read_words(word_path, dialect)
    phones = read_phones(phone_path, dialect)
    for i, w in enumerate(words):
        beg = w['begin']
        end = w['end']
        if dialect == 'timit':
            found_all = False
            found = []
            while not found_all:
                p = phones.pop(0)
                if p['begin'] < w['begin']:
                    continue
                found.append(p)
                if p['end'] == w['end']:
                    found_all = True
            words[i]['phones'] = found
        elif dialect == 'buckeye':
            if w['ur'] is None:
                continue
            expected = w['sr']
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
            words[i]['phones'] = found
            words[i]['begin'] = found[0]['begin']
            words[i]['end'] = found[-1]['end']
        else:
            raise(NotImplementedError)
    return words

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
                output.append({'word':word, 'begin':start, 'end':end})
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
                line = {'word':word,'begin':begin,'end':end,'ur':citation,'sr':phonetic,'category':category}
                output.append(line)
                begin = end
        else:
            raise(NotImplementedError)
    return output

def validate_data(words,name):
    for i, w in enumerate(words):
        if i > 0:
            prev = words[i-1]
            if prev['End'] > w['Begin']:
                if w['UR'] != 'NULL':
                    if prev['UR'] != 'NULL':
                        print(name)
                        print(prev)
                        print(w)
                        raise(Exception)
                else:
                    words[i]['Begin'] = prev['End']


        if i < len(words)-1:
            foll = words[i+1]
            if foll['Begin'] < w['End']:
                if w['UR'] != 'NULL':
                    if foll['UR'] != 'NULL':
                        print(name)
                        print(foll)
                        print(w)
                        raise(Exception)
                else:
                    words[i]['End'] = foll['Begin']
        try:
            cat = Category.objects.get(Label=w['Category'])
        except Exception:
            print(name)
            print(foll)
            print(w)

            raise(Exception)
    return words
