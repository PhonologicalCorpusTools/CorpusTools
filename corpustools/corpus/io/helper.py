import re

from corpustools.corpus.classes import Discourse, Attribute

class AnnotationType(object):
    def __init__(self, name, subtype, supertype, anchor = False,
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

    def add(self, annotations):
        self._list.extend(annotations)

    def __iter__(self):
        for x in self._list:
            yield x

    def __len__(self):
        return len(self._list)

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
        print(keys)
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
            print(v.subtype,v.supertype)
            for ann in v:
                print(ann)
                newann = dict()
                for k2,v2 in ann.items():
                    try:
                        newk2 = self.data[k2].output_name
                        newv2 = (v2[0]+shifts[newk2],v2[1]+shifts[newk2])

                    except KeyError:
                        newk2 = k2
                        newv2 = v2
                    newann[newk2] = newv2

                print(newann)
                newdata[v.output_name].add([newann])
            if v.base:
                shifts[v.output_name] += len(v)
            print(shifts)
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

def compile_digraphs(digraph_list):
    pattern = '|'.join(d for d in digraph_list)
    pattern += '|\w'
    return re.compile(pattern)

def parse_transcription(string, delimiter, digraph_pattern):
    if delimiter is not None:
        return string.split(delimiter)
    if digraph_pattern is not None:
        return digraph_re.findall(string)
    return [x for x in string]

def data_to_discourse(data, attribute_mapping):
    d = Discourse(name = data['name'])
    corpus = Corpus(data['name']+ ' lexicon')
    base = data['base_levels']
    if base is not None:
        spelling_name = data['hierarchy'][base[0]]
    elif len(data['hierarchy'].keys()) > 0:
        spelling_name = list(data['hierarchy'].keys())[0]
    else:
        spelling_name = list(data['data'].keys())[0]

    for i,s in enumerate(data['data'][spelling_name]):

        spelling = s['label']
        try:
            word = corpus.find(spelling)
        except KeyError:
            word_kwargs = {'spelling': (attribute_mapping[spelling_name],spelling)}
            word_token_kwargs = dict()
            for k, v in s.items():
                if k not in attribute_mapping:
                    continue
                if k == 'label':
                    continue
                if k in base:
                    v = data['data'][k][s[k][0]:s[k][1]]
                att = attribute_mapping[k]
                word_kwargs[att.name] = (att, v)
            word = Word(**word_kwargs)
            corpus.add_word(word)
        for k,v in s.items():
            if k in attribute_mapping:
                continue
        word.frequency += 1

    return d
