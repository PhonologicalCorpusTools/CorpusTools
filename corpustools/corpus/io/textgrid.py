import os
import string
import re

from textgrid import TextGrid, IntervalTier

from corpustools.corpus.classes import SpontaneousSpeechCorpus, Speaker, Attribute
from corpustools.exceptions import TextGridTierError, PCTError

from .helper import (compile_digraphs, parse_transcription, DiscourseData,
                    AnnotationType,data_to_discourse, find_wav_path,
                    Annotation, BaseAnnotation)

def uniqueLabels(tier):
    return set(x.mark for x in tier.intervals)

def averageLabelLen(tier):
    labels = uniqueLabels(tier)
    return sum(len(lab) for lab in labels)/len(labels)


def inspect_discourse_textgrid(path):
    trans_delimiters = ['.',' ', ';', ',']
    textgrids = []
    if os.path.isdir(path):
        for root, subdirs, files in os.walk(path):
            for filename in files:
                if not filename.lower().endswith('.textgrid'):
                    continue
                textgrids.append(os.path.join(root,filename))
    else:
        textgrids.append(path)
    anno_types = []
    for t in textgrids:
        tg = load_textgrid(t)
        spellings, segments, attributes = guess_tiers(tg)
        if len(segments) == 0:
            base = None
        else:
            base = segments[0]
        if len(spellings) == 0:
            anchor = None
        else:
            anchor = spellings[0]
        interval_tiers = [x for x in tg.tiers if isinstance(x, IntervalTier)]
        if len(anno_types) == 0:
            for ti in interval_tiers:
                if ti.name in spellings:
                    a = AnnotationType(ti.name, base, None, anchor = True, token = False)
                elif ti.name in segments:
                    a = AnnotationType(ti.name, None, anchor, base = True, token = True)
                else:
                    labels = uniqueLabels(ti)
                    cat = Attribute.guess_type(labels, trans_delimiters)
                    att = Attribute(Attribute.sanitize_name(ti.name), cat, ti.name)
                    a = AnnotationType(ti.name, None, anchor, token = False, attribute = att)
                    if cat == 'tier':
                        for l in labels:
                            for delim in trans_delimiters:
                                if delim in l:
                                    a.trans_delimiter = delim
                                    break
                            if a.trans_delimiter is not None:
                                break
                a.add((x.mark for x in ti), save = False)
                anno_types.append(a)
        else:
            if len(anno_types) != len(interval_tiers):
                raise(PCTError("The TextGrids must have the same number of tiers."))
            for i, ti in enumerate(interval_tiers):
                anno_types[i].add((x.mark for x in ti), save = False)

    return anno_types

def load_textgrid(path):
    tg = TextGrid()
    tg.read(path)
    return tg

def guess_tiers(tg):
    segment_tiers = []
    spelling_tiers = []
    attribute_tiers = []
    tier_properties = {}
    interval_tiers = [x for x in tg.tiers if isinstance(x, IntervalTier)]
    for i,t in enumerate(interval_tiers):
        tier_properties[t.name] = (i, len(t), averageLabelLen(t), len(uniqueLabels(t)))

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

def textgrid_to_data(path, annotation_types, stop_check = None,
                            call_back = None):
    tg = load_textgrid(path)
    name = os.path.splitext(os.path.split(path)[1])[0]

    for a in annotation_types:
        a.reset()
    data = DiscourseData(name, annotation_types)
    for word_name in data.word_levels:
        spelling_tier = tg.getFirst(word_name)

        for si in spelling_tier:
            annotations = dict()
            word = Annotation(si.mark)
            for n in data.base_levels:
                if data[word_name].speaker != data[n].speaker \
                            and data[n].speaker is not None:
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
                        parsed = parse_transcription(ti.mark, data[n])
                        if len(parsed) > 0:
                            parsed[0].begin = phoneBegin
                            parsed[-1].end = phoneEnd
                            tier_elements.extend(parsed)
                    else:
                        if ti.mark == '':
                            ti.mark = '#'
                        a = parse_transcription(ti.mark, data[n])[0]
                        a.begin = phoneBegin
                        a.end = phoneEnd
                        tier_elements.append(a)
                level_count = data.level_length(n)
                word.references.append(n)
                word.begins.append(level_count)
                word.ends.append(level_count + len(tier_elements))
                annotations[n] = tier_elements

            mid_point = si.minTime + (si.maxTime - si.minTime)
            for at in annotation_types:
                if at.ignored:
                    continue
                if at.base:
                    continue
                if at.anchor:
                    continue
                t = tg.getFirst(at.name)
                ti = t.intervalContaining(mid_point)

                if ti is None:
                    value = None
                else:
                    value = ti.mark
                    if at.delimited:
                        value = parse_transcription(ti.mark, at)
                    elif at.ignored:
                        value = ''.join(x for x in value if x not in at.ignored)
                if at.token:
                    word.token[at.name] = value
                else:
                    word.additional[at.name] = value

            annotations[word_name] = [word]
            data.add_annotations(**annotations)
    return data


def load_discourse_textgrid(corpus_name, path, annotation_types,
                            lexicon = None,
                            feature_system_path = None,
                            stop_check = None, call_back = None):
    data = textgrid_to_data(path, annotation_types, call_back, stop_check)
    data.name = corpus_name
    data.wav_path = find_wav_path(path)
    discourse = data_to_discourse(data, lexicon)

    if feature_system_path is not None:
        feature_matrix = load_binary(feature_system_path)
        discourse.lexicon.set_feature_matrix(feature_matrix)
    return discourse

def load_directory_textgrid(corpus_name, path, annotation_types,
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
            if not filename.lower().endswith('.textgrid'):
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
            call_back('Parsing file {} of {}...'.format(i+1, len(file_tuples)))
            call_back(i)
        root, filename = t
        name = os.path.splitext(filename)[0]
        d = load_discourse_textgrid(name, os.path.join(root,filename),
                                    annotation_types, corpus.lexicon,
                                    None,
                                    stop_check, call_back)
        corpus.add_discourse(d)

    if feature_system_path is not None:
        feature_matrix = load_binary(feature_system_path)
        corpus.lexicon.set_feature_matrix(feature_matrix)
    return corpus
