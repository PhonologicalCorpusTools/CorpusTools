
from collections import OrderedDict

from .lexicon import Transcription, Corpus, Attribute

import os
import wave

class Speaker(object):
    """
    Speaker objects contain information about the producers of WordTokens
    or Discourses

    Parameters
    ----------
    name : string
        Name to identify the Speaker

    Attributes
    ----------
    name : string
        Name of Speaker

    gender : string
        Gender of Speaker

    age : int or string
        Age of Speaker


    """
    def __init__(self,name, **kwargs):

        self.name = name

        self.gender = None
        self.age = None

        for k,v in kwargs.items():
            setattr(self,k,v)

    def __repr__(self):
        return '<Speaker object with name \'{}\>'.format(self.name)

    def __str__(self):
        return str(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other,Speaker):
            return self.name == other.name
        else:
            return self.name == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __le__(self, other):
        return self.name <= other.name

    def __ge__(self, other):
        return self.name >= other.name

class SpontaneousSpeechCorpus(object):
    """
    SpontaneousSpeechCorpus objects a collection of Discourse objects and
    Corpus objects for frequency information.

    Parameters
    ----------
    name : string
        Name to identify the SpontaneousSpeechCorpus

    directory : string
        Directory associated with the SpontaneousSpeechCorpus

    Attributes
    ----------
    lexicon : Corpus
        Corpus object with token frequencies from its Discourses

    discourses : dictionary
        Discourses of the SpontaneousSpeechCorpus indexed by the names of
        the Discourses

    """
    def __init__(self,name,directory):
        self.name = name
        self.directory = directory

        self.lexicon = Corpus(name+' lexicon')
        self.lexicon.has_wordtokens = True

        self.discourses = OrderedDict()

    def __iter__(self):
        for d in self.discourses.values():
            yield d

    def __setstate__(self,state):
        self.__dict__.update(state)
        self.lexicon.has_wordtokens = True


    def add_discourse(self, data, discourse_info, delimiter=None):
        """
        Add a discourse to the SpontaneousSpeechCorpus

        Parameters
        ----------
        data : list of dictionaries
            Dictionaries should minimally have `Spelling`, `Begin` and
            `End` as keys, and `Transcription` if the production has
            a transcription

        discourse_info : dictionary
            Dictionary of information for building the discourse

        delimiter : string
            String to split segments into multiple segments, if needed.
            Defaults to None
        """
        d = Discourse(**discourse_info)
        d_atts = d.attributes
        previous_time = None
        for line in data:
            spelling = line['lookup_spelling']
            if 'lookup_transcription' in line:
                transcription = line['lookup_transcription']
            else:
                transcription = list()
            if 'Transcription' in line:
                t = line['Transcription']
            else:
                t = list()
            word = self.lexicon.get_or_create_word(spelling, transcription)
            word.frequency += 1
            token_kwargs = {'word':word, 'transcription':t,
                            'begin': line['Begin'], 'end': line['End']}
            if previous_time is not None:
                token_kwargs['previous_token'] = d[previous_time]
            additional_keys = [(Attribute.sanitize_name(x),x)
                            for x in line.keys()
                            if Attribute.sanitize_name(x) not in token_kwargs.keys()
                            and not x.startswith('lookup_')]
            for sank, unsank in additional_keys:
                token_kwargs[sank] = line[unsank]
            wordtoken = WordToken(**token_kwargs)
            word.wordtokens.append(wordtoken)
            d.add_word(wordtoken)
            att_names = [Attribute(Attribute.sanitize_name(x),
                                    'spelling',
                                    x) for x in line.keys()
                if Attribute.sanitize_name(x) not in d_atts and not x.islower()]
            d.update_attributes(att_names)
            if delimiter is not None:
                segs = list()
                for s in t:
                    if delimiter in s['symbol']:
                        segs.extend(s['symbol'].split(delimiter))
                    else:
                        segs.append(s['symbol'])
            else:
                segs = [x['symbol'] for x in t]
            self.lexicon.update_inventory(segs)
            if previous_time is not None:
                d[previous_time].following_token_time = wordtoken.begin

            previous_time = wordtoken.begin
        self.discourses[str(d)] = d

class Discourse(object):
    """
    Discourse objects are collections of linear text with word tokens

    Parameters
    ----------
    name : string
        Identifier for the Discourse

    speaker : Speaker
        Speaker producing the tokens/text (defaults to an empty Speaker)

    Attributes
    ----------
    attributes : list of Attributes
        The Discourse object tracks all of the attributes used by its
        WordToken objects

    words : dictionary of WordTokens
        The keys are the beginning times of the WordTokens (or their
        place in a text if it's not a speech discourse) and the values
        are the WordTokens

    """
    def __init__(self, **kwargs):
        self.name = ''
        self.speaker = Speaker(None)

        for k,v in kwargs.items():
            setattr(self,k,v)

        self._attributes = [Attribute('spelling','spelling','Spelling'),
                            Attribute('transcription','tier','Transcription'),
                            Attribute('begin','numeric','Begin'),
                            Attribute('end','numeric', 'End')]

        self.words = dict()

    @property
    def attributes(self):
        return self._attributes

    def update_attributes(self, attributes):
        """
        Add additional WordToken attributes to track.  If any of the
        attributes to be added overlaps in `name` with the current attributes, it is
        not added.

        Parameters
        ----------
        attributes : list of Attributes
            Attributes of WordTokens to be tracked by the Discourse

        """
        for a in attributes:
            if a not in self._attributes:
                self._attributes.append(a)

    def keys(self):
        """
        Returns a sorted list of keys for looking up WordTokens

        Returns
        -------
        list
            List of begin times or indices of WordTokens in the Discourse
        """
        return sorted(self.words.keys())

    def __len__(self):
        return len(self.words.keys())

    def __eq__(self, other):
        if not isinstance(other,Discourse):
            return False
        if self.name != other.name:
            return False
        if self.speaker != other.speaker:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __le__(self, other):
        return self.name <= other.name

    def __ge__(self, other):
        return self.name >= other.name

    def __str__(self):
        return self.name

    def add_word(self,wordtoken):
        """
        Adds a WordToken to the Discourse

        Parameters
        ----------
        wordtoken : WordToken
            WordToken to be added
        """
        wordtoken.discourse = self
        self.words[wordtoken.begin] = wordtoken

    def __getitem__(self, key):
        if isinstance(key, float) or isinstance(key, int):
            #Find the word token at a given time
            keys = filter(lambda x: x >= key,self.words.keys())
            t = min(keys,key = lambda x: x - key)
            return self.words[t]
        raise(TypeError)

    @property
    def has_audio(self):
        """
        Checks whether the Discourse is associated with a .wav file

        Returns
        -------
        bool
            True if a .wav file is associated and if that file exists,
            False otherwise
        """
        if hasattr(self,'wav_path') and os.path.exists(self.wav_path):
            return True
        return False

    def __setstate__(self,state):
        self.__dict__.update(state)
        if hasattr(self,'lexicon'):
            self.lexicon.has_wordtokens = True
        for wt in self:
            wt.wordtype.wordtokens.append(wt)

    def __iter__(self):
        for k in sorted(self.words.keys()):
            yield self.words[k]

    def _extract_tokens(self, tokens, output_dir):
        if not self.has_audio():
            return
        filenames = []
        with wave.open(self.wav_path,'r') as w_in:
            sr = w_in.getframerate()
            bitdepth = w_in.getsampwidth()
            for t in tokens:
                wt = self[t]
                name = '{}_{}.wav'.format(self.name,wt.begin)
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
        """
        Create a Corpus object from the Discourse

        Returns
        -------
        Corpus
            Corpus with spelling and transcription from previous Corpus
            and token frequency from the Discourse

        """
        corpus = Corpus(self.name + ' lexicon')
        corpus.has_wordtokens = True
        for token in self:
            word = corpus.get_or_create_word(token.wordtype.spelling,token.wordtype.transcription)
            word.frequency += 1
            token.wordtype = word
            word.wordtokens.append(token)
        return corpus

    def find_wordtype(self,wordtype):
        """
        Look up all WordTokens that are instances of a Word

        Parameters
        ----------
        wordtype : Word
            Word to look up

        Returns
        -------
        list of WordTokens
            List of the given Word's WordTokens in this Discourse
        """
        return list(x for x in self if x.wordtype == wordtype)

    def _calc_frequency(self,query):
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
    """
    WordToken objects are individual productions of Words

    Parameters
    ----------
    word : Word
        Word that the WordToken is associated with

    transcription : iterable of strings
        Transcription for the WordToken (can be different than the
        transcription of the Word type).  Defaults to None if not
        specified

    spelling : string
        Spelling for the WordToken (can be different than the
        spelling of the Word type).  Defaults to None if not
        specified

    begin : float or int
        Beginning of the WordToken (can be specified as either in seconds
        of time or in position from the beginning of the Discourse)

    end : float or int
        End of the WordToken (can be specified as either in seconds
        of time or in position from the beginning of the Discourse)

    previous_token : WordToken
        The preceding WordToken in the Discourse, defaults to None if
        not specified

    following_token : WordToken
        The following WordToken in the Discourse, defaults to None if
        not specified

    discourse : Discourse
        Parent Discourse object that the WordToken belongs to

    speaker : Speaker
        The Speaker that produced the token

    Attributes
    ----------
    transcription : Transcription
        The WordToken's transcription, or the word type's
        transcription if the WordToken's transcription is None

    spelling : string
        The WordToken's spelling, or the word type's
        spelling if the WordToken's spelling is None

    previous_token : WordToken
        The previous WordToken in the Discourse

    following_token : WordToken
        The following WordToken in the Discourse

    duration : float
        The duration of the WordToken


    """
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
