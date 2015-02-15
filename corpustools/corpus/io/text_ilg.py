
import os
import re

from corpustools.corpus.classes import Corpus, Word, Discourse, WordToken



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

        lines = text.splitlines()
        lines = [x for x in lines if not x.startswith("\'") and x.strip() != '']
        if len(lines) % 2 != 0:
            raise(Exception("There doesn't appear to be equal numbers of orthography and transcription lines"))
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
            spelling_line = lines[i].strip().split(delimiter)
            transcription_line = lines[i+1].strip().split(delimiter)

            if len(spelling_line) != len(transcription_line):
                raise(Exception("Orthography line and transcription line were not the same length."))

            for j in range(len(spelling_line)):
                spelling = spelling_line[j].strip()
                spelling = ''.join(x for x in spelling if not x in ignore_list)
                if spelling == '':
                    raise(Exception('Spellings must have at least one character not in the ignore_list.'))

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
                                #transcription = transcription,
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

