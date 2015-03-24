import os
import re
import string

from corpustools.corpus.classes import SpontaneousSpeechCorpus, Speaker, Attribute

from .textgrid import TextGrid, IntervalTier, PointTier

phone_file_extensions = ['phones','phn']
word_file_extensions = ['words','wrd']

class SpontaneousIOError(Exception):
    def __init__(self, tiertype, tier_name, tiers):
        self.main = 'The {} tier name was not found'.format(tiertype)
        self.information = 'The tier name \'{}\' was not found in any tiers'.format(tier_name)
        self.details = 'The tier name looked for (ignoring case) was \'{}\'.\n'.format(tier_name)
        self.details += 'The following tiers were found:\n\n'
        for t in tiers:
            self.details += '{}\n'.format(t.name)

FILLERS = set(['uh','um','okay','yes','yeah','oh','heh','yknow','um-huh',
                'uh-uh','uh-huh','uh-hum','mm-hmm'])

### HELPERS ###
def process_tier_name(name):
    t = '^({0}|\s)*(\w+\s*\w+)({0}|\s)*(\w*\s*\w*)({0}|\s)*$'.format('|'.join([re.escape(x) for x in string.punctuation]))
    pattern = re.compile(t)
    matches = pattern.match(name)
    r1 = matches.group(2)
    if r1 == '':
        r1 = None
    r2 = matches.group(4)
    if r2 == '':
        r2 = None
    return r1,r2

def is_word_tier(tier_name,word_tier_name):
    if word_tier_name.lower() in tier_name.lower():
        return True
    return False

def is_phone_tier(tier_name,phone_tier_name):
    if phone_tier_name.lower() in tier_name.lower():
        return True
    return False

### END HELPERS ###

def get_speaker_names(tiers,word_name):
    speakers = list()
    for t in tiers:
        if not is_word_tier(t.name,word_name):
            continue
        names = process_tier_name(t.name)
        if word_name.lower() in names[0]:
            speakers.append(names[1])
        else:
            speakers.append(names[0])
    return sorted(set(speakers))

def figure_out_tiers(tiers, word_tier_name, phone_tier_name, speaker):
    if not word_tier_name:
        word_tier_name = 'word'
    if not phone_tier_name:
        phone_tier_name = 'phone'
    # tier checking
    for t in tiers:
        if is_word_tier(t.name, word_tier_name):
            break
    else:
        raise(SpontaneousIOError('word',word_tier_name,tiers))
    for t in tiers:
        if is_phone_tier(t.name, phone_tier_name):
            break
    else:
        raise(SpontaneousIOError('phone',phone_tier_name,tiers))

    speakers_in_tiers = get_speaker_names(tiers,word_tier_name)
    if speaker is None or speakers_in_tiers != ['Unknown']:
        speakers = {Speaker(x): {'word_tier':'', 'phone_tier':'', 'other':list()}
                    for x in speakers_in_tiers}
    else:
        speakers = {Speaker(speaker):{'word_tier':'','phone_tier':'','other':list()}}
    for t in tiers:
        if isinstance(t,PointTier):
            continue
        names = process_tier_name(t.name)
        for s,v in speakers.items():
            if s.name in names:
                if names[0] == s.name:
                    tier = names[1]
                else:
                    tier = names[0]
                if is_word_tier(tier, word_tier_name):
                    speakers[s]['word_tier'] = t
                elif is_phone_tier(tier,phone_tier_name):
                    speakers[s]['phone_tier'] = t
                else:
                    speakers[s]['other'].append(t)
    return speakers

def textgrids_to_data(path, word_tier_name, phone_tier_name, speaker, delimiter):
    tg = TextGrid()
    tg.read(path)
    speaker_delimited = figure_out_tiers(tg.tiers,
                                        word_tier_name,
                                        phone_tier_name,speaker)
    words = list()
    for s, v in speaker_delimited.items():
        for wi in v['word_tier']:
            w = {'lookup_spelling':wi.mark, 'Begin':wi.minTime, 'End': wi.maxTime, 'Speaker':s}
            w['Transcription'] = list()
            for pi in v['phone_tier']:
                if pi.maxTime <= w['Begin']:
                    continue
                if pi.minTime >= w['End']:
                    break
                if not pi.mark:
                    continue

                phoneBegin = pi.minTime
                phoneEnd = pi.maxTime
                if phoneBegin < w['Begin']:
                    phoneBegin = w['Begin']
                if phoneEnd > w['End']:
                    phoneEnd = w['End']
                w['Transcription'].append({'symbol':pi.mark,'begin':phoneBegin,'end':phoneEnd})
            for o in v['other']:
                for oi in o:
                    if oi.maxTime < w['Begin']:
                        continue
                    if not oi.mark:
                        continue
                    if oi.minTime >= w['End']:
                        break
                    if oi.minTime <= w['Begin'] and oi.maxTime >= w['End']:
                        w[tier_name] = oi.mark
            words.append(w)
    return words

def align_dialog_info(words, phones, wavs, speaker_source, stop_check, call_back):

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

def align_textgrid_info(textgrids, wavs, speaker_source, stop_check, call_back):
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
        if speaker_source == 'filename':
            dialogs[name]['speaker'] = name[:3] #Hack?
        elif speaker_source == 'directory':
            dialogs[name]['speaker'] = os.path.basename(os.path.dirname(p))
        else:
            dialogs[name]['speaker'] = None
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

def import_spontaneous_speech_corpus(corpus_name, directory, **kwargs):
    """
    Create a SpontaneousSpeechCorpus from a directory of Praat TextGrid
    files or paired word-phone files.

    When using TextGrids, speakers will be recognized automatically
    (though each speaker must have a tier for spelling, specified by
    `word_tier_name` and a tier for transcription, specified by
    `phone_tier_name`).  Any interval tiers that are not identified as
    word or phone tiers will be added as attributes of the resulting
    WordTokens.

    Parameters
    ----------

    corpus_name : str
        Informative identifier to refer to corpus

    directory : str
        Full path to the corpus directory

    dialect : str
        One of 'textgrid', 'buckeye' or 'timit'

    speaker_source : string
        Either 'filename', 'directory' or unspecified.  The option 'filename'
        means that the first three characters of a filename will be used
        as the name of the speaker for that dialog. The option 'directory'
        will use the directory name for the Speaker names.  Unspecified will
        create a base Speaker to be edited later.

    word_tier_name : string
        Only used for TextGrids, the name to identify tiers to use for
        spelling

    phone_tier_name : string
        Only used for TextGrids, the name to identify tiers to use for
        transcription

    delimiter : string
        Single character to use if the phone labels contain multiple
        segments

    stop_check : callable
        Callable that returns a boolean for whether to exit before
        finishing full calculation

    call_back : callable
        Function that can handle strings (text updates of progress),
        tuples of two integers (0, total number of steps) and an integer
        for updating progress out of the total set by a tuple

    Returns
    -------
    SpontaneousSpeechCorpus
        SpontaneousSpeechCorpus object generated from the directory

    """

    dialect = kwargs.pop('dialect', 'textgrid')
    stop_check = kwargs.pop('stop_check', None)
    call_back = kwargs.pop('call_back', None)
    speaker_source = kwargs.pop('speaker_source', None)
    delimiter = kwargs.pop('delimiter', None)

    corpus = SpontaneousSpeechCorpus(corpus_name,directory)

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
        word_tier_name = kwargs.pop('word_tier_name', None)
        phone_tier_name = kwargs.pop('phone_tier_name', None)
        dialogs = align_textgrid_info(textgrids, wavs, speaker_source, stop_check, call_back)
    else:
        dialogs = align_dialog_info(words, phones, wavs, speaker_source, stop_check, call_back)
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
            data = textgrids_to_data(v['textgrid'], word_tier_name,
                                                    phone_tier_name,
                                                    v['speaker'], delimiter)
        else:
            if 'words' not in v:
                continue
            if 'phones' not in v:
                continue
            data = files_to_data(v['words'], v['phones'], dialect)
            discourse_info['speaker'] = Speaker(v['speaker'])

        if 'wav' in v:
            discourse_info['wav_path'] = v['wav']
        corpus.add_discourse(data, discourse_info,delimiter=delimiter)
    return corpus

def phone_match(one,two):
    if one != two and one not in two:
        return False
    return True

def files_to_data(word_path,phone_path, dialect):

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
