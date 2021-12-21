from collections import OrderedDict
from .lexicon import Transcription, Corpus, Attribute, Word
import os
import wave
import random
from decimal import Decimal

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
    name : str
        Name to identify the SpontaneousSpeechCorpus

    directory : str
        Directory associated with the SpontaneousSpeechCorpus

    Attributes
    ----------
    lexicon : Corpus
        Corpus object with token frequencies from its Discourses

    discourses : dict
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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def add_discourse(self, discourse):
        """
        Add a discourse to the SpontaneousSpeechCorpus

        Parameters
        ----------
        discourse : Discourse
            Discourse to be added
        """
        self.discourses[str(discourse)] = discourse
        self.lexicon += discourse.lexicon

class Discourse(object):
    """
    Discourse objects are collections of linear text with word tokens

    Parameters
    ----------
    name : str
        Identifier for the Discourse

    speaker : Speaker
        Speaker producing the tokens/text (defaults to an empty Speaker)

    Attributes
    ----------
    attributes : list of Attributes
        The Discourse object tracks all of the attributes used by its
        WordToken objects

    words : dict of WordTokens
        The keys are the beginning times of the WordTokens (or their
        place in a text if it's not a speech discourse) and the values
        are the WordTokens
    """
    def __init__(self, kwargs):
        self.name = kwargs['name']
        self.speaker = Speaker(None)
        self.wav_path = kwargs['wav_path']
        self._attributes = [kwargs['spelling_name'], kwargs['transcription_name'],
                            Attribute('begin','numeric','Begin'),
                            Attribute('end','numeric', 'End')]

        try:
            for att in kwargs['other_attributes']:
                self._attributes.append(att)
        except KeyError:
            pass

        self.words = dict()
        self.lexicon = Corpus(self.name + ' lexicon')
        self.lexicon.has_wordtokens = True
        self.lexicon.discourse = self

    def random_word(self):
        word = random.choice(list(self.words.keys()))
        return self.words[word]

    @property
    def attributes(self):
        #return [a for a in self._attributes if not a.name in ('spelling', 'transcription')]
        att_list = list()
        for a in self._attributes:
            if not a.display_name in [at.display_name for at in att_list]:
                att_list.append(a)
        #att_list.sort()
        return att_list
        #return self._attributes

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

    def add_word(self, wordtoken):
        """
        Adds a WordToken to the Discourse

        Parameters
        ----------
        wordtoken : WordToken
            WordToken to be added
        """
        wordtoken.discourse = self
        self.words[wordtoken.begins] = wordtoken
        for a in self.attributes:
            if not hasattr(wordtoken,a.name):
                wordtoken.add_attribute(a.name, a.default_value)
            a.update_range(getattr(wordtoken,a.name))

    def add_attribute(self, attribute, initialize_defaults = False):
        """
        Add an Attribute of any type to the Discourse or replace an existing Attribute.

        Parameters
        ----------
        attribute : Attribute
            Attribute to add or replace

        initialize_defaults : bool
            If True, word tokens will have this attribute set to the ``default_value``
            of the attribute, defaults to False
        """
        for i,a in enumerate(self._attributes):
            if attribute.display_name == a.display_name:
                self._attributes[i] = attribute
                break
        else:
            self._attributes.append(attribute)

        if initialize_defaults:
            for word in self:
                word.add_attribute(attribute.name,attribute.default_value)


    def __getitem__(self, key):
        if isinstance(key, float) or isinstance(key, int) or isinstance(key, Decimal):
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
        if self.wav_path is not None and os.path.exists(self.wav_path):
            return True
        return False

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self,state):
        if 'wav_path' not in state:
            state['wav_path'] = None
        self.__dict__.update(state)

        if hasattr(self,'lexicon'):
            self.lexicon.has_wordtokens = True
        # for wt in self:
        #     self.lexicon[str(wt.wordtype)].wordtokens.append(wt)
        #     wt.wordtype.wordtokens.append(wt)

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
            word = corpus.get_or_create_word(spelling=token.wordtype.spelling,
                                             transcription=token.wordtype.transcription)
            word.frequency += 1
            token.wordtype = word
            word.wordtokens.append(token)
        return corpus

    def find_wordtype(self, wordtype):
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


class WordToken():
    """
    WordToken objects are individual productions of Words

    Parameters
    ----------
    word : Word
        Word that the WordToken is associated with

    transcription : iterable of str
        Transcription for the WordToken (can be different than the
        transcription of the Word type).  Defaults to None if not
        specified

    spelling : str
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

    spelling : str
        The WordToken's spelling, or the word type's
        spelling if the WordToken's spelling is None

    previous_token : WordToken
        The previous WordToken in the Discourse

    following_token : WordToken
        The following WordToken in the Discourse

    duration : float
        The duration of the WordToken


    """
    wordtoken_attributes = {'wordtype': None, 'discourse': None, 'speaker': None, 'wavpath': None, 'begin': None,
                            'end': None, '_spelling': None, '_transcription': None, '_freq_names': None}
    def __init__(self,update=False,**kwargs):

        if update:
            self.update(update)
            return

        self.wordtype = kwargs.pop('word',None)
        self.discourse = None
        self.speaker = None
        self.wavpath = None
        self.begin = kwargs.pop('begin')
        self.end = kwargs.pop('end')
        self.begins = self.begin
        self.ends = self.end
        self._spelling = None
        self._transcription = None
        self._freq_names = ['abs_freq', 'freq_per_mil', 'sfreq', 'lowercase_freq', 'log10_freq']

        for key, value in kwargs.items():
            if not all([letter.isupper() for letter in key]):
                key = key.capitalize()
            if isinstance(value, tuple):
                att, value = value
                if att.att_type == 'numeric':
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = float('nan')
                    if key == 'Frequency':
                        setattr(self, '_frequency', value)
                elif att.att_type == 'tier':
                    value = Transcription(value)
                    self._transcription = value

                setattr(self, key, value)

            elif isinstance(value, list):
                # probably a transcription
                value = Transcription(value)
                setattr(self, key, value)
                self._transcription = value

            elif isinstance(value, str):
                try:
                    value = float(value)
                except ValueError:
                    self._spelling = value  # it's spelling, leave value as-is
                setattr(self, key, value)

            else:
                setattr(self, key, value)

        if not self._transcription:
            for name,value in self.__dict__.items():
                if isinstance(value, Transcription):
                    self._transcription = getattr(self, name)
                    break
            else:
                try:
                    self._transcription = self.wordtype._transcription
                except AttributeError:
                    self._transcription = None

        if not self._spelling:
            try:
                self._spelling = self.wordtype._spelling
            except AttributeError:
                if self._transcription is not None:
                    self._spelling = str(self._transcription)
                else:
                    self._spelling = None

    def __copy__(self):
        return WordToken(update=self)

    def update(self, old_token):

        for attribute, value in old_token.__dict__.items():
            if not hasattr(self, attribute):
                setattr(self, attribute, value)

        for attribute, default_value in WordToken.wordtoken_attributes.items():
            if hasattr(old_token, attribute):
                setattr(self, attribute, getattr(old_token, attribute))
            else:
                setattr(self, attribute, default_value)

    def __getstate__(self):
        state = self.__dict__.copy()
        state['wavpath'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

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


    def add_attribute(self, tier_name, default_value):
        setattr(self, tier_name, default_value)

    #@property
    #def previous_token(self):
    #    if self.discourse is not None and self.previous_token_time is not None:
    #        return self.discourse[self.previous_token_time]
    #    return None

    #@property
    #def following_token(self):
    #    if self.discourse is not None and self.following_token_time is not None:
    #        return self.discourse[self.following_token_time]
    #    return None

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

    @spelling.setter
    def spelling(self, value):
        self._spelling = value

    @spelling.deleter
    def spelling(self):
        del self._spelling

    @property
    def transcription(self):
        if self._transcription is not None:
            return self._transcription
        if self.wordtype is not None:
            return self.wordtype.transcription
        return None

    @transcription.setter
    def transcription(self, value):
        self._transcription = value

    @transcription.deleter
    def transcription(self):
        del self._transcription