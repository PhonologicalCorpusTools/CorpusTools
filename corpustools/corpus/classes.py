#!/usr/bin/env python

import os
import random
import collections
import math

class CorpusIntegrityError(Exception):
    pass

class Segment(object):
    """
    Class for segment symbols
    """

    def __init__(self, symbol):
        #None defaults are for word-boundary symbols
        self.symbol = symbol
        self.features = dict()

    def specify(self,feature_dict):
        self.features = feature_dict

    def feature_match(self, specification):
        """
        Return true if segment matches specification, false otherwise.
        Specification can be a single feature value '+feature' or a list of
        feature values ['+feature1','-feature2']
        """
        if isinstance(specification,str):
            try:
                if self.features[specification[1:]]!=specification[0]:
                    return False
            except KeyError:
                return False
        elif isinstance(specification,list):
            for f in specification:
                try:
                    if self.features[f[1:]]!=f[0]:
                        return False
                except KeyError:
                    return False
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.symbol

    def __eq__(self, other):
        """Two segments are considered equal if their symbol attributes match

        """
        if isinstance(other, Segment):
            return self.symbol == other.symbol
        else:
            return self.symbol == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self,other):
        if isinstance(other, Segment):
            return self.symbol < other.symbol
        else:
            return self.symbol < other

    def __le__(self,other):
        return (self.symbol == other.symbol or self.symbol < other.symbol)

    def __ge__(self,other):
        return (self.symbol == other.symbol or self.symbol > other.symbol)

    def __gt__(self,other):
        if isinstance(other, Segment):
            return self.symbol > other.symbol
        else:
            return self.symbol > other

    def __len__(self):
        return len(self.symbol)

class Transcription(object):
    """
    Transcription object, sequence of symbols
    """
    def __init__(self,seg_list):
        self._list = seg_list

    def __getitem__(self, key):
        if isinstance(key,int) or isinstance(key,slice):
            return self._list[key]
        raise(KeyError)

    def __str__(self):
        return '.'.join(self._list)

    def __iter__(self):
        for s in self._list:
            yield s

    def __add__(self, other):
        """
        Allow for Transcriptions to be added to get all the segments in each
        """
        if not isinstance(other,Transcription):
            raise(TypeError)
        return self._list + other._list

    def __eq__(self, other):
        if not isinstance(other, Transcription) and not isinstance(other,list):
            return False

        if len(other) != len(self):
            return False
        for i,s  in enumerate(self):
            if s != other[i]:
                return False
        return True

    def __lt__(self,other):
        if isinstance(other, Transcription):
            return self._list < other._list
        else:
            return self._list < other

    def __le__(self,other):
        if isinstance(other, Transcription):
            return (self._list == other._list or self._list < other._list)
        else:
            return self._list <= other

    def __ge__(self,other):
        if isinstance(other, Transcription):
            return (self._list == other._list or self._list > other._list)
        else:
            return self._list >= other

    def __gt__(self,other):
        if isinstance(other, Transcription):
            return self._list > other._list
        else:
            return self._list > other

    def match_segments(self, segments):
        """
        Returns a matching segments from a list of segments
        """
        match = list()
        for s in self:
            if s in segments:
                match.append(s)
        return match

    def get_env(self,pos):
        """
        Return the symbol to the left and the symbol to the right of the position
        """

        if len(self) == 1:
            lhs = '#'
            rhs = '#'
        elif pos == 0:
            lhs = '#'
            rhs = self[pos+1]
        elif pos == len(self)-1:
            lhs = self[pos-1]
            rhs = '#'
        else:
            lhs = self[pos-1]
            rhs = self[pos+1]
        return lhs,rhs

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self._list)

class FeatureMatrix(object):
    """
    An object that stores feature values for segments


    Attributes
    ----------
    name : str
        An informative identifier for the feature matrix

    feature_entries : list of Dictionary
        Dictionaries in the list should contain feature names as keys
        and feature values as values, as well as a special key-value pair
        for the symbol

    """

    def __init__(self, name,feature_entries):
        self.name = name
        self._features = None
        self.possible_values = set()
        self.matrix = {}
        self._default_value = 'n'
        for s in feature_entries:
            if self._features is None:
                self._features = {k for k in s.keys() if k != 'symbol'}
            self.matrix[s['symbol']] = {k:v for k,v in s.items() if k != 'symbol'}
            self.possible_values.update({v for k,v in s.items() if k != 'symbol'})

        #What are these?
        self.matrix['#'] = {'#':''}
        self.matrix[''] = {'*':''}

    def __eq__(self, other):
        if not isinstance(other,FeatureMatrix):
            return False
        if self.matrix == other.matrix:
            return True
        return False

    def __setstate__(self,state):
        if '_features' not in state:
            state['_features'] = state['features']
        self.__dict__.update(state)

        #Backwards compatability
        if '_default_value' not in state:
            self._default_value = 'n'

    def validate(self):
        """
        Make sure that all segments in the matrix have all the features.
        If not, add an unspecified value for that feature to them.
        """
        for v in self.possible_values:
            if v not in ['+','-','.']:
                default_value = v
                break
        #dictionary
        for k,v in self.matrix.items():
            for f in self._features:
                if f not in v:
                    self.matrix[k][f] = self._default_value

    @property
    def default_value(self):
        return self._default_value

    @property
    def features(self):
        """
        Get a list of features that are used in this feature system

        Returns
        -------
        list
            Sorted list of the names of all features in the matrix
        """
        return sorted(list(self._features))

    def add_segment(self,seg,feat_spec):
        """
        Add a segment with a feature specification to the feature system

        Attributes
        ----------
        seg : str
            Segment symbol to add to the feature system

        feat_spec : dictionary
            Dictionary with features as keys and feature values as values

        """

        #Validation
        for f in feat_spec.keys():
            if f not in self._features:
                raise(AttributeError('The segment \'%s\' has a feature \'%s\' that is not defined for this feature matrix' %(seg,f)))

        self.matrix[seg] = feat_spec

    def add_feature(self,feature):
        """
        Add a feature to the feature system

        Attributes
        ----------
        feature : str
            Name of the feature to add to the feature system

        """

        self._features.update({feature})
        self.validate()

    @property
    def segments(self):
        """
        Return a list of segment symbols that are specified in the feature
        system

        Returns
        -------
        list
            List of all the segments with feature specifications
        """
        return list(self.matrix.keys())

    def seg_to_feat_line(self,symbol):
        """
        Get a list of feature values for a given segment in the order
        that features are return in get_feature_list

        Use for display purposes

        Attributes
        ----------
        symbol : str
            Segment symbol to look up

        Returns
        -------
        list
            List of feature values for the symbol, as well as the symbol itself
        """
        featline = [symbol] + [ self.matrix[symbol][feat]
                            for feat in self.features]
        return featline

    def __getitem__(self,item):
        if isinstance(item,str):
            return self.matrix[item]
        elif isinstance(item,tuple):
            return self.matrix[item[0]][item[1]]

    def __delitem__(self,item):
        del self.matrix[item]

    def __contains__(self,item):
        return item in list(self.matrix.keys())

    def __setitem__(self,key,value):
        self.matrix[key] = value

    def __len__(self):
        return len(self.matrix)

class Speaker(object):
    def __init__(self,identifier, **kwargs):

        self.identifier = identifier

        for k,v in kwargs.items():
            setattr(self,k,v)

class Discourse(object):
    def __init__(self, identifier, **kwargs):
        self.identifier = identifier

        for k,v in kwargs.items():
            setattr(self,k,v)

        self.words = dict()

        self.lexicon = Corpus(identifier+' lexicon')

    def add_word(self,wordtoken):
        self.words[wordtoken.begin] = wordtoken
        self.lexicon.add_word(wordtoken.wordtype)

    def __getitem__(self, key):
        if isinstance(key, float) or isinstance(key, int):
            #Find the word token at a given time
            keys = filter(lambda x: x > 0,[key - x for x in self.words.keys()])

            return self.words[min(keys)]
        raise(TypeError)

    def __iter__(self):
        for k in sorted(self.words.keys()):
            yield self.words[k]

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

        self.previous_token = kwargs.pop('previous_token',None)
        self.following_token = kwargs.pop('following_token',None)

        self.discourse = kwargs.pop('discourse',None)
        self.speaker = kwargs.pop('speaker',None)

        for k,v in kwargs.items():
            setattr(self,k,v)

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


class Word(object):
    """An object representing a word in a corpus

    A Corpus object creates Words from information in a user-supplied text file.
    The names of the attributes of a Word are therefore unpredictable.

    Attributes
    ----------
    spelling : str
        A representation of a word that lacks phonological information.

    transcription : list of Segments
        A representation of a word that includes phonological information.

    tiers : list
        A list of tiers, which are created with the self.add_tier method. This
        is an empty list if not tiers have been created.

    descriptors : list of str
        A list of the names of the attributes of a Word instance. This is
        automatically generated based on the contents of the original corpus


    """

    _corpus = None

    _freq_names = ['abs_freq', 'freq_per_mil','sfreq',
        'lowercase_freq', 'log10_freq']

    def __init__(self, **kwargs):

        self.tiers = list()
        self.transcription = None
        self.spelling = None
        self.frequency = 1
        self.descriptors = ['spelling','transcription']

        for key, value in kwargs.items():
            key = key.lower()
            if key in self._freq_names:
                key = 'frequency'
            if isinstance(value,list):
                #transcription type stuff
                if key != 'transcription':
                    self.tiers.append(key)
                value = Transcription(value)
            elif key != 'spelling':
                try:
                    f = float(value)
                    if not math.isnan(f) and not math.isinf(f):
                        value = f
                except ValueError:
                    pass
            setattr(self,key, value)
            if key not in self.descriptors:
                self.descriptors.append(key)
        if self.spelling is None and self.transcription is None:
            raise(ValueError('Words must be specified with at least a spelling or a transcription.'))
        if self.spelling is None:
            self.spelling = ''.join(map(str,self.transcription))

    def __getstate__(self):
        state = self.__dict__.copy()
        #for k,v in state.items():
        #    if (k == 'transcription' or k in self.tiers) and v is not None:
        #        state[k] = [x.symbol for x in v] #Only store string symbols
        return state

    def add_tier(self, tier_name, tier_segments):
        """Adds a new tier attribute to a Word instance

        Parameters
        ----------
        tier_name : str
            User-supplied name for the new tier

        tier_features: list of str
            User-supplied list of phonological features values that define
            which segments are included in the tier

        """
        matching_segs = self.transcription.match_segments(tier_segments)
        new_tier = Transcription(matching_segs)
        setattr(self,tier_name,new_tier)
        if tier_name not in self.tiers:
            self.tiers.append(tier_name)

    def remove_tier(self, tier_name):
        """Deletes a tier attribute from a Word

        Parameters
        ----------
        tier_name : str
            Name of tier attribute to be deleted.

        Notes
        ----------
        If tier_name is not a valid attribute, this function does nothing. It
        does not raise an error.

        """
        try:
            self.tiers.remove(tier_name)
            delattr(self, tier_name)
        except ValueError:
            pass #tier_name does not exist

    def details(self):
        """Formatted printout of a Word's attributes and their values.

        Notes
        ----------
        This is intended for debugging and interactive mode.
        """
        print('-'*25)
        for description in self.descriptors:
            print('{}: {}'.format(description, getattr(self,description)))
        print('-'*25+'\n')

    def get_env(self,pos,tier_name):
        """Get details of a particular environment in a Word

        Parameters
        ----------
        pos : int
            A position in the word, so 0<=pos<=len(self)

        Returns
        ----------
        e : Environment
            Environment of the segment at the given position in the word

        """
        tier = getattr(self,tier_name)
        lhs, rhs = tier.get_env(pos)
        e = Environment(lhs, rhs)

        return e

    def __repr__(self):
        return '<Word: \'%s\'>' % self.spelling

    def __str__(self):
        return self.spelling


    def __eq__(self, other):
        if not isinstance(other,Word):
            return False
        if self.spelling != other.spelling:
            return False
        if self.transcription != other.transcription:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.spelling < other.spelling

    def __gt__(self, other):
        return self.spelling > other.spelling

    def __le__(self, other):
        return self.spelling <= other.spelling

    def __ge__(self, other):
        return self.spelling >= other.spelling

class Environment(object):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return '_'.join([self.lhs, self.rhs])

    def __hash__(self):
        return hash((lhs,rhs))

    def __eq__(self,other):
        """Two Environments are equal if they share a left AND right hand side

        """
        if not isinstance(other,Environment):
            return False

        if other.lhs != self.lhs:
            return False
        if other.rhs != self.rhs:
            return False
        return True

    def __ne__(self,other):
        return not self.__eq__(other)


class EnvironmentFilter(object):
    def __init__(self, corpus, env):

        #there's a problem where some feature names have underscores in them
        #so doing lhs,rhs=env.split('_') causes unpacking problems
        #this in an awakward work-around that checks to see if either side of
        #the environment is a list of features, by looking for brackets, then
        #splits by brackets if necessary. However, I can't split out any
        #starting brackets [ because I also use those for identifying lists
        #at a later point
        #otherwise, if its just segment envrionments, split by underscore
        if ']_[' in env:
            #both sides are lists
            lhs, rhs = env.split(']_')
        elif '_[' in env:
            #only the right hand side is a list of a features
            lhs, rhs = env.split('_', maxsplit=1)
        elif ']_' in env:
            #only the left hand side is a list of features
            lhs, rhs = env.split(']_')
        else: #both sides are segments
            lhs, rhs = env.split('_')

        if not lhs:
            self.lhs_string  = ''
            self.lhs = list()
        elif lhs.startswith('['):
            self.lhs_string = lhs
            lhs = lhs.lstrip('[')
            lhs = lhs.rstrip(']')
            #lhs = {feature[1:]:feature[0] for feature in lhs.split(',')}
            lhs = lhs.split(',')
            self.lhs = corpus.features_to_segments(lhs)
        #else it's a segment, just leave it as the string it already is
        else:
            self.lhs_string = lhs
            self.lhs = [lhs]

        if not rhs:
            self.rhs_string  = ''
            self.rhs = list()
        elif rhs.startswith('['):
            self.rhs_string = rhs
            rhs = rhs.lstrip('[')
            rhs = rhs.rstrip(']')
            #rhs = {feature[1:]:feature[0] for feature in rhs.split(',')}
            rhs = rhs.split(',')
            self.rhs = corpus.features_to_segments(rhs)
        #else it's a segment, just leave it as the string it already is
        else:
            self.rhs_string = rhs
            self.rhs = [rhs]

    def __str__(self):
        return '_'.join([self.lhs_string,self.rhs_string])

    def __eq__(self, other):
        if not hasattr(other,'lhs'):
            return False
        if not hasattr(other,'rhs'):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def __hash__(self):
        return hash((self.rhs_string, self.lhs_string))

    def __contains__(self, item):
        if not isinstance(item, Environment):
            return False
        if self.rhs:
            if item.rhs not in self.rhs:
                return False
        if self.lhs:
            if item.lhs not in self.lhs:
                return False
        return True


class Corpus(object):
    """
    Attributes
    ----------

    name : str
        Name of the corpus, used only for easy of reference

    wordlist : dict
        Dictionary where every key is a unique string representing a word in a
        corpus, and each entry is a Word object

    specifier : FeatureSpecifier
        See the FeatureSpecifier object

    inventory : list
        list of all Segments that appear at least once in self.wordlist.values()

    orthography : list
        list of one-character strings that appear in self.wordlist.keys()

    custom : bool
        True if this is a user-supplied corpus, False if it is a built-in corpus

    feature_system : str
        Name of the feature system used for the corpus
    """

    #__slots__ = ['name', 'wordlist', 'specifier',
    #            'inventory', 'orthography', 'custom', 'feature_system',
    #            'has_frequency_value','has_spelling_value','has_transcription_value']

    def __init__(self, name):
        self.name = name
        self.wordlist = dict()
        self.specifier = None
        self._inventory = {'#' : Segment('#')} #set of Segments, if transcription exists
        self.orthography = {'#'} #set of orthographic characters
        self.custom = False
        self.has_frequency = True
        self.has_spelling = False
        self.has_transcription = False
        self._tiers = []

    def __eq__(self, other):
        if not isinstance(other,Corpus):
            return False
        if self.wordlist != other.wordlist:
            return False
        return True

    @property
    def tiers(self):
        return self._tiers

    @property
    def attributes(self):
        att = list()
        if self.has_spelling:
            att.append('spelling')
        if self.has_transcription:
            att.append('transcription')
        att.append('frequency')
        att += self.tiers
        return att

    @property
    def words(self):
        return sorted(list(self.wordlist.keys()))

    def features_to_segments(self, feature_description):
        segments = list()
        for k,v in self._inventory.items():
            if v.feature_match(feature_description):
                segments.append(k)
        return segments

    def add_tier(self, tier_name, tier_features):
        if tier_name not in self._tiers:
            self._tiers.append(tier_name)
        tier_segs = self.features_to_segments(tier_features)
        for word in self:
            word.add_tier(tier_name,tier_segs)

    def remove_tier(self, tier_name):
        for i in range(len(self._tiers)):
            if self._tiers[i] == tier_name:
                del self._tiers[i]
                break
        for word in self:
            word.remove_tier(tier_name)

    def __setstate__(self,state):
        try:
            if '_inventory' not in state:
                state['_inventory'] = state['inventory']
            if 'has_spelling' not in state:
                state['has_spelling'] = state['has_spelling_value']
            if 'has_transcription' not in state:
                state['has_transcription'] = state['has_transcription_value']
            self.__dict__.update(state)
            self._specify_features()

            #Backwards compatability
            word = self.random_word()
            if '_tiers' not in state:
                self._tiers = word.tiers
            if not isinstance(word.transcription, Transcription):
                for w in self:
                    w.transcription = Transcription(w.transcription)
                    for t in w.tiers:
                        setattr(w,t,Transcription(getattr(w,t)))
        except Exception as e:
            raise(CorpusIntegrityError("An error occurred while loading the corpus: {}.\nPlease redownload or recreate the corpus.".format(str(e))))


    def _specify_features(self):
        if self.specifier is not None:
            for k in self._inventory.keys():
                try:
                    self._inventory[k].specify(self.specifier[k])
                except KeyError:
                    pass

    def check_coverage(self):
        if not self.specifier is not None:
            return []
        return [x for x in self._inventory.keys() if x not in self.specifier]

    def iter_sort(self):
        """Sorts the keys in the corpus dictionary, then yields the values in that order

        """
        sorted_list = sorted(self.wordlist.keys())
        for word in sorted_list:
            yield self.wordlist[word]

    def set_feature_matrix(self,matrix):
        """
        Set the feature system to be used by the corpus and make sure
        every word is using it too.

        Attributes
        ----------
        matrix : FeatureMatrix
            New feature system to use in the corpus
        """
        self.specifier = matrix
        self._specify_features()

    @property
    def inventory(self):
        """
        Returns a sorted list of segments used in transcriptions

        Returns
        -------
        list
            Sorted list of segment symbols used in transcriptions in the corpus
        """
        return sorted(list(self._inventory.values()))

    def get_random_subset(self, size, new_corpus_name='randomly_generated'):
        """Get a new corpus consisting a random selection from the current corpus

        Parameters
        ----------
        size : int
            Size of new corpus

        new_corpus_name : str

        Returns
        ----------
        new_corpus : Corpus
            New corpus object with len(new_corpus) == size
        """
        new_corpus = Corpus(new_corpus_name)
        while len(new_corpus) < size:
            word = self.random_word()
            new_corpus.add_word(word, allow_duplicates=False)
        new_corpus.specifier = self.specifier
        return new_corpus

    def add_word(self, word, allow_duplicates=True):
        """Add a word to the Corpus.
        If allow_duplicates is True, then words with identical spelling can
        be added. They are kept sepearate by adding a "silent" number to them
        which is never displayed to the user. If allow_duplicates is False,
        then duplicates are simply ignored.

        Parameters
        ----------
        word : Word
            Word object to be added

        allow_duplicates : bool

        """
        word._corpus = self
        #If the word doesn't exist, add it
        try:
            check = self.find(word.spelling, keyerror=True)
            if allow_duplicates:
                #Some words have more than one entry in a corpus, e.g. "live" and "live"
                #so they need to be assigned unique keys

                n = 0
                while True:
                    n += 1
                    #key = '{} ({})'.format(word.spelling.lower(),n)
                    key = '{} ({})'.format(word.spelling,n)
                    try:
                        check = self.find(key, keyerror=True)
                    except KeyError:
                    #if isinstance(check, EmptyWord):
                        self.wordlist[key] = word
                        break
        except KeyError:
            self.wordlist[word.spelling] = word
            if word.spelling is not None:
                self.orthography.update(word.spelling)
                if not self.has_spelling:
                    self.has_spelling = True

        if word.transcription is not None:
            for s in word.transcription:
                if s not in self._inventory:
                    self._inventory[s] = Segment(s)
            if not self.has_transcription:
                self.has_transcription = True

    def random_word(self):
        """Return a randomly selected Word

        """
        word = random.choice(list(self.wordlist.keys()))
        return self.wordlist[word]

    def get_features(self):
        """Get a list of the features used to describe Segments

        Returns
        ----------
        list of str

        """
        return self.specifier.features

    def find(self, word, keyerror=True):
        """Search for a Word in the corpus
        If keyerror == True, then raise a KeyError if the word is not found
        If keyerror == False, then return an EmptyWord if the word is not found

        Parameters
        ----------
        word : str
            String representing the spelling of the word (not transcription)

        keyerror : bool
            Set whether a KeyError should be raised if a word is not found

        Returns
        ----------
        result : Word or EmptyWord


        Raises
        ----------
        KeyError if keyerror == True and word is not found

        """
        try:
            result = self.wordlist[word]
        except KeyError:
            try:
                key = '{} (1)'.format(word)
                result = [self.wordlist[key]]
            except KeyError:
                if keyerror:
                    raise KeyError('The word \"{}\" is not in the corpus'.format(word))
                else:
                    result = EmptyWord(word, 'Word could not be found in the corpus')

        return result

    def __contains__(self,item):
        return self.wordlist.__contains__(item)

    def __len__(self):
        return len(self.wordlist)

    def __setitem__(self,item,value):
        self.wordlist[item] = value

    def __getitem__(self,item):
        return self.wordlist[item]

    def __iter__(self):
        return iter(self.wordlist.values())
