
import os
import re

from corpustools.corpus.classes import Corpus, Word, Discourse, WordToken

from corpustools.exceptions import (DelimiterError, ILGError, ILGLinesMismatchError,
                                ILGWordMismatchError)

from .helper import compile_digraphs, parse_transcription, DiscourseData

def inspect_ilg(path):
    pass

def ilg_to_data(path, annotation_types, delimiter, ignore_list, digraph_list = None,
                trans_delimiter = None,
                    stop_check = None, call_back = None):
    #if 'spelling' not in line_names:
    #    raise(PCTError('Spelling required for parsing interlinear gloss files.'))
    if digraph_list is not None:
        digraph_pattern = compile_digraphs(digraph_list)
    else:
        digraph_pattern = None
    with open(path, encoding='utf-8-sig', mode='r') as f:
        text = f.read()
        if delimiter is not None and delimiter not in text:
            e = DelimiterError('The delimiter specified does not create multiple words. Please specify another delimiter.')
            raise(e)
        lines = enumerate(text.splitlines())
        lines = [x for x in lines if x[1].strip() != '']
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
                raise(ILGWordMismatchError((actual_line_ind-1, cur_line[-1]),
                                            (actual_line_ind, line)))

            if annotation_type.delimited:
                line = [parse_transcription(x,
                                        trans_delimiter,
                                        digraph_pattern) for x in line]
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


def load_corpus_ilg(corpus_name, path, delimiter, ignore_list, digraph_list = None,
                    trans_delimiter = None, feature_system_path = None,
                    stop_check = None, call_back = None):
    discourse = Discourse(name = corpus_name)
    corpus = Corpus(corpus_name)

    if digraph_list is not None:
        pattern = '|'.join(d for d in digraph_list)
        pattern += '|\w'
        digraph_re = re.compile(pattern)

    if trans_delimiter is None:
        trans_delimiter = []
    trans_patt = ''.join([re.escape(x) for x in trans_delimiter])
    trans_patt = '['+trans_patt+']+'

    with open(path, encoding='utf-8-sig', mode='r') as f:
        text = f.read()
        if delimiter is not None and delimiter not in text:
            e = DelimiterError('The delimiter specified does not create multiple words. Please specify another delimiter.')
            raise(e)

        lines = enumerate(text.splitlines())
        lines = [x for x in lines if not x[1].startswith('"') and x[1].strip() != '']
        print(len(lines))
        if len(lines) % 2 != 0:
            raise(ILGLinesMismatchError(lines))
        if call_back is not None:
            call_back('Processing file...')
            call_back(0,len(lines))
            cur = 0
        begin = 0
        previous_time = None
        trans_check = False
        for i in range(0,len(lines),2):
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 2
                if cur % 20 == 0:
                    call_back(cur)
            spelling_line = lines[i][1].strip().split(delimiter)
            transcription_line = lines[i+1][1].strip().split(delimiter)

            if len(spelling_line) != len(transcription_line):
                raise(ILGWordMismatchError((lines[i][0], spelling_line),
                                            (lines[i+1][0], transcription_line)))

            for j in range(len(spelling_line)):
                spelling = spelling_line[j].strip()
                spelling = ''.join(x for x in spelling if not x in ignore_list)
                if spelling == '':
                    raise(ILGError('Spellings must have at least one character not in the ignore_list.'))

                transcription = transcription_line[j].strip()
                if trans_delimiter:
                    transcription = re.sub('^'+trans_patt,'',transcription)
                    transcription = re.sub(trans_patt+'$','',transcription)
                    transcription = re.split(trans_patt,transcription)
                    if not trans_check and len(transcription) > 1:
                        trans_check = True
                elif digraph_list and len(transcription) > 1:
                    transcription = digraph_re.findall(transcription)
                else:
                    transcription = list(transcription)
                try:
                    word = corpus.find(spelling)
                except KeyError:
                    word = Word(spelling = spelling,
                                transcription = transcription,
                                frequency = 0)

                    corpus.add_word(word)
                word.frequency += 1
                if previous_time is not None:
                    wordtoken = WordToken(word=word,
                                    transcription = transcription,
                                    begin = begin, end = begin + 1,
                                    previous_token = discourse[previous_time])
                else:
                    wordtoken = WordToken(word=word,
                                    transcription = transcription,
                                    begin = begin, end = begin + 1)
                word.wordtokens.append(wordtoken)
                discourse.add_word(wordtoken)
                if previous_time is not None:
                    discourse[previous_time].following_token_time = wordtoken.begin

                previous_time = wordtoken.begin
                begin += 1
    discourse.lexicon = corpus

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

