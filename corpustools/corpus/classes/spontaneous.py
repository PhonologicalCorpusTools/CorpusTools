
from collections import OrderedDict

from .lexicon import Transcription, Corpus

import os
import wave

class Speaker(object):
    def __init__(self,identifier, **kwargs):

        self.identifier = identifier

        for k,v in kwargs.items():
            setattr(self,k,v)

class SpontaneousSpeechCorpus(object):
    def __init__(self,name,directory):
        self.name = name
        self.directory = directory

        self.lexicon = Corpus(name+' lexicon')

        self.discourses = OrderedDict()

    def __iter__(self):
        for d in self.discourses.values():
            yield d

    def __setstate__(self,state):
        self.__dict__.update(state)

    def add_discourse(self, data, discourse_info):
        d = Discourse(**discourse_info)
        previous_time = None
        for line in data:
            spelling = line['word']
            transcription = line['ur']
            word = self.lexicon.get_or_create_word(spelling, transcription)
            word.frequency += 1
            if previous_time is not None:
                wordtoken = WordToken(word=word, transcription=line['sr'],
                                begin = line['begin'], end = line['end'],
                                previous_token = d[previous_time])
            else:
                wordtoken = WordToken(word=word, transcription=line['sr'],
                                begin = line['begin'], end = line['end'])
            word.wordtokens.append(wordtoken)
            d.add_word(wordtoken)
            if previous_time is not None:
                d[previous_time].following_token_time = wordtoken.begin

            previous_time = wordtoken.begin
        self.discourses[str(d)] = d

class Discourse(object):
    def __init__(self, **kwargs):
        self.name = ''

        for k,v in kwargs.items():
            setattr(self,k,v)

        self.words = dict()

    def __str__(self):
        return self.name

    def add_word(self,wordtoken):
        wordtoken.discourse = self
        self.words[wordtoken.begin] = wordtoken

    def __getitem__(self, key):
        if isinstance(key, float) or isinstance(key, int):
            #Find the word token at a given time
            keys = filter(lambda x: x >= key,self.words.keys())
            t = min(keys,key = lambda x: x - key)
            return self.words[t]
        raise(TypeError)

    def has_audio(self):
        if hasattr(self,'wav_path') and os.path.exists(self.wav_path):
            return True
        return False

    def __setstate__(self,state):
        self.__dict__.update(state)
        for wt in self:
            wt.wordtype.wordtokens.append(wt)

    def __iter__(self):
        for k in sorted(self.words.keys()):
            yield self.words[k]

    def extract_tokens(self, tokens, output_dir):
        if not self.has_audio():
            return
        filenames = []
        with wave.open(self.wav_path,'r') as w_in:
            sr = w_in.getframerate()
            bitdepth = w_in.getsampwidth()
            for t in tokens:
                wt = self[t]
                name = '{}_{}.wav'.format(self.identifier,wt.begin)
                wt.wav_path = os.path.join(output_dir,name)
                filenames.append(wt.wav_path)
                if os.path.exists(wt.wav_path):
                    continue

                begpos = int(wt.begin * sr)
                endpos = int(wt.end * sr)
                duration = endpos - begpos
                w_in.setpos(begpos)
                data = w_in.readframes(duration)
                with wave.open(wt.wav_path,'w') as w_out:
                    w_out.setnchannels(1)
                    w_out.setframerate(sr)
                    w_out.setsampwidth(bitdepth)
                    w_out.writeframes(data)
        return filenames


    def create_lexicon(self):
        corpus = Corpus(self.identifier + ' lexicon')
        for token in self:
            word = corpus.get_or_create_word(token.wordtype.spelling,token.wordtype.transcription)
            word.frequency += 1
            token.wordtype = word
        return corpus

    def find_wordtype(self,wordtype):
        return list(x for x in self if x.wordtype == wordtype)

    def calc_frequency(self,query):
        if isinstance(query, tuple):
            count = 0
            base = query[0]
            for x in self.find_wordtype(base):
                cur = query[0]
                for i in range(1,len(query)):
                    if cur.following_token != query[i]:
                        break
                    cur = cur.following_token
                else:
                    count += 1
            return count
        elif isinstance(query, Word):
            return len(self.find_wordtype(query))

class WordToken(object):
    def __init__(self,**kwargs):
        self.wordtype = kwargs.pop('word',None)
        self._transcription = kwargs.pop('transcription',None)
        if self._transcription is not None:
            self._transcription = Transcription(self._transcription)
        self._spelling = kwargs.pop('spelling',None)

        self.begin = kwargs.pop('begin',None)
        self.end = kwargs.pop('end',None)

        prev = kwargs.pop('previous_token',None)
        if prev is None:
            self.previous_token_time = None
        else:
            self.previous_token_time = prev.begin
        foll = kwargs.pop('following_token',None)
        if foll is None:
            self.following_token_time = None
        else:
            self.following_token_time = foll.begin

        self.discourse = kwargs.pop('discourse',None)
        self.speaker = kwargs.pop('speaker',None)

        for k,v in kwargs.items():
            setattr(self,k,v)

        self.wavpath = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state['wavpath'] = None
        return state

    def __eq__(self, other):
        if not isinstance(other,WordToken):
            return False
        if self.wordtype != other.wordtype:
            return False
        if self.begin != other.begin:
            return False
        if self.end != other.end:
            return False
        if self.discourse != other.discourse:
            return False
        if self.speaker != other.speaker:
            return False
        return True

    def __str__(self):
        return str(self.wordtype)

    def __repr__(self):
        return '<WordToken: {}, {}, {}-{}>'.format(str(self.wordtype),
                            str(self.transcription),self.begin,self.end)

    @property
    def previous_token(self):
        if self.discourse is not None and self.previous_token_time is not None:
            return self.discourse[self.previous_token_time]
        return None

    @property
    def following_token(self):
        if self.discourse is not None and self.following_token_time is not None:
            return self.discourse[self.following_token_time]
        return None

    @property
    def duration(self):
        return self.end - self.begin

    @property
    def spelling(self):
        if self._spelling is not None:
            return self._spelling
        if self.wordtype is not None:
            return self.wordtype.spelling
        return None

    @property
    def transcription(self):
        if self._transcription is not None:
            return self._transcription
        if self.wordtype is not None:
            return self.wordtype.transcription
        return None

    @property
    def previous_conditional_probability(self):
        if self.previous_token is not None:
            return self.discourse.calc_frequency(
                                (self.previous_token.wordtype,self.wordtype)
                                ) / self.discourse.calc_frequency(self.previous_token.wordtype)
        return None
