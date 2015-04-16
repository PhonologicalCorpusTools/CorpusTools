
import os
import re

from corpustools.corpus.classes import Corpus, Word, Discourse, WordToken

from corpustools.exceptions import (DelimiterError, ILGError, ILGLinesMismatchError,
                                ILGWordMismatchError)

from .helper import compile_digraphs, parse_transcription, DiscourseData,data_to_discourse

def inspect_ilg(path):
    pass

def text_to_lines(path, delimiter):
    with open(path, encoding='utf-8-sig', mode='r') as f:
        text = f.read()
        if delimiter is not None and delimiter not in text:
            e = DelimiterError('The delimiter specified does not create multiple words. Please specify another delimiter.')
            raise(e)
    lines = enumerate(text.splitlines())
    lines = [x for x in lines if x[1].strip() != '']
    return lines

def ilg_to_data(path, annotation_types, delimiter, ignore_list, digraph_list = None,
                    stop_check = None, call_back = None):
    #if 'spelling' not in line_names:
    #    raise(PCTError('Spelling required for parsing interlinear gloss files.'))
    if digraph_list is not None:
        digraph_pattern = compile_digraphs(digraph_list)
    else:
        digraph_pattern = None

    lines = text_to_lines(path, delimiter)

    if len(lines) % len(annotation_types) != 0:
        raise(ILGLinesMismatchError(lines))

    if call_back is not None:
        call_back('Processing file...')
        call_back(0,len(lines))
        cur = 0
    index = 0
    name = os.path.splitext(os.path.split(path)[1])[0]

    data = DiscourseData(name, annotation_types)
    while index < len(lines):
        cur_line = dict()
        for line_ind, annotation_type in enumerate(annotation_types):
            if annotation_type.name == 'ignore':
                continue
            actual_line_ind, line = lines[index+line_ind]
            line = line.strip().split(delimiter)
            if len(cur_line.values()) != 0 and len(list(cur_line.values())[-1]) != len(line):
                raise(ILGWordMismatchError((actual_line_ind-1, list(cur_line.values())[-1]),
                                            (actual_line_ind, line)))

            if annotation_type.delimited:
                line = [parse_transcription(x,
                                        annotation_type.attribute.delimiter,
                                        digraph_pattern, ignore_list) for x in line]
            cur_line[annotation_type.name] = line
        for word_name in data.word_levels:
            for i, s in enumerate(cur_line[word_name]):
                annotations = dict()
                word = {'label':s, 'token':dict()}

                for n in data.base_levels:
                    tier_elements = [{'label':x} for x in cur_line[n][i]]
                    level_count = data.level_length(n)
                    word[n] = (level_count,level_count+len(tier_elements))
                    annotations[n] = tier_elements
                for line_type in cur_line.keys():
                    if data[line_type].token:
                        word['token'][line_type] = cur_line[line_type][i]
                    if data[line_type].base:
                        continue
                    if data[line_type].anchor:
                        continue
                    word[line_type] = cur_line[line_type][i]
                annotations[word_name] = [word]
                data.add_annotations(**annotations)
        index += len(annotation_types)
    return data


def load_corpus_ilg(corpus_name, path, annotation_types, delimiter,
                    ignore_list, digraph_list = None,
                    trans_delimiter = None, feature_system_path = None,
                    stop_check = None, call_back = None):
    data = ilg_to_data(path, annotation_types, delimiter, ignore_list,
                digraph_list,trans_delimiter,
                    stop_check, call_back)
    mapping = { x.name: x.attribute for x in annotation_types}
    discourse = data_to_discourse(data, mapping)

    return discourse

def export_corpus_ilg(discourse, path, trans_delim = '.'):
    with open(path, encoding='utf-8', mode='w') as f:
        spellings = list()
        transcriptions = list()
        for wt in discourse:
            spellings.append(wt.spelling)
            transcriptions.append(trans_delim.join(wt.transcription))
            if len(spellings) > 10:
                f.write(' '.join(spellings))
                f.write('\n')
                f.write(' '.join(transcriptions))
                f.write('\n')
                spellings = list()
                transcriptions = list()
        if spellings:
            f.write(' '.join(spellings))
            f.write('\n')
            f.write(' '.join(transcriptions))
            f.write('\n')

