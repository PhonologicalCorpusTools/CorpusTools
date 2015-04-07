
import os
import re

FILLERS = set(['uh','um','okay','yes','yeah','oh','heh','yknow','um-huh',
                'uh-uh','uh-huh','uh-hum','mm-hmm'])

def phone_match(one,two):
    if one != two and one not in two:
        return False
    return True

def multiple_files_to_data(word_path,phone_path, dialect):

    words = read_words(word_path, dialect)
    phones = read_phones(phone_path, dialect)
    for i, w in enumerate(words):
        beg = w['Begin']
        end = w['End']
        if dialect == 'timit':
            found_all = False
            found = []
            while not found_all:
                p = phones.pop(0)
                if p['begin'] < w['Begin']:
                    continue
                found.append(p)
                if p['end'] == w['End']:
                    found_all = True
            words[i]['Transcription'] = found
        elif dialect == 'buckeye':
            if w['lookup_transcription'] is None:
                continue
            expected = w['sr']
            found = []
            while len(found) < len(expected):
                cur_phone = phones.pop(0)
                if phone_match(cur_phone['symbol'],expected[len(found)]) \
                    and cur_phone['end'] >= beg and cur_phone['begin'] <= end:
                        found.append(cur_phone)
                if not len(phones) and i < len(words)-1:
                    print(name)
                    print(w)
                    raise(Exception)
            found[0]['begin'] = words[i]['Begin']
            found[-1]['end'] = words[i]['End']
            words[i]['Transcription'] = found
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
                output.append({'symbol':phone,'begin':begin,'end':end})
        elif dialect == 'buckeye':
            f = re.split("#\r{0,1}\n",file_handle.read())[1]
            flist = f.splitlines()
            begin = 0.0
            for l in flist:
                line = re.split("\s+\d{3}\s+",l.strip())
                end = float(line[0])
                label = re.split(" {0,1};| {0,1}\+",line[1])[0]
                output.append({'symbol':label,'begin':begin,'end':end})
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
                output.append({'lookup_spelling':word, 'Begin':start, 'End':end})
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
                line = {'lookup_spelling':word,'Begin':begin,'End':end,
                        'lookup_transcription':citation,'sr':phonetic,
                        'Category':category}
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
