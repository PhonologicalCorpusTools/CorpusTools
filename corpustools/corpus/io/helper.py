import re
import os

from corpustools.corpus.classes import Discourse, Attribute, Corpus, Word, WordToken
from corpustools.exceptions import DelimiterError

class AnnotationType(object):
    def __init__(self, name, subtype, supertype, attribute = None, anchor = False,
                    token = False, base = False,
                    delimited = False, speaker = None):
        self._list = list()
        self.name = name
        self.subtype = subtype
        self.supertype = supertype
        self.token = token
        self.base = base
        self.delimited = delimited
        self.anchor = anchor
        self.speaker = speaker
        if self.speaker is not None:
            self.output_name = re.sub('{}\W*'.format(self.speaker),'',self.name)
        else:
            self.output_name = self.name
        if attribute is None:
            if base:
                self.attribute = Attribute(Attribute.sanitize_name(name), 'tier', name)
            else:
                self.attribute = Attribute(Attribute.sanitize_name(name), 'spelling', name)
        else:
            self.attribute = attribute

    def __getitem__(self, key):
        return self._list[key]

    def add(self, annotations):
        self._list.extend(annotations)

    def __iter__(self):
        for x in self._list:
            yield x

    def __len__(self):
        return len(self._list)

    @property
    def delimiter(self):
        return self.attribute.delimiter

    @property
    def is_word_anchor(self):
        return not self.token and self.anchor

    @property
    def is_token_base(self):
        return self.token and self.base

    @property
    def is_type_base(self):
        return not self.token and self.base

class DiscourseData(object):
    def __init__(self, name, levels):
        self.name = name
        self.data = {x.name: x for x in levels}

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, item):
        return item in self.data

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def collapse_speakers(self):
        newdata = dict()
        shifts = {self.data[x].output_name: 0 for x in self.base_levels}
        #Sort keys by speaker, then non-base levels, then base levels

        keys = list()
        speakers = sorted(set(x.speaker for x in self.data.values() if x.speaker is not None))
        for s in speakers:
            base = list()
            for k,v in self.data.items():
                if v.speaker != s:
                    continue
                if v.base:
                    base.append(k)
                else:
                    keys.append(k)
            keys.extend(base)
        for k in keys:
            v = self.data[k]
            name = v.output_name
            if name not in newdata:
                subtype = v.subtype
                supertype = v.supertype
                if subtype is not None:
                    subtype = self.data[subtype].output_name
                if supertype is not None:
                    supertype = self.data[supertype].output_name
                newdata[v.output_name] = AnnotationType(v.output_name, subtype, supertype,
                    anchor = v.anchor,token = v.token, base = v.base,
                    delimited = v.delimited)
            for ann in v:
                newann = dict()
                for k2,v2 in ann.items():
                    try:
                        newk2 = self.data[k2].output_name
                        newv2 = (v2[0]+shifts[newk2],v2[1]+shifts[newk2])

                    except KeyError:
                        newk2 = k2
                        newv2 = v2
                    newann[newk2] = newv2

                newdata[v.output_name].add([newann])
            if v.base:
                shifts[v.output_name] += len(v)
        self.data = newdata

    @property
    def word_levels(self):
        levels = list()
        for k in self.data.keys():
            if self.data[k].is_word_anchor:
                levels.append(k)
        return levels

    @property
    def base_levels(self):
        levels = list()
        for k in self.data.keys():
            if self.data[k].base:
                levels.append(k)
        return levels

    def add_annotations(self,**kwargs):
        for k,v in kwargs.items():
            self.data[k].add(v)

    def level_length(self, key):
        return len(self.data[key])

def get_corpora_list(storage_directory):
    corpus_dir = os.path.join(storage_directory,'CORPUS')
    corpora = [x.split('.')[0] for x in os.listdir(corpus_dir)]
    return corpora

def corpus_name_to_path(storage_directory,name):
    return os.path.join(storage_directory,'CORPUS',name+'.corpus')

def compile_digraphs(digraph_list):
    pattern = '|'.join(d for d in digraph_list)
    pattern += '|\w'
    return re.compile(pattern)

def parse_transcription(string, delimiter, digraph_pattern, ignore_list = None):
    if delimiter is not None:
        string = string.split(delimiter)
    elif digraph_pattern is not None:
        string = digraph_pattern.findall(string)
    if ignore_list is not None:
        string = [x for x in string if x not in ignore_list]
    return [x for x in string if x != '']

def text_to_lines(path, delimiter):
    with open(path, encoding='utf-8-sig', mode='r') as f:
        text = f.read()
        if delimiter is not None and delimiter not in text:
            e = DelimiterError('The delimiter specified does not create multiple words. Please specify another delimiter.')
            raise(e)
    lines = [x for x in text.splitlines() if x.strip() != '']
    return lines

def data_to_discourse(data, attribute_mapping):
    d = Discourse(name = data.name)
    ind = 0
    for level in data.word_levels:
        prev_time = None
        for i, s in enumerate(data[level]):
            word_kwargs = dict()
            word_token_kwargs = dict()
            for k,v in s.items():
                if k == 'label':
                    word_kwargs['spelling'] = (attribute_mapping[level],v)
                else:
                    if k == 'token':
                        for token_key, token_value in v.items():
                            att = attribute_mapping[token_key]
                            if att not in d.attributes:
                                d.add_attribute(att, initialize_defaults = True)
                            word_token_kwargs[att.name] = (att, token_value)
                    else:
                        att = attribute_mapping[k]
                        if data[k].token:
                            if att not in d.attributes:
                                d.add_attribute(att, initialize_defaults = True)
                        else:
                            if att not in d.lexicon.attributes:
                                d.lexicon.add_attribute(att, initialize_defaults = True)
                        if k in data and len(data[k]) > 0:
                            seq = data[k][v[0]:v[1]]
                            if data[k].token:
                                word_token_kwargs[att.name] = (att, seq)
                                if len(seq) > 0 and 'begin' in seq[0]:
                                    word_token_kwargs['begin'] = seq[0]['begin']
                                    word_token_kwargs['end'] = seq[-1]['end']

                            else:
                                word_kwargs[att.name] = (att, seq)
                        else:
                            word_kwargs[att.name] = (att, v)
            word = d.lexicon.get_or_create_word(**word_kwargs)
            word_token_kwargs['word'] = word
            if 'begin' not in word_token_kwargs:
                word_token_kwargs['begin'] = ind
                word_token_kwargs['end'] = ind + 1
            if prev_time is not None:
                word_token_kwargs['previous_token_time'] = prev_time
            wordtoken = WordToken(**word_token_kwargs)
            word.frequency += 1
            word.wordtokens.append(wordtoken)
            d.add_word(wordtoken)
            if prev_time is not None:
                d[prev_time].following_token_time = wordtoken.begin
            prev_time = wordtoken.begin
            ind += 1
    return d
