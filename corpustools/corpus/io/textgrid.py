import os
import string
import re

from .textgrid_classes import TextGrid, IntervalTier, PointTier

from corpustools.corpus.classes import SpontaneousSpeechCorpus, Speaker, Attribute
from corpustools.exceptions import TextGridTierError

from .helper import compile_digraphs, parse_transcription, DiscourseData, AnnotationType,data_to_discourse

def characters_discourse_textgrid(path):
    pass

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
        raise(TextGridTierError('word',word_tier_name,tiers))
    for t in tiers:
        if is_phone_tier(t.name, phone_tier_name):
            break
    else:
        raise(TextGridTierError('phone',phone_tier_name,tiers))

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

def inspect_discourse_textgrid(path, transdelim = None):
    if transdelim is not None:
        trans_delimiters = [transdelim]
    else:
        trans_delimiters = ['.',' ', ';', ',']
    tg = load_textgrid(path)
    spellings, segments, attributes = guess_tiers(tg)
    if len(segments) == 0:
        base = None
    else:
        base = segments[0]
    if len(spellings) == 0:
        anchor = None
    else:
        anchor = spellings[0]
    anno_types = list()
    for t in tg.intervalTiers:
        if t.name in spellings:
            a = AnnotationType(t.name, base, None, anchor = True, token = False)
        elif t.name in segments:
            a = AnnotationType(t.name, None, anchor, base = True, token = True)
        else:
            labels = t.uniqueLabels()
            cat = Attribute.guess_type(labels, trans_delimiters)
            att = Attribute(Attribute.sanitize_name(t.name), cat, t.name)
            a = AnnotationType(t.name, None, anchor, token = False, attribute = att)
            if cat == 'tier':
                for l in labels:
                    for delim in trans_delimiters:
                        if delim in l:
                            a.trans_delimiter = delim
                            break
                    if a.trans_delimiter is not None:
                        break
        a.add((x.mark for x in t), save = False)
        anno_types.append(a)
    return anno_types

def load_textgrid(path):
    tg = TextGrid()
    tg.read(path)
    return tg

def guess_tiers(tg):
    segment_tiers = list()
    spelling_tiers = list()
    attribute_tiers = list()
    tier_properties = dict()
    for i,t in enumerate(tg.intervalTiers):
        tier_properties[t.name] = (i, len(t), t.averageLabelLen(), len(t.uniqueLabels()))

    max_labels = max(tier_properties.values(), key = lambda x: x[2])
    likely_segment = [k for k,v in tier_properties.items() if v == max_labels]
    if len(likely_segment) == 1:
        segment_tiers.append(likely_segment)
    likely_spelling = min((x for x in tier_properties.keys() if x not in segment_tiers),
                        key = lambda x: tier_properties[x][0])
    spelling_tiers.append(likely_spelling)

    for k in tier_properties.keys():
        if k in segment_tiers:
            continue
        if k in spelling_tiers:
            continue
        attribute_tiers.append(k)

    return spelling_tiers, segment_tiers, attribute_tiers

def textgrid_to_data(path, annotation_types, ignore_list = None, digraph_list = None,
                            call_back = None, stop_check = None):
    if digraph_list is not None:
        digraph_pattern = compile_digraphs(digraph_list)
    else:
        digraph_pattern = None
    tg = load_textgrid(path)
    name = os.path.splitext(os.path.split(path)[1])[0]

    data = DiscourseData(name, annotation_types)

    for word_name in data.word_levels:
        spelling_tier = tg.getFirst(word_name)

        for si in spelling_tier:
            annotations = dict()
            word = {'label': si.mark, 'token':dict()}
            for n in data.base_levels:
                if data[word_name].speaker != data[n].speaker and data[n].speaker is not None:
                    continue
                t = tg.getFirst(n)
                tier_elements = list()
                for ti in t:
                    if ti.maxTime <= si.minTime:
                        continue
                    if ti.minTime >= si.maxTime:
                        break
                    #if not ti.mark:
                    #    continue

                    phoneBegin = ti.minTime
                    phoneEnd = ti.maxTime

                    if phoneBegin < si.minTime:
                        phoneBegin = si.minTime
                    if phoneEnd > si.maxTime:
                        phoneEnd = si.maxTime
                    if data[n].delimited:
                        parsed = [{'label':x} for x in parse_transcription(ti.mark,
                                        data[n].attribute.delimiter,
                                        digraph_pattern)]
                        if len(parsed) > 0:
                            parsed[0]['begin'] = phoneBegin
                            parsed[-1]['end'] = phoneEnd
                            tier_elements.extend(parsed)
                    else:
                        tier_elements.append({'label': ti.mark,'begin': phoneBegin, 'end': phoneEnd})
                level_count = data.level_length(n)
                word[n] = (level_count,level_count+len(tier_elements))
                annotations[n] = tier_elements

            mid_point = si.minTime + (si.maxTime - si.minTime)
            for at in annotation_types:
                if at.base:
                    continue
                if at.anchor:
                    continue
                t = tg.getFirst(at.name)
                ti = t.intervalContaining(mid_point)
                #if ti is None:
                #    word[at.name] = None
                #    continue
                value = ti.mark
                if at.delimited:
                    value = [{'label':x} for x in parse_transcription(ti.mark,
                                        at.attribute.delimiter,
                                        digraph_pattern)]
                if at.token:
                    word['token'][at.name] = value
                else:
                    word[at.name] = value

            annotations[word_name] = [word]
            data.add_annotations(**annotations)
    return data


def load_discourse_textgrid(corpus_name, path, annotation_types, ignore_list = None,
                            digraph_list = None,
                            feature_system_path = None,
                            call_back = None, stop_check = None):
    data = textgrid_to_data(path, annotation_types,ignore_list,
                            digraph_list, call_back, stop_check)
    data.name = corpus_name
    mapping = { x.name: x.attribute for x in data.data.values()}
    discourse = data_to_discourse(data, mapping)

    return discourse

def textgrids_to_data(path, word_tier_name, phone_tier_name, speaker, delimiter):
    tg = load_textgrid(path)
    name = os.path.splitext(os.path.split(path)[1])[0]
    speaker_delimited = figure_out_tiers(tg.tiers,
                                        word_tier_name,
                                        phone_tier_name,speaker)
    data = {'name': name,
            'hierarchy':{'phone':'word', 'word':'speaker'}}

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
                        w[Attribute.sanitize_name(o.name)] = oi.mark
            words.append(w)
    return words

def align_textgrids(textgrids, wavs, speaker_source, stop_check, call_back):
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
